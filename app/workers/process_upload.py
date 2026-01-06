import logging

from app.core.database import AsyncSessionLocal
from app.services.worker_service import WorkerService


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def process_upload_worker(upload_id: str) -> None:
    logger.info(f"🚀 BG worker started for upload_id={upload_id}")
    async with AsyncSessionLocal() as db:
        service = WorkerService(db)
        await service.process_upload(upload_id)
