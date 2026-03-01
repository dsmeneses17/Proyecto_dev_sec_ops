from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict
from typing_extensions import Annotated
from uuid import UUID

class RestaurantBase(BaseModel):
    nombre: Annotated[str, Field(max_length=100)]
    descripcion: Optional[Annotated[str, Field(max_length=500)]] = None
    logo: Optional[HttpUrl] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    horarios: Optional[Dict] = None
    slug: Optional[Annotated[str, Field(max_length=100)]] = None
    qr_color_fg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#000000"  # QR foreground color
    qr_color_bg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#FFFFFF"  # QR background color

    

class RestaurantCreate(RestaurantBase):
    id: Optional[UUID] = None

class RestaurantUpdate(RestaurantBase):
    id: UUID   # <-- ahora UUID en lugar de str

class RestaurantOut(BaseModel):
    id: UUID   # <-- ahora UUID en lugar de str
    nombre: str
    descripcion: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    horarios: Optional[Dict] = None
    slug: Optional[str] = None
    logo: Optional[str] = None  # ✅ ahora opcional
    qr_color_fg: str = "#000000"
    qr_color_bg: str = "#FFFFFF"

    class Config:
        from_attributes = True  # en Pydantic v2 reemplaza orm_mode

class RestaurantQRColorUpdate(BaseModel):
    """Schema for updating QR colors only."""
    qr_color_fg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#000000"
    qr_color_bg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#FFFFFF"