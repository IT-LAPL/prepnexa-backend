import uuid
import logging
from typing import List

from app.repositories.predicted_paper_repo import PredictedPaperRepository
from app.core.s3 import upload_bytesio_to_s3
from app.prompts.question_paper_prompt import QUESTION_PAPER_PROMPT
from app.services.llm_client import call_llm
from app.services.pdf_generator import generate_question_paper_pdf

logger = logging.getLogger(__name__)
from app.models.upload import Upload


class PredictedPaperService:
    def __init__(self, repo: PredictedPaperRepository):
        self.repo = repo

    async def list_for_user(self, user_id) -> List[dict]:
        rows = await self.repo.list_for_user(user_id)
        return [
            {
                "id": paper.id,
                "exam_id": paper.exam_id,
                "year": upload.year,
                "has_pdf": paper.pdf_s3_key is not None,
            }
            for paper, upload in rows
        ]

    async def get_detail(self, paper_id: str, user_id: str) -> dict:
        paper = await self.repo.get(paper_id)
        if not paper:
            return None

        # ensure ownership
        upload = await self.repo.db.get(Upload, paper.upload_id)
        if not upload or upload.user_id != user_id:
            return None

        files = await self.repo.list_files_for_upload(upload.id)

        return {
            "id": paper.id,
            "predicted_text": paper.predicted_text,
            "pdf_s3_key": paper.pdf_s3_key,
            "exam_id": paper.exam_id,
            "year": upload.year,
            "source_files": [
                {
                    "id": f.id,
                    "filename": f.original_filename,
                    "file_type": f.file_type,
                    "s3_key": f.s3_key,
                    "page_count": f.page_count,
                }
                for f in files
            ],
        }

    async def predict_and_store(self, upload_id: str, exam_id: str, context_text: str):
        """
        Run LLM prediction, save PredictedPaper, generate PDF and upload to S3.
        """
        logger.info(f"🧠 Starting prediction for upload_id={upload_id}")

        if not context_text.strip():
            raise ValueError("Empty context text for prediction")

        context = context_text[:12000]
        prompt = QUESTION_PAPER_PROMPT.format(context=context)

        logger.info("📤 Sending prompt to LLM")
        predicted_text = await call_llm(prompt)

        # save predicted paper
        from app.models.predicted_paper import PredictedPaper

        predicted_paper = PredictedPaper(
            upload_id=upload_id,
            exam_id=exam_id,
            predicted_text=predicted_text,
        )
        self.repo.db.add(predicted_paper)
        await self.repo.db.flush()

        # generate PDF and upload
        logger.info("📝 Generating PDF")
        pdf_buffer = generate_question_paper_pdf(predicted_text)

        s3_key = f"predicted/{upload_id}/{uuid.uuid4()}.pdf"
        logger.info(f"☁️ Uploading PDF to S3 → {s3_key}")
        upload_bytesio_to_s3(
            file_obj=pdf_buffer, s3_key=s3_key, content_type="application/pdf"
        )

        predicted_paper.pdf_s3_key = s3_key
        await self.repo.db.commit()

        logger.info(f"✅ Prediction + PDF saved (s3_key={s3_key})")

        return predicted_paper
