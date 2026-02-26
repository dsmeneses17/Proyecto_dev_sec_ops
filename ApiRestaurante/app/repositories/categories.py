from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.category import Category


def get_by_id(db: Session, category_id) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def list_by_restaurant_id(db: Session, restaurant_id) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.restaurante_id == restaurant_id)
        .order_by(Category.posicion.asc())
        .all()
    )


def create(
    db: Session,
    *,
    restaurante_id,
    nombre: str,
    posicion: int,
    descripcion: str | None = None,
    activa: bool = True,
) -> Category:
    category = Category(
        restaurante_id=restaurante_id,
        nombre=nombre,
        descripcion=descripcion,
        posicion=posicion,
        activa=activa,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
