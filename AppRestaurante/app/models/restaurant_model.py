from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
from uuid import UUID

class RestaurantBase(BaseModel):
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    horarios: Optional[Dict] = None
    logo: Optional[HttpUrl] = None

class RestaurantCreate(RestaurantBase):
    id: Optional[UUID] = None  


class RestaurantUpdate(BaseModel):
    id: UUID   # <-- corregido
    nombre: Optional[str] = None
    slug: Optional[str] = None
    descripcion: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    horarios: Optional[Dict] = None
    logo:Optional[str] = None

class RestaurantOut(RestaurantBase):
    id: UUID   # <-- corregido

    model_config = { 
        "from_attributes": True,     
        "json_encoders": {UUID: str} # UUID a string automáticamente 
    }
