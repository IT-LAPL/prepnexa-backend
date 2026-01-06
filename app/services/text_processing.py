from app.models.file import File
from app.repositories.processed_text_repo import ProcessedTextRepository


class TextProcessingService:
    def __init__(self, repo: ProcessedTextRepository):
        self.repo = repo

    async def clean_text(self, file: File, raw_text: str):
        """Normalize raw OCR text and persist ProcessedText via repository."""
        cleaned = raw_text.replace("\n\n", "\n").strip()
        processed = await self.repo.create(
            file_id=file.id, cleaned_text=cleaned, confidence=0.9
        )
        return processed
