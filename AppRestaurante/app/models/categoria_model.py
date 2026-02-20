from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=50, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, description="Descripción opcional")
    posicion: int = Field(..., description="Posición usada para ordenamiento")
    activa: Optional[bool] = Field(default=True, description="Si la categoría está activa")
    restaurante_id: Optional[UUID] = None  # 👈 NO obligatorio

class CategoriaCreate(CategoriaBase):
    restaurante_id: Optional[UUID] = None
    id: Optional[UUID] = None


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    posicion: Optional[int] = None
    activa: Optional[bool] = None

class CategoriaOut(CategoriaBase):
    id: UUID
    restaurante_id: UUID
    creado_en: datetime
    actualizado_en: datetime