from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.predicted_paper import PredictedPaper
from app.models.upload import Upload
from app.models.file import File as FileModel


class PredictedPaperRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user(self, user_id) -> List[Tuple[PredictedPaper, Upload]]:
        stmt = (
            select(PredictedPaper, Upload)
            .join(Upload, Upload.id == PredictedPaper.upload_id)
            .where(Upload.user_id == user_id)
            .order_by(PredictedPaper.id.desc())
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get(self, paper_id: UUID) -> Optional[PredictedPaper]:
        return await self.db.get(PredictedPaper, paper_id)

    async def list_files_for_upload(self, upload_id) -> List[FileModel]:
        stmt = select(FileModel).where(FileModel.upload_id == upload_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
