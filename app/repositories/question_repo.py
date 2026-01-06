from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.models.question_topic import QuestionTopic


class QuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_question(
        self,
        processed_text_id: str,
        exam_id: str,
        subject_id: str,
        year: int,
        question_number: int | None,
        question_text: str,
    ) -> Question:
        question = Question(
            processed_text_id=processed_text_id,
            exam_id=exam_id,
            subject_id=subject_id,
            year=year,
            question_number=question_number,
            question_text=question_text,
        )
        self.db.add(question)
        await self.db.flush()
        return question

    async def add_question_topic(
        self, question_id: str, topic_id: str, confidence: float | None
    ):
        q_topic = QuestionTopic(
            question_id=question_id,
            topic_id=topic_id,
            confidence=confidence,
        )
        self.db.add(q_topic)
        return q_topic
