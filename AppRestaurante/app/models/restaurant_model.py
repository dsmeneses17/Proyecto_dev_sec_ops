from uuid import UUID

from pydantic import BaseModel, HttpUrl


class RestaurantBase(BaseModel):
    nombre: str
    slug: str
    descripcion: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    horarios: dict | None = None
    logo: HttpUrl | None = None


class RestaurantCreate(RestaurantBase):
    id: UUID | None = None


class RestaurantUpdate(BaseModel):
    id: UUID  # <-- corregido
    nombre: str | None = None
    slug: str | None = None
    descripcion: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    horarios: dict | None = None
    logo: str | None = None


class RestaurantOut(RestaurantBase):
    id: UUID  # <-- corregido

    model_config = {
        "from_attributes": True,
        "json_encoders": {UUID: str},  # UUID a string automáticamente
    }
