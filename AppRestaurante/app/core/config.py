import os

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


settings = Settings() 
