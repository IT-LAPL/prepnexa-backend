import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String)

    subjects = relationship("Subject", back_populates="exam")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    exam = relationship("Exam", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    subject = relationship("Subject", back_populates="topics")
    question_topics = relationship(
        "app.models.question_topic.QuestionTopic",
        back_populates="topic",
    )
