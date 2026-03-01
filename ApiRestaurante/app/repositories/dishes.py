from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.dish import Dish


def get_by_id(db: Session, dish_id) -> Dish | None:
    return db.query(Dish).filter(Dish.id == dish_id).first()


def list_by_category_id(db: Session, category_id) -> list[Dish]:
    return (
        db.query(Dish)
        .filter(Dish.categoria_id == category_id)
        .order_by(Dish.posicion.asc().nullslast(), Dish.creado_en.desc())
        .all()
    )


def create(
    db: Session,
    *,
    categoria_id,
    nombre: str,
    precio: Decimal,
    descripcion: str | None = None,
    precio_oferta: Decimal | None = None,
    imagen_url: str | None = None,
    disponible: bool = True,
    destacado: bool = False,
    etiquetas: list[str] | None = None,
    posicion: int | None = None,
) -> Dish:
    dish = Dish(
        categoria_id=categoria_id,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        precio_oferta=precio_oferta,
        imagen_url=imagen_url,
        disponible=disponible,
        destacado=destacado,
        etiquetas=etiquetas,
        posicion=posicion,
    )
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish
