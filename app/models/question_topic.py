from sqlalchemy import ForeignKey, Float, UniqueConstraint
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
import uuid

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.exam import Topic


class QuestionTopic(Base):
    __tablename__ = "question_topics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"))
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"))
    confidence: Mapped[float | None] = mapped_column(Float)
    # Use fully-qualified relationship strings to avoid registry ordering issues
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="question_topics",
    )

    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="question_topics",
    )

    __table_args__ = (
        # ensure a question-topic pair is unique
        # (keeps semantics from earlier implementation)
        UniqueConstraint("question_id", "topic_id", name="uq_question_topic"),
    )
