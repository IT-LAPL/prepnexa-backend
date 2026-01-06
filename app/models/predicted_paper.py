import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PredictedPaper(Base):
    __tablename__ = "predicted_papers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False
    )

    predicted_text: Mapped[str] = mapped_column(Text, nullable=False)

    pdf_s3_key: Mapped[str | None] = mapped_column(String, nullable=True)

    # # relationship for flashcards created from this predicted paper
    # flashcards = relationship(
    #     "Flashcard",
    #     back_populates="predicted_paper",
    #     cascade="all, delete-orphan",
    # )
