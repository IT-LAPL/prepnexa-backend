from app.models.processed_text import ProcessedText
from app.models.file import File
from sqlalchemy.ext.asyncio import AsyncSession


async def clean_text(db: AsyncSession, file: File, raw_text: str) -> ProcessedText:
    cleaned = raw_text.replace("\n\n", "\n").strip()

    processed = ProcessedText(
        file_id=file.id,
        cleaned_text=cleaned,
        confidence=0.9,  # placeholder
    )

    db.add(processed)
    await db.flush()

    return processed
