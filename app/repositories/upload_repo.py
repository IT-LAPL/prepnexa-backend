from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.upload import Upload
from app.models.file import File as FileModel


class UploadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_upload(self, upload: Upload) -> Upload:
        self.db.add(upload)
        await self.db.flush()
        return upload

    async def add_file(self, file: FileModel) -> FileModel:
        self.db.add(file)
        return file

    async def commit(self) -> None:
        await self.db.commit()

    async def get_upload(self, upload_id: UUID) -> Optional[Upload]:
        return await self.db.get(Upload, upload_id)

    async def list_files_for_upload(self, upload_id: UUID) -> List[FileModel]:
        stmt = select(FileModel).where(FileModel.upload_id == upload_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
