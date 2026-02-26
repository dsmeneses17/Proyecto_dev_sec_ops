from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories import categories as categories_repo


class CategoryServiceError(Exception):
    pass


class CategoryNameAlreadyExists(CategoryServiceError):
    pass


@dataclass(frozen=True)
class CreateCategoryInput:
    restaurante_id: object
    nombre: str
    posicion: int
    descripcion: str | None = None
    activa: bool = True


def create_category(db: Session, data: CreateCategoryInput):
    existing = categories_repo.list_by_restaurant_id(db, data.restaurante_id)
    if any((c.nombre or "").strip().lower() == data.nombre.strip().lower() for c in existing):
        raise CategoryNameAlreadyExists("Ya existe una categoría con ese nombre")

    return categories_repo.create(
        db,
        restaurante_id=data.restaurante_id,
        nombre=data.nombre,
        descripcion=data.descripcion,
        posicion=data.posicion,
        activa=data.activa,
    )
