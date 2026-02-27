from functools import lru_cache

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


class StorageConfigurationError(RuntimeError):
    pass


def _assert_storage_configured():
    if not settings.S3_BUCKET_NAME:
        raise StorageConfigurationError("S3_BUCKET_NAME no está configurado")


@lru_cache(maxsize=1)
def get_s3_client():
    _assert_storage_configured()

    client_kwargs = {
        "region_name": settings.S3_REGION,
        "config": Config(s3={"addressing_style": "path" if settings.S3_FORCE_PATH_STYLE else "auto"}),
    }

    if settings.S3_ENDPOINT_URL:
        client_kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

    return boto3.client("s3", **client_kwargs)


def build_public_url(object_name: str) -> str:
    if settings.S3_PUBLIC_BASE_URL:
        return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{object_name}"

    if settings.S3_REGION == "us-east-1":
        return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{object_name}"

    return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.S3_REGION}.amazonaws.com/{object_name}"


def upload_bytes_to_object_storage(content: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
    _assert_storage_configured()
    s3 = get_s3_client()

    try:
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=object_name,
            Body=content,
            ContentType=content_type,
            CacheControl="public, max-age=31536000",
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Error subiendo archivo a Object Storage: {exc}") from exc

    return build_public_url(object_name)
