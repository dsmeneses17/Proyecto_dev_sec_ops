from pydantic import BaseModel, Field
from pydantic import field_validator
from typing import Optional, List
from typing_extensions import Annotated
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class DishBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=300)
    precio: Decimal
    precio_oferta: Optional[Decimal] = None
    disponible: Optional[bool] = True
    destacado: Optional[bool] = False
    etiquetas: Optional[List[str]] = None
    posicion: Optional[int] = None
    imagen_url: Optional[str] = None
    categoria_id: UUID

    @field_validator("etiquetas")
    @classmethod
    def validate_etiquetas(cls, value: Optional[List[str]]):
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
    creado_en: Optional[datetime]
    actualizado_en: Optional[datetime]
    eliminado_en: Optional[datetime]

    class Config:
        from_attributes = True  # en Pydantic v2, reemplaza orm_mode