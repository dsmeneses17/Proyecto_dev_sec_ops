import os


def _parse_csv_env(name: str, default: str) -> tuple[str, ...]:
    raw_value = os.getenv(name, default)
    return tuple(item.strip() for item in raw_value.split(",") if item.strip())


class Settings:
    DB_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/mydb")
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_super_secreta")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    BACKEND_URL: str = "http://backend_api:5000/api/v1/"

    ERROR_NOHAYRESTAURANTE :str = "No se encontró restaurante para este usuario"

    #roles
    ROL_ADMIN:str="admin"

    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_ENDPOINT_URL: str | None = os.getenv("S3_ENDPOINT_URL")
    S3_PUBLIC_BASE_URL: str | None = os.getenv("S3_PUBLIC_BASE_URL")
    S3_FORCE_PATH_STYLE: bool = os.getenv("S3_FORCE_PATH_STYLE", "false").lower() == "true"
    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")

    IMAGE_WORKERS: int = int(os.getenv("IMAGE_WORKERS", "2"))
    IMAGE_QUEUE_MAXSIZE: int = int(os.getenv("IMAGE_QUEUE_MAXSIZE", "100"))
    IMAGE_QUEUE_PUT_TIMEOUT_SEC: float = float(os.getenv("IMAGE_QUEUE_PUT_TIMEOUT_SEC", "2.0"))
    IMAGE_SHUTDOWN_TIMEOUT_SEC: float = float(os.getenv("IMAGE_SHUTDOWN_TIMEOUT_SEC", "30"))
    IMAGE_MAX_FILE_MB: int = int(os.getenv("IMAGE_MAX_FILE_MB", "5"))
    IMAGE_MAX_FILE_BYTES: int = IMAGE_MAX_FILE_MB * 1024 * 1024
    IMAGE_ALLOWED_CONTENT_TYPES: tuple[str, ...] = _parse_csv_env(
        "IMAGE_ALLOWED_CONTENT_TYPES",
        "image/jpeg,image/png,image/webp",
    )
    IMAGE_ALLOWED_TARGETS: tuple[str, ...] = _parse_csv_env(
        "IMAGE_ALLOWED_TARGETS",
        "logo,dish,general",
    )
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "lax")
    ENFORCE_HTTPS_REDIRECT: bool = os.getenv("ENFORCE_HTTPS_REDIRECT", "true").lower() == "true"


settings = Settings()
