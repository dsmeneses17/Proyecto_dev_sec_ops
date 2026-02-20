# app/core/security.py
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError 
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

# Configuración mínima
SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_role(user: dict):
    return user.get("rol", "cliente")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido desde decode: {e}")




async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        role = payload.get("rol")
        username = payload.get("username")  # si quieres mantenerlo
        email = payload.get("email")        # si quieres mostrarlo
        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError as e:
        print("❌ Error al decodificar token:", e)
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    return {
        "id": user_id,
        "usuario": username,
        "email": email,
        "rol": role
    }

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

