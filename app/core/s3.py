import asyncio
import tempfile
from fastapi import UploadFile
from app.core.aws import s3, bucket


def _upload_fileobj_sync(
    file_obj,
    bucket: str,
    key: str,
    content_type: str | None = None,
):
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    s3.upload_fileobj(
        file_obj,
        bucket,
        key,
        ExtraArgs=extra_args,
    )


async def upload_file_to_s3(
    file: UploadFile,
    s3_key: str,
):
    """
    Async wrapper around boto3 upload_fileobj
    """
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        _upload_fileobj_sync,
        file.file,
        bucket,
        s3_key,
        file.content_type,
    )


def upload_bytesio_to_s3(
    file_obj,
    s3_key: str,
    content_type: str = "application/pdf",
):
    """
    Uploads an in-memory file (BytesIO) to S3
    """
    s3.upload_fileobj(
        file_obj,
        bucket,
        s3_key,
        ExtraArgs={"ContentType": content_type},
    )


def _download_fileobj_sync(
    bucket: str,
    key: str,
    local_path: str,
):
    with open(local_path, "wb") as f:
        s3.download_fileobj(bucket, key, f)


async def download_file_from_s3(s3_key: str):
    loop = asyncio.get_running_loop()

    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_path = tmp_file.name
    tmp_file.close()

    await loop.run_in_executor(
        None,
        _download_fileobj_sync,
        bucket,
        s3_key,
        tmp_path,
    )

    return tmp_path
