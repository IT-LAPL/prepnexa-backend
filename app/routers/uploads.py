from uuid import uuid4
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

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}


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

    for file in files:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}",
            )

    upload = Upload(
        exam_id=exam_id,
        user_id=current_user.id,
        year=year,
        status=UploadStatus.pending,
    )

    db.add(upload)
    await db.flush()

    file_records = []

    for file in files:
        file_type = (
            FileType.pdf if file.content_type == "application/pdf" else FileType.image
        )

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

        # 🔥 S3 upload happens here (async)
        await upload_file_to_s3(file, s3_key)

    upload.status = UploadStatus.processing

    await db.commit()

    background_tasks.add_task(process_upload_worker, upload.id)

    return {
        "upload_id": upload.id,
        "files_uploaded": len(file_records),
        "status": upload.status,
    }
