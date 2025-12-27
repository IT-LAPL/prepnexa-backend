import uuid
from sqlalchemy import Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    processed_text_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("processed_texts.id")
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id"))
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))

    year: Mapped[int]
    question_number: Mapped[int | None]
    question_text: Mapped[str] = mapped_column(Text)
    marks: Mapped[int | None]

    processed_text = relationship("ProcessedText", back_populates="questions")
    question_topics = relationship(
        "QuestionTopic",
        back_populates="question",
        cascade="all, delete-orphan",
    )
