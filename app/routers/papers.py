from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.services.paper_prediction_service import PredictedPaperService
from app.dependencies.services import get_predicted_paper_service
from app.models.user import User

router = APIRouter(prefix="/predicted-papers", tags=["predicted-papers"])


@router.get("/")
async def list_predicted_papers(
    current_user: User = Depends(get_current_user),
    service: PredictedPaperService = Depends(get_predicted_paper_service),
):
    return await service.list_for_user(user_id=current_user.id)


@router.get("/{paper_id}")
async def predicted_paper_detail(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    service: PredictedPaperService = Depends(get_predicted_paper_service),
):
    detail = await service.get_detail(paper_id=paper_id, user_id=current_user.id)
    if not detail:
        raise HTTPException(status_code=404, detail="Prediction not found or forbidden")
    return detail
