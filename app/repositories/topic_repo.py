from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.exam import Topic


class TopicRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_topics_by_exam(self, exam_id) -> List[Topic]:
        stmt = select(Topic).where(Topic.subject.has(exam_id=exam_id))
        result = await self.db.execute(stmt)
        return result.scalars().all()
