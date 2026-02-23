from pydantic import BaseModel, Field
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