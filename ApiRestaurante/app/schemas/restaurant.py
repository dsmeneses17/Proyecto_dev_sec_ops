from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class RestaurantBase(BaseModel):
    nombre: Annotated[str, Field(max_length=100)]
    descripcion: Annotated[str, Field(max_length=500)] | None = None
    logo: HttpUrl | None = None
    telefono: str | None = None
    direccion: str | None = None
    horarios: dict | None = None
    slug: Annotated[str, Field(max_length=100)] | None = None
    qr_color_fg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#000000"  # QR foreground color
    qr_color_bg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#FFFFFF"  # QR background color


class RestaurantCreate(RestaurantBase):
    id: UUID | None = None


class RestaurantUpdate(RestaurantBase):
    id: UUID  # <-- ahora UUID en lugar de str


class RestaurantOut(BaseModel):
    id: UUID  # <-- ahora UUID en lugar de str
    nombre: str
    descripcion: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    horarios: dict | None = None
    slug: str | None = None
    logo: str | None = None  # ✅ ahora opcional
    qr_color_fg: str = "#000000"
    qr_color_bg: str = "#FFFFFF"

    class Config:
        from_attributes = True  # en Pydantic v2 reemplaza orm_mode


class RestaurantQRColorUpdate(BaseModel):
    """Schema for updating QR colors only."""

    qr_color_fg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#000000"
    qr_color_bg: Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")] = "#FFFFFF"
