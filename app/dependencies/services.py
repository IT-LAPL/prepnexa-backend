from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService
from app.repositories.upload_repo import UploadRepository
from app.services.upload_service import UploadService
from app.repositories.predicted_paper_repo import PredictedPaperRepository
from app.services.paper_prediction_service import PredictedPaperService


async def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)


async def get_user_service(repo: UserRepository = Depends(get_user_repo)):
    return UserService(repo)


async def get_upload_repo(db: AsyncSession = Depends(get_db)):
    return UploadRepository(db)


async def get_upload_service(
    repo: UploadRepository = Depends(get_upload_repo),
):
    return UploadService(repo)


async def get_predicted_paper_repo(db: AsyncSession = Depends(get_db)):
    return PredictedPaperRepository(db)


async def get_predicted_paper_service(
    repo: PredictedPaperRepository = Depends(get_predicted_paper_repo),
):
    return PredictedPaperService(repo)
