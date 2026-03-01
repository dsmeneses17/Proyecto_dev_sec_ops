from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=50, description="Nombre de la categoría")
    descripcion: str | None = Field(None, description="Descripción opcional")
    posicion: int = Field(..., description="Posición usada para ordenamiento")
    activa: bool | None = Field(default=True, description="Si la categoría está activa")
    restaurante_id: UUID | None = None

class CategoriaCreate(CategoriaBase):
    restaurante_id: UUID | None = None
    id: UUID | None = None


class CategoriaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=50)
    descripcion: str | None = None
    posicion: int | None = None
    activa: bool | None = None

class CategoriaOut(CategoriaBase):
    id: UUID
    restaurante_id: UUID
    creado_en: datetime
    actualizado_en: datetime
