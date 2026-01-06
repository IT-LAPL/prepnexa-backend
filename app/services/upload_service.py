from typing import List
from uuid import uuid4
from fastapi import HTTPException, status

from app.repositories.upload_repo import UploadRepository
from app.models.upload import Upload, UploadStatus
from app.models.file import File as FileModel, FileType


class UploadService:
    def __init__(self, repo: UploadRepository):
        self.repo = repo

    async def create_upload(self, user_id, exam_id, year, files: List[tuple]) -> dict:
        # files: list of tuples (original_filename, file_type, s3_key)
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No files"
            )

        upload = Upload(
            exam_id=exam_id, user_id=user_id, year=year, status=UploadStatus.pending
        )

        await self.repo.create_upload(upload)

        file_records = []
        for orig_name, file_type, s3_key in files:
            file_record = FileModel(
                id=str(uuid4()),
                upload_id=upload.id,
                file_type=file_type,
                s3_key=s3_key,
                original_filename=orig_name,
            )
            await self.repo.add_file(file_record)
            file_records.append(file_record)

        upload.status = UploadStatus.processing
        await self.repo.commit()

        return {"upload": upload, "files": file_records}

    async def get_upload_files(self, upload_id):
        return await self.repo.list_files_for_upload(upload_id)
