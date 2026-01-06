import boto3
from typing import Optional

from app.core.config import settings


def get_s3_client(
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: Optional[str] = None,
):
    """Return a boto3 S3 client. Allows creating a client with alternate credentials for testing."""
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id or settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY,
        region_name=region_name or settings.AWS_REGION,
    )


# default module-level client (convenience)
s3 = get_s3_client()

# default bucket name
bucket = settings.AWS_S3_BUCKET
