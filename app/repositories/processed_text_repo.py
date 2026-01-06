from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processed_text import ProcessedText


class ProcessedTextRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, file_id: str, cleaned_text: str, confidence: float | None
    ) -> ProcessedText:
        processed = ProcessedText(
            file_id=file_id,
            cleaned_text=cleaned_text,
            confidence=confidence,
        )
        self.db.add(processed)
        await self.db.flush()
        return processed

    async def get(self, processed_text_id: str) -> Optional[ProcessedText]:
        return await self.db.get(ProcessedText, processed_text_id)
