import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.upload import Upload, UploadStatus
from app.models.file import File
from app.models.processed_text import ProcessedText
from app.services.ocr_service import run_ocr
from app.repositories.processed_text_repo import ProcessedTextRepository
from app.services.text_processing import TextProcessingService
from app.repositories.question_repo import QuestionRepository
from app.repositories.topic_repo import TopicRepository
from app.services.question_extractor import QuestionExtractorService
from app.repositories.predicted_paper_repo import PredictedPaperRepository
from app.services.paper_prediction_service import PredictedPaperService

logger = logging.getLogger(__name__)


class WorkerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_upload(self, upload_id: str) -> None:
        logger.info(f"🚀 WorkerService started for upload_id={upload_id}")

        upload: Optional[Upload] = await self.db.get(Upload, upload_id)
        if not upload:
            logger.warning(f"❌ Upload not found: {upload_id}")
            return

        try:
            upload.status = UploadStatus.processing
            await self.db.commit()

            # Load files
            stmt = select(File).where(File.upload_id == upload_id)
            result = await self.db.execute(stmt)
            files = result.scalars().all()
            if not files:
                logger.warning(f"❌ No files found for upload {upload_id}")
                upload.status = UploadStatus.failed
                await self.db.commit()
                return

            # Process each file
            for idx, file in enumerate(files, start=1):
                logger.info(
                    f"🔍 Processing file {idx}/{len(files)}: {file.original_filename}"
                )

                logger.info(f"📷 Running OCR on file: {file.original_filename}")
                raw_text = await run_ocr(file)
                logger.info(f"✅ OCR complete for file: {file.original_filename}")

                logger.info(f"🧹 Cleaning text for file: {file.original_filename}")
                processed_repo = ProcessedTextRepository(self.db)
                text_processing_service = TextProcessingService(processed_repo)
                processed_text = await text_processing_service.clean_text(
                    file=file, raw_text=raw_text
                )
                logger.info(f"✅ Text cleaned for file: {file.original_filename}")
                logger.info(
                    f"❓ Extracting questions for file: {file.original_filename}"
                )
                question_repo = QuestionRepository(self.db)
                topic_repo = TopicRepository(self.db)
                extractor = QuestionExtractorService(question_repo, topic_repo)
                await extractor.extract_questions(
                    upload=upload, processed_text=processed_text
                )
                logger.info(
                    f"✅ Questions extracted for file: {file.original_filename}"
                )

            logger.info("📚 Loading processed text for prediction")

            stmt = select(ProcessedText).join(File).where(File.upload_id == upload_id)
            result = await self.db.execute(stmt)
            processed_texts = result.scalars().all()

            if not processed_texts:
                raise RuntimeError("No processed text found for prediction")

            combined_text = "\n\n".join(
                pt.cleaned_text for pt in processed_texts if pt.cleaned_text
            )

            logger.info(
                f"🧠 Running question paper prediction (chars={len(combined_text)})"
            )

            # use repository + service for prediction and persistence
            predicted_repo = PredictedPaperRepository(self.db)
            predicted_service = PredictedPaperService(predicted_repo)
            predicted_paper = await predicted_service.predict_and_store(
                upload_id=upload.id, exam_id=upload.exam_id, context_text=combined_text
            )

            # generate flashcards for the predicted paper
            from app.repositories.flashcard_repo import FlashcardRepository
            from app.services.flashcard_service import FlashcardService

            flashcard_repo = FlashcardRepository(self.db)
            flashcard_service = FlashcardService(flashcard_repo)
            try:
                await flashcard_service.generate_flashcards(
                    user_id=str(upload.user_id),
                    predicted_paper_id=str(predicted_paper.id),
                    text=predicted_paper.predicted_text,
                    max_cards=20,
                )
            except Exception:
                logger.exception(
                    "Failed to generate flashcards for predicted_paper=%s",
                    predicted_paper.id,
                )

            upload.status = UploadStatus.completed
            await self.db.commit()
            logger.info(f"🎉 Upload {upload_id} processing completed")

        except Exception:
            logger.exception(f"🔥 WorkerService failed for upload {upload_id}")
            upload.status = UploadStatus.failed
            await self.db.commit()
            raise
