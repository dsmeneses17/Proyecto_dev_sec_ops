from functools import lru_cache
from urllib.parse import urlparse

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
        "config": Config(
            signature_version="s3v4",
            s3={
                "addressing_style": "path" if settings.S3_FORCE_PATH_STYLE else "auto",
                "use_global_endpoint": False,
            },
        ),
    }

    if settings.S3_ENDPOINT_URL:
        client_kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
    else:
        client_kwargs["endpoint_url"] = f"https://s3.{settings.S3_REGION}.amazonaws.com"

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


def _extract_object_name_from_url(image_url: str) -> str | None:
    if not image_url:
        return None

    if settings.S3_PUBLIC_BASE_URL and image_url.startswith(settings.S3_PUBLIC_BASE_URL.rstrip("/") + "/"):
        return image_url.replace(settings.S3_PUBLIC_BASE_URL.rstrip("/") + "/", "", 1)

    parsed = urlparse(image_url)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").lstrip("/")

    if not host or not path:
        return None

    expected_bucket = (settings.S3_BUCKET_NAME or "").lower()
    if expected_bucket and host.startswith(f"{expected_bucket}.s3"):
        return path

    if host.startswith("s3.") or host == "s3.amazonaws.com":
        if path.startswith(f"{settings.S3_BUCKET_NAME}/"):
            return path[len(settings.S3_BUCKET_NAME) + 1:]

    return None


def build_display_url(image_url: str, expires_in_seconds: int = 3600) -> str:
    object_name = _extract_object_name_from_url(image_url)
    if not object_name:
        return image_url

    try:
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": object_name},
            ExpiresIn=expires_in_seconds,
        )
    except Exception:
        return image_url


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
