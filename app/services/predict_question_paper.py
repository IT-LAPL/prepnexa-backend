import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import upload_bytesio_to_s3
from app.models.predicted_paper import PredictedPaper
from app.prompts.question_paper_prompt import QUESTION_PAPER_PROMPT
from app.services.llm_client import call_llm
from app.services.pdf_generator import generate_question_paper_pdf

logger = logging.getLogger(__name__)


async def predict_question_paper(
    db: AsyncSession,
    upload_id,
    exam_id,
    context_text: str,
):
    logger.info(f"🧠 Starting prediction for upload_id={upload_id}")

    if not context_text.strip():
        raise ValueError("Empty context text for prediction")

    context = context_text[:12000]  # LLM safety
    prompt = QUESTION_PAPER_PROMPT.format(context=context)

    logger.info("📤 Sending prompt to LLM")
    predicted_text = await call_llm(prompt)

    # 1️⃣ Save predicted text
    predicted_paper = PredictedPaper(
        upload_id=upload_id,
        exam_id=exam_id,
        predicted_text=predicted_text,
    )
    db.add(predicted_paper)
    await db.flush()

    # 2️⃣ Generate PDF (BytesIO)
    logger.info("📝 Generating PDF")
    pdf_buffer = generate_question_paper_pdf(predicted_text)

    # 3️⃣ Upload PDF to S3
    s3_key = f"predicted/{upload_id}/{uuid.uuid4()}.pdf"

    logger.info(f"☁️ Uploading PDF to S3 → {s3_key}")
    upload_bytesio_to_s3(
        file_obj=pdf_buffer,
        s3_key=s3_key,
        content_type="application/pdf",
    )

    # 4️⃣ Save S3 key
    predicted_paper.pdf_s3_key = s3_key
    await db.commit()

    logger.info(f"✅ Prediction + PDF saved (s3_key={s3_key})")

    return predicted_paper
