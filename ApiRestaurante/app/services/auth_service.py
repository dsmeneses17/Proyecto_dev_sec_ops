from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories import users as users_repo
from app.utils.security import hash_password, verify_password


class AuthServiceError(Exception):
    pass


class UsernameAlreadyExists(AuthServiceError):
    pass


class InvalidCredentials(AuthServiceError):
    pass


@dataclass(frozen=True)
class RegisterUserInput:
    nombre_completo: str
    usuario: str
    password: str
    rol: str = "cliente"
    email: str | None = None


def register_user(db: Session, data: RegisterUserInput):
    if users_repo.get_by_username(db, data.usuario) is not None:
        raise UsernameAlreadyExists("Usuario ya existe")

    password_hash = hash_password(data.password)
    return users_repo.create(
        db,
        nombre_completo=data.nombre_completo,
        usuario=data.usuario,
        password_hash=password_hash,
        rol=data.rol,
        email=data.email,
    )


def authenticate(db: Session, *, usuario: str, password: str):
    user = users_repo.get_by_username(db, usuario)
    if user is None:
        raise InvalidCredentials("Credenciales inválidas")

    if not verify_password(password, user.password):
        raise InvalidCredentials("Credenciales inválidas")

    return user
