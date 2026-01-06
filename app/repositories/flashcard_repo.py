import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flashcards import Flashcard

logger = logging.getLogger(__name__)


class FlashcardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, flashcard: Flashcard):
        self.db.add(flashcard)
        await self.db.flush()
        return flashcard
