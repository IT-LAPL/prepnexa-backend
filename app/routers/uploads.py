from uuid import uuid4
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.s3 import upload_file_to_s3
from app.dependencies.auth import get_current_user
from app.models.file import FileType
from app.models.upload import Upload, UploadStatus
from app.models.file import File as FileModel
from app.models.user import User
from app.workers.process_upload import process_upload_worker

router = APIRouter(prefix="/uploads", tags=["uploads"])

# ✅ Allowed extensions (RELIABLE across mobile/web)
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def detect_file_type(file: UploadFile) -> FileType:
    """
    Detect file type using filename extension.
    Mobile clients often send content-type as application/octet-stream.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename",
        )

    ext = Path(file.filename).suffix.lower()

    if ext == ".pdf":
        return FileType.pdf
    if ext in {".png", ".jpg", ".jpeg"}:
        return FileType.image

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported file extension: {ext}",
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_upload(
    background_tasks: BackgroundTasks,
    exam_id: str = Form(...),
    year: int = Form(...),
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded",
        )

    # ✅ Validate all files FIRST
    for file in files:
        detect_file_type(file)

    # Create upload record
    upload = Upload(
        exam_id=exam_id,
        user_id=current_user.id,
        year=year,
        status=UploadStatus.pending,
    )

    db.add(upload)
    await db.flush()  # get upload.id

    file_records: list[FileModel] = []

    for file in files:
        file_type = detect_file_type(file)

        s3_key = f"uploads/{upload.id}/{uuid4()}_{file.filename}"

        file_record = FileModel(
            id=str(uuid4()),
            upload_id=upload.id,
            file_type=file_type,
            s3_key=s3_key,
            original_filename=file.filename,
        )

        db.add(file_record)
        file_records.append(file_record)

        # 🔥 Upload to S3 (async)
        await upload_file_to_s3(file, s3_key)

    # Mark upload as processing
    upload.status = UploadStatus.processing

    await db.commit()

    # Background processing
    background_tasks.add_task(process_upload_worker, upload.id)

    return {
        "upload_id": upload.id,
        "files_uploaded": len(file_records),
        "status": upload.status,
    }
