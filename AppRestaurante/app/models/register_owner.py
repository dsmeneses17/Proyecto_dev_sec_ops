from pydantic import BaseModel, EmailStr, Field


class OwnerRestaurantRegister(BaseModel):
    # Owner
    nombre_completo: str = Field(..., min_length=2, max_length=120)
    usuario: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=256)

    # Restaurant
    restaurant_nombre: str = Field(..., min_length=2, max_length=100)
    restaurant_slug: str = Field(..., min_length=2, max_length=120)
    restaurant_telefono: str | None = None
    restaurant_direccion: str | None = None
