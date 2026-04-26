from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    nombre: Annotated[str, Field(max_length=50)]
    descripcion: str | None = None
    posicion: Annotated[int, Field(ge=0)]
    activa: bool | None = True


class CategoryCreate(CategoryBase):
    restaurante_id: UUID | None = None


class CategoryUpdate(CategoryBase):
    pass


class CategoryOut(BaseModel):
    id: UUID
    restaurante_id: UUID
    nombre: str
    descripcion: str | None = None
    posicion: int
    activa: bool

    class Config:
        from_attributes = True  # Pydantic v2


class CategoryReorder(BaseModel):
    """Schema para reordenar categorías."""

    categorias: list[dict]  # [{"id": "...", "posicion": 1}, ...]
