from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.file import File
from app.models.predicted_paper import PredictedPaper
from app.models.upload import Upload
from app.models.user import User

router = APIRouter(prefix="/predicted-papers", tags=["predicted-papers"])


@router.get("/")
async def list_predicted_papers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(PredictedPaper, Upload)
        .join(Upload, Upload.id == PredictedPaper.upload_id)
        .where(Upload.user_id == current_user.id)
        .order_by(PredictedPaper.id.desc())
    )

    result = await db.execute(stmt)

    return [
        {
            "id": paper.id,
            "exam_id": paper.exam_id,
            "year": upload.year,
            "has_pdf": paper.pdf_s3_key is not None,
        }
        for paper, upload in result.all()
    ]


@router.get("/{paper_id}")
async def predicted_paper_detail(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    paper = await db.get(PredictedPaper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Prediction not found")

    upload = await db.get(Upload, paper.upload_id)
    if upload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    files = (
        (await db.execute(select(File).where(File.upload_id == upload.id)))
        .scalars()
        .all()
    )

    return {
        "id": paper.id,
        "predicted_text": paper.predicted_text,
        "pdf_s3_key": paper.pdf_s3_key,
        "exam_id": paper.exam_id,
        "year": upload.year,
        "source_files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "file_type": f.file_type,
                "s3_key": f.s3_key,
                "page_count": f.page_count,
            }
            for f in files
        ],
    }
