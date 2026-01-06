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
from app.models.file import File as FileModel
from app.models.user import User
from app.workers.dispatcher import enqueue_process_upload
from app.services.upload_service import UploadService
from app.dependencies.services import get_upload_service

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
    upload_service: UploadService = Depends(get_upload_service),
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded",
        )

    # ✅ Validate all files FIRST
    for file in files:
        detect_file_type(file)

    # Build file metadata and upload to S3
    file_meta = []
    for file in files:
        file_type = detect_file_type(file)
        # generate s3 key placeholder; upload happens here
        s3_key = f"uploads/{{uuid4()}}_{file.filename}"
        await upload_file_to_s3(file, s3_key)
        file_meta.append((file.filename, file_type, s3_key))

    result = await upload_service.create_upload(
        user_id=current_user.id, exam_id=exam_id, year=year, files=file_meta
    )

    # enqueue processing via Celery (with retries)
    enqueue_process_upload(result["upload"].id)

    return {
        "upload_id": result["upload"].id,
        "files_uploaded": len(result["files"]),
        "status": result["upload"].status,
    }
