from datetime import datetime, timezone
import enum
import uuid

from sqlalchemy import DateTime, String, Integer, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FileType(str, enum.Enum):
    pdf = "pdf"
    image = "image"


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    upload_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("uploads.id"))
    file_type: Mapped[FileType] = mapped_column(Enum(FileType))
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)

    page_count: Mapped[int | None] = mapped_column(Integer)
    extracted_text: Mapped[str | None] = mapped_column(Text)

    upload = relationship("Upload", back_populates="files")
    processed_text = relationship("ProcessedText", back_populates="file", uselist=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
