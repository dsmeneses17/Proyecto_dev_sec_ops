from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories import restaurants as restaurants_repo
from app.utils.slug import generate_unique_slug


class RestaurantServiceError(Exception):
    pass


class RestaurantSlugAlreadyExists(RestaurantServiceError):
    pass


@dataclass(frozen=True)
class CreateRestaurantInput:
    nombre: str
    admin_id: int
    slug: str | None = None
    descripcion: str | None = None
    logo: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    horarios: dict | None = None


def create_restaurant(db: Session, data: CreateRestaurantInput):
    # Auto-generate slug from nombre if not provided
    if data.slug:
        # If explicitly provided, verify uniqueness
        existing = restaurants_repo.get_by_slug(db, data.slug)
        if existing is not None:
            raise RestaurantSlugAlreadyExists("Slug de restaurante ya existe")
        final_slug = data.slug
    else:
        final_slug = generate_unique_slug(db, data.nombre)

    return {
        "nombre": data.nombre,
        "slug": final_slug,
        "admin_id": data.admin_id,
        "descripcion": data.descripcion,
        "logo": data.logo,
        "telefono": data.telefono,
        "direccion": data.direccion,
        "horarios": data.horarios,
    }
