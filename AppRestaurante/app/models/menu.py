from pydantic import BaseModel
from typing import List, Optional


class DishPublic(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    precio: float
    precio_oferta: Optional[float]
    imagen_url: Optional[str]
    destacado: Optional[bool]
    etiquetas: Optional[str]


class CategoryPublic(BaseModel):
    id: str
    nombre: str
    platos: List[DishPublic]


class RestaurantPublic(BaseModel):
    id: str
    nombre: str
    logo_url: Optional[str]
    slug: str


class PublicMenuResponse(BaseModel):
    restaurant: RestaurantPublic
    categorias: List[CategoryPublic]
