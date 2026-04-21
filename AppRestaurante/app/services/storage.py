from functools import lru_cache
import logging
from urllib.parse import quote, urlparse

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from google.cloud import storage

from app.core.config import settings


logger = logging.getLogger(__name__)


class StorageConfigurationError(RuntimeError):
    pass


def _provider() -> str:
    return (settings.STORAGE_PROVIDER or "s3").strip().lower()


def _assert_storage_configured():
    provider = _provider()
    if provider == "gcs":
        if not settings.GCS_BUCKET_NAME:
            raise StorageConfigurationError("GCS_BUCKET_NAME no esta configurado")
        return

    if provider == "s3":
        if not settings.S3_BUCKET_NAME:
            raise StorageConfigurationError("S3_BUCKET_NAME no esta configurado")
        return

    raise StorageConfigurationError(f"Storage provider no soportado: {provider}")


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


@lru_cache(maxsize=1)
def get_gcs_client():
    _assert_storage_configured()

    if settings.GCP_PROJECT_ID:
        return storage.Client(project=settings.GCP_PROJECT_ID)
    return storage.Client()


def _extract_object_name_from_url(image_url: str) -> str | None:
    if not image_url:
        return None

    provider = _provider()

    if provider == "gcs":
        if image_url.startswith("gs://"):
            prefix = f"gs://{settings.GCS_BUCKET_NAME}/"
            if settings.GCS_BUCKET_NAME and image_url.startswith(prefix):
                return image_url.replace(prefix, "", 1)
            return None

        if settings.GCS_PUBLIC_BASE_URL and image_url.startswith(settings.GCS_PUBLIC_BASE_URL.rstrip("/") + "/"):
            return image_url.replace(settings.GCS_PUBLIC_BASE_URL.rstrip("/") + "/", "", 1)

        parsed = urlparse(image_url)
        host = (parsed.netloc or "").lower()
        path = (parsed.path or "").lstrip("/")

        if not host or not path:
            return None

        expected_bucket = (settings.GCS_BUCKET_NAME or "").lower()

        if host == "storage.googleapis.com" and path.startswith(f"{settings.GCS_BUCKET_NAME}/"):
            return path[len(settings.GCS_BUCKET_NAME) + 1:]

        if expected_bucket and host == f"{expected_bucket}.storage.googleapis.com":
            return path

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


def resolve_object_name(image_ref: str) -> str | None:
    if not image_ref:
        return None

    if image_ref.startswith(("http://", "https://", "gs://", "s3://")):
        return _extract_object_name_from_url(image_ref)

    if image_ref.startswith("/media/"):
        return image_ref[len("/media/"):]

    return image_ref.strip().lstrip("/")


def build_proxy_url(object_name: str) -> str:
    safe_name = quote(object_name, safe="/")
    return f"/media/{safe_name}"


def build_display_url(image_ref: str, expires_in_seconds: int = 3600) -> str:
    del expires_in_seconds
    object_name = resolve_object_name(image_ref)
    if not object_name:
        return image_ref
    return build_proxy_url(object_name)


def read_object_from_storage(image_ref: str) -> tuple[bytes, str, str | None]:
    _assert_storage_configured()
    object_name = resolve_object_name(image_ref)
    if not object_name:
        raise FileNotFoundError("Object name no valido")

    provider = _provider()

    if provider == "gcs":
        gcs = get_gcs_client()
        blob = gcs.bucket(settings.GCS_BUCKET_NAME).blob(object_name)
        if not blob.exists():
            raise FileNotFoundError(f"Objeto no encontrado: {object_name}")
        blob.reload()
        content = blob.download_as_bytes()
        return content, (blob.content_type or "application/octet-stream"), blob.cache_control

    s3 = get_s3_client()
    response = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=object_name)
    body = response["Body"].read()
    return body, (response.get("ContentType") or "application/octet-stream"), response.get("CacheControl")


def upload_bytes_to_object_storage(content: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
    _assert_storage_configured()
    provider = _provider()

    if provider == "gcs":
        logger.info(
            "Uploading to GCS provider=%s bucket=%s project=%s object=%s content_type=%s size=%s",
            provider,
            settings.GCS_BUCKET_NAME,
            settings.GCP_PROJECT_ID,
            object_name,
            content_type,
            len(content),
        )
        try:
            gcs = get_gcs_client()
            bucket = gcs.bucket(settings.GCS_BUCKET_NAME)
            blob = bucket.blob(object_name)
            blob.cache_control = "public, max-age=31536000"
            blob.upload_from_string(content, content_type=content_type)
        except Exception as exc:
            logger.exception(
                "GCS upload failed: bucket=%s object=%s size=%s content_type=%s exception_type=%s",
                settings.GCS_BUCKET_NAME,
                object_name,
                len(content),
                content_type,
                type(exc).__name__,
            )
            raise RuntimeError(f"Error subiendo archivo a GCS: {exc}") from exc

        return object_name

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
        logger.exception(
            "S3 upload failed bucket=%s object=%s content_type=%s",
            settings.S3_BUCKET_NAME,
            object_name,
            content_type,
        )
        raise RuntimeError(f"Error subiendo archivo a Object Storage: {exc}") from exc

    return object_name
