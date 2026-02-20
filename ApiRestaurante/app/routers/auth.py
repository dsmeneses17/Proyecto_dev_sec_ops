from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.core.security import create_access_token, get_current_user, create_access_token, decode_token
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.utils.security import hash_password, verify_password
from app.models.user import User
from app.deps import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.core.security import  SECRET_KEY, ALGORITHM

from jose import JWTError, jwt
from app.models.restaurant import Restaurant


router = APIRouter()


@router.post("/login")
def login(user_credentials: dict, db: Session = Depends(get_db)):
    usuario = user_credentials["usuario"]
    password = user_credentials["password"]

    # Buscar usuario en la DB
    db_user = db.query(User).filter(User.usuario == usuario).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Credenciales inválidas")

    if not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Buscar restaurante si es admin
    restaurant_id = None
    if db_user.rol == "admin":
        if db_user.restaurants and len(db_user.restaurants) > 0:
            restaurant_id = db_user.restaurants[0].id
        else:
            restaurant_id = None  # Admin sin restaurante
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    # Crear token con info completa
    access_token = create_access_token(data={
        "sub": str(db_user.id),      # UUID del usuario como string
        "rol": db_user.rol,
        "email": db_user.email,
        "restaurant_id": str(restaurant_id) if restaurant_id else None,
        "restaurant_slug": str(restaurant.slug ) if restaurant.slug else None 
    })
    print(f"access token: {access_token}")
    # Retornar token y datos mínimos
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(db_user.id),
        "rol": db_user.rol,
        "restaurant_id": str(restaurant_id) if restaurant_id else None,
        "restaurant_slug": str(restaurant.slug ) if restaurant.slug else None
    }



@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    # current_user ya viene decodificado desde el token
    return current_user




@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.usuario == user.usuario).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    new_user = User(
        nombre_completo=user.nombre_completo,
        usuario=user.usuario,
        password=hash_password(user.password),
        rol=user.rol,
        activo=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario registrado"}

@router.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
        data = {"sub": payload["sub"], "rol": payload["rol"]}
        new_access_token = create_access_token(data)
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
