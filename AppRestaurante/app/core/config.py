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


settings = Settings() 
