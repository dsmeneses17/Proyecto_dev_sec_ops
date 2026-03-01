from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.usuario == username).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email.ilike(email.strip())).first()


def create(
    db: Session,
    *,
    nombre_completo: str,
    usuario: str,
    password_hash: str,
    rol: str = "cliente",
    email: str | None = None,
    activo: bool = True,
) -> User:
    user = User(
        nombre_completo=nombre_completo,
        usuario=usuario,
        password=password_hash,
        rol=rol,
        email=email,
        activo=activo,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
