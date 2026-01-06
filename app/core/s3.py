import asyncio
import tempfile
from fastapi import UploadFile
from typing import Optional
import logging

from app.core.aws import get_s3_client, s3 as default_s3, bucket as default_bucket

logger = logging.getLogger(__name__)


def _upload_fileobj_sync(
    file_obj,
    bucket: str,
    key: str,
    content_type: Optional[str] = None,
    s3_client=None,
):
    # Ensure file pointer is at start
    try:
        file_obj.seek(0)
    except Exception:
        pass

    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    client = s3_client or default_s3
    client.upload_fileobj(
        file_obj,
        bucket,
        key,
        ExtraArgs=extra_args,
    )


async def upload_file_to_s3(
    file: UploadFile,
    s3_key: str,
    bucket: Optional[str] = None,
    s3_client=None,
):
    """
    Async wrapper around boto3 upload_fileobj.

    Returns the S3 key on success.
    """
    loop = asyncio.get_running_loop()
    b = bucket or default_bucket
    try:
        await loop.run_in_executor(
            None,
            _upload_fileobj_sync,
            file.file,
            b,
            s3_key,
            file.content_type,
            s3_client,
        )
    except Exception:
        logger.exception("Failed to upload file to S3: %s", s3_key)
        raise

    return s3_key


def upload_bytesio_to_s3(
    file_obj,
    s3_key: str,
    content_type: str = "application/pdf",
    bucket: Optional[str] = None,
    s3_client=None,
):
    """
    Uploads an in-memory file (BytesIO) to S3 and returns the S3 key.
    """
    b = bucket or default_bucket
    try:
        try:
            file_obj.seek(0)
        except Exception:
            pass

        client = s3_client or default_s3
        client.upload_fileobj(
            file_obj,
            b,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )
    except Exception:
        logger.exception("Failed to upload bytes to S3: %s", s3_key)
        raise

    return s3_key


def _download_fileobj_sync(
    bucket: str,
    key: str,
    local_path: str,
    s3_client=None,
):
    client = s3_client or default_s3
    with open(local_path, "wb") as f:
        client.download_fileobj(bucket, key, f)


async def download_file_from_s3(
    s3_key: str, bucket: Optional[str] = None, s3_client=None
):
    loop = asyncio.get_running_loop()

    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_path = tmp_file.name
    tmp_file.close()

    b = bucket or default_bucket

    try:
        await loop.run_in_executor(
            None,
            _download_fileobj_sync,
            b,
            s3_key,
            tmp_path,
            s3_client,
        )
    except Exception:
        logger.exception("Failed to download S3 object %s", s3_key)
        raise

    return tmp_path
