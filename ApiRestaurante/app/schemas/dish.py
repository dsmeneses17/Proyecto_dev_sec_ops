from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DishBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: str | None = Field(None, max_length=300)
    precio: Decimal
    precio_oferta: Decimal | None = None
    disponible: bool | None = True
    destacado: bool | None = False
    etiquetas: list[str] | None = None
    posicion: int | None = None
    imagen_url: str | None = None
    categoria_id: UUID

    @field_validator("etiquetas")
    @classmethod
    def validate_etiquetas(cls, value: list[str] | None):
        if value is None:
            return value

        normalized: list[str] = []
        for item in value:
            tag = (item or "").strip().lower()
            if not tag:
                continue
            if len(tag) > 30:
                raise ValueError(f"Etiqueta demasiado larga: {item}")
            normalized.append(tag)

        unique_tags = list(dict.fromkeys(normalized))
        if len(unique_tags) > 10:
            raise ValueError("Máximo 10 etiquetas por plato")

        return unique_tags


class DishCreate(DishBase):
    pass


class DishUpdate(DishBase):
    pass


class DishOut(DishBase):
    id: UUID
    creado_en: datetime | None
    actualizado_en: datetime | None
    eliminado_en: datetime | None

    class Config:
        from_attributes = True  # en Pydantic v2, reemplaza orm_mode
