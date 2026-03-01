from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.core.security import create_access_token, get_current_user, create_access_token, decode_token
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.utils.security import hash_password, verify_password
from app.utils.slug import generate_unique_slug
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
    restaurant = None
    if restaurant_id:
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    restaurant_slug = restaurant.slug if restaurant else None
    
    # Crear token con info completa
    access_token = create_access_token(data={
        "sub": str(db_user.id),      # UUID del usuario como string
        "rol": db_user.rol,
        "email": db_user.email,
        "restaurant_id": str(restaurant_id) if restaurant_id else None,
    "restaurant_slug": str(restaurant_slug) if restaurant_slug else None
    })
    print(f"access token: {access_token}")
    # Retornar token y datos mínimos
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(db_user.id),
        "rol": db_user.rol,
        "restaurant_id": str(restaurant_id) if restaurant_id else None,
    "restaurant_slug": str(restaurant_slug) if restaurant_slug else None
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

    existing_email = db.query(User).filter(User.email.ilike(user.email.strip())).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    new_user = User(
        nombre_completo=user.nombre_completo,
        usuario=user.usuario,
        email=user.email,
        password=hash_password(user.password),
        rol=user.rol,
        activo=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "Usuario registrado",
        "user_id": str(new_user.id),
        "rol": new_user.rol,
    }


@router.post("/register-owner")
def register_owner(payload: dict, db: Session = Depends(get_db)):
    """Register a new restaurant owner (admin) plus their restaurant."""

    required = [
        "nombre_completo",
        "usuario",
        "email",
        "password",
        "restaurant_nombre",
    ]
    missing = [k for k in required if not (payload.get(k) or "").strip()]
    if missing:
        raise HTTPException(status_code=422, detail=f"Faltan campos: {', '.join(missing)}")

    usuario = payload["usuario"].strip()
    email = payload["email"].strip()
    email_lc = email.lower()

    # Auto-generate slug from restaurant name; honour an explicit slug if provided.
    restaurant_nombre = payload["restaurant_nombre"].strip()
    explicit_slug = (payload.get("restaurant_slug") or "").strip()
    if explicit_slug:
        restaurant_slug = generate_unique_slug(db, explicit_slug)
    else:
        restaurant_slug = generate_unique_slug(db, restaurant_nombre)

    if db.query(User).filter(User.usuario == usuario).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    if db.query(User).filter(User.email.ilike(email_lc)).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    new_user = User(
        nombre_completo=payload["nombre_completo"].strip(),
        usuario=usuario,
        email=email,
        password=hash_password(payload["password"]),
        rol="admin",
        activo=True,
    )
    db.add(new_user)
    db.flush()  # get user id

    new_restaurant = Restaurant(
        nombre=restaurant_nombre,
        slug=restaurant_slug,
        telefono=(payload.get("restaurant_telefono") or None),
        direccion=(payload.get("restaurant_direccion") or None),
        admin_id=new_user.id,
    )
    db.add(new_restaurant)

    db.commit()
    db.refresh(new_user)
    db.refresh(new_restaurant)

    return {
        "message": "Registro completado",
        "user_id": str(new_user.id),
        "restaurant_id": str(new_restaurant.id),
        "restaurant_slug": new_restaurant.slug,
    }

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
