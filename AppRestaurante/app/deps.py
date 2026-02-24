from fastapi import Depends, HTTPException, Header
import jwt

SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

async def get_current_user(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Formato de autorización inválido")

        payload = decode_token(token)
        username: str = payload.get("sub")
        role: str = payload.get("role")   #aquí extraemos el rol

        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # devolvemos un objeto simulado con rol incluido
    return {
        "id": 1,
        "usuario": username,
        "email": f"{username}@example.com",
        "rol": role
    }