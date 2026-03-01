from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import Annotated
from uuid import UUID

class CategoryBase(BaseModel):
    nombre: Annotated[str, Field(max_length=50)]
    descripcion: Optional[str] = None
    posicion: Annotated[int, Field(ge=0)]
    activa: Optional[bool] = True

class CategoryCreate(CategoryBase):
    restaurante_id: UUID | None = None

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(BaseModel):
    id: UUID
    restaurante_id: UUID
    nombre: str
    descripcion: Optional[str] = None
    posicion: int
    activa: bool

    class Config:
        from_attributes = True  # Pydantic v2


class CategoryReorder(BaseModel):
    """Schema para reordenar categorías."""
    categorias: list[dict]  # [{"id": "...", "posicion": 1}, ...]

