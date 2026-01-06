import time
import logging

from app.workers.tasks import process_upload_task

logger = logging.getLogger(__name__)


def enqueue_process_upload(
    upload_id: str, retries: int = 3, backoff: float = 1.0
) -> None:
    """Attempt to enqueue the Celery task with retry/backoff.

    Raises the final exception if all retries fail.
    """
    attempt = 0
    while True:
        try:
            process_upload_task.delay(str(upload_id))
            return
        except Exception as exc:
            attempt += 1
            logger.exception(
                "Failed to enqueue process_upload task (attempt %d/%d)",
                attempt,
                retries,
            )
            if attempt > retries:
                raise
            time.sleep(backoff * attempt)
