import uuid
from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProcessedText(Base):
    __tablename__ = "processed_texts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("files.id"), unique=True)

    cleaned_text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)

    file = relationship("File", back_populates="processed_text")
    questions = relationship("Question", back_populates="processed_text")
