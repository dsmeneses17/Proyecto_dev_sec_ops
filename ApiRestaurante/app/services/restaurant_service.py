from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories import restaurants as restaurants_repo


class RestaurantServiceError(Exception):
    pass


class RestaurantSlugAlreadyExists(RestaurantServiceError):
    pass


@dataclass(frozen=True)
class CreateRestaurantInput:
    nombre: str
    slug: str
    admin_id: int
    descripcion: str | None = None
    logo: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    horarios: dict | None = None


def create_restaurant(db: Session, data: CreateRestaurantInput):
    existing = restaurants_repo.get_by_slug(db, data.slug)
    if existing is not None:
        raise RestaurantSlugAlreadyExists("Slug de restaurante ya existe")

    # NOTE: repo level create() isn't implemented for restaurants in our minimal repo.
    # To keep this service useful and testable without refactoring routers, we return
    # a plain dict describing what would be created.
    return {
        "nombre": data.nombre,
        "slug": data.slug,
        "admin_id": data.admin_id,
        "descripcion": data.descripcion,
        "logo": data.logo,
        "telefono": data.telefono,
        "direccion": data.direccion,
        "horarios": data.horarios,
    }
