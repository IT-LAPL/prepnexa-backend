from sqlalchemy import select
import logging

from app.core.database import AsyncSessionLocal
from app.models.upload import Upload, UploadStatus
from app.models.file import File
from app.services.ocr_service import run_ocr
from app.services.text_processing import clean_text
from app.services.question_extractor import extract_questions
from app.services.predict_question_paper import predict_question_paper
from app.models.processed_text import ProcessedText


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Ensure logs are visible


async def process_upload_worker(upload_id: str) -> None:
    logger.info(f"🚀 BG worker started for upload_id={upload_id}")

    async with AsyncSessionLocal() as db:
        upload: Upload | None = None

        try:
            # 1️⃣ Load upload
            upload = await db.get(Upload, upload_id)
            if not upload:
                logger.warning(f"❌ Upload not found: {upload_id}")
                return
            logger.info(f"📂 Loaded upload: {upload_id}")

            upload.status = UploadStatus.processing
            await db.commit()
            logger.info(f"⏳ Upload {upload_id} marked as processing")

            # 2️⃣ Load files
            stmt = select(File).where(File.upload_id == upload_id)
            result = await db.execute(stmt)
            files = result.scalars().all()
            if not files:
                logger.warning(f"❌ No files found for upload {upload_id}")
                upload.status = UploadStatus.failed
                await db.commit()
                return
            logger.info(f"📄 Found {len(files)} file(s) for upload {upload_id}")

            # 3️⃣ Process each file
            for idx, file in enumerate(files, start=1):
                logger.info(
                    f"🔍 Processing file {idx}/{len(files)}: {file.original_filename}"
                )

                # OCR
                logger.info(f"📷 Running OCR on file: {file.original_filename}")
                raw_text = await run_ocr(file)
                logger.info(f"✅ OCR complete for file: {file.original_filename}")

                # Cleaning & normalization
                logger.info(f"🧹 Cleaning text for file: {file.original_filename}")
                processed_text = await clean_text(
                    db=db,
                    file=file,
                    raw_text=raw_text,
                )
                logger.info(f"✅ Text cleaned for file: {file.original_filename}")

                # Question extraction
                logger.info(
                    f"❓ Extracting questions for file: {file.original_filename}"
                )
                await extract_questions(
                    db=db,
                    upload=upload,
                    processed_text=processed_text,
                )
                logger.info(
                    f"✅ Questions extracted for file: {file.original_filename}"
                )

            logger.info("📚 Loading processed text for prediction")

            stmt = select(ProcessedText).join(File).where(File.upload_id == upload_id)
            result = await db.execute(stmt)
            processed_texts = result.scalars().all()

            if not processed_texts:
                raise RuntimeError("No processed text found for prediction")

            combined_text = "\n\n".join(
                pt.cleaned_text for pt in processed_texts if pt.cleaned_text
            )

            logger.info(
                f"🧠 Running question paper prediction " f"(chars={len(combined_text)})"
            )

            # 5️⃣ PREDICT QUESTION PAPER
            await predict_question_paper(
                db=db,
                upload_id=upload.id,
                exam_id=upload.exam_id,
                context_text=combined_text,
            )

            # 4️⃣ Mark upload completed
            upload.status = UploadStatus.completed
            await db.commit()
            logger.info(f"🎉 Upload {upload_id} processing completed")

        except Exception as exc:
            # 5️⃣ Fail-safe handling
            logger.exception(f"🔥 Worker failed for upload {upload_id}")
            if upload:
                upload.status = UploadStatus.failed
                await db.commit()
            raise exc
