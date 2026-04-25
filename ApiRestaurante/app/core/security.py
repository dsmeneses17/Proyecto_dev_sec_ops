# app/core/security.py
import os
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Configure it via Secret Manager/Cloud Run env vars.")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# app/core/security.py


# Función temporal para debug
async def oauth2_scheme_debug(token: str = Depends(oauth2_scheme)):
    print("Token recibido en oauth2_scheme_debug:", token)
    return token


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crea un JWT con datos del usuario"""
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


def get_current_user_debug(authorization: str = Header(None)):
    print("Header Authorization recibido:", authorization)

    if not authorization:
        raise HTTPException(status_code=401, detail="No se envió Authorization")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato inválido")

    token = authorization[len("Bearer ") :].strip()
    print("Token extraído:", token)

    try:
        payload = decode_token(token)
        print("Payload decodificado:", payload)
    except Exception as e:
        print("Error al decodificar token:", e)
        raise HTTPException(status_code=401, detail="Token inválido")

    return {
        "id": payload.get("sub"),
        "rol": payload.get("rol"),
        "email": payload.get("email"),
        "restaurant_id": payload.get("restaurant_id"),
    }


def get_current_user(token: str = Depends(oauth2_scheme)):
    print("Token recibido en get_current_user:", token)
    try:
        payload = decode_token(token)
        print("Payload decodificado:", payload)
    except Exception as e:
        print("Error al decodificar token:", e)
        raise HTTPException(status_code=401, detail="Token inválid")
    payload = decode_token(token)

    user_id = payload.get("sub")
    role = payload.get("rol")
    email = payload.get("email")
    restaurant_id = payload.get("restaurant_id")
    restaurant_slug = payload.get("restaurant_slug")

    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Token inválido")

    return {
        "id": user_id,
        "rol": role,
        "email": email,
        "restaurant_id": restaurant_id,
        "restaurant_slug": restaurant_slug,
    }
