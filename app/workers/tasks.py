from app.core.celery_app import celery_app
import asyncio
from app.workers.process_upload import process_upload_worker


@celery_app.task(name="process_upload")
def process_upload_task(upload_id: str):
    """Celery task wrapper that runs the async process_upload_worker."""

    # run the async worker function in a fresh event loop
    asyncio.run(process_upload_worker(upload_id))
