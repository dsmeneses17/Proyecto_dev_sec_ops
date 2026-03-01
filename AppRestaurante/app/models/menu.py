from pydantic import BaseModel
from typing import List, Optional, Union


class DishPublic(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    precio: float
    precio_oferta: Optional[float]
    imagen_url: Optional[str]
    destacado: Optional[bool]
    # Backend may return etiquetas as a list
    etiquetas: Optional[Union[str, List[str]]]


class CategoryPublic(BaseModel):
    id: str
    nombre: str
    platos: List[DishPublic]


class RestaurantPublic(BaseModel):
    id: str
    nombre: str
    logo_url: Optional[str]
    slug: str
    qr_color_fg: str = "#000000"
    qr_color_bg: str = "#FFFFFF"


class PublicMenuResponse(BaseModel):
    restaurant: RestaurantPublic
    categorias: List[CategoryPublic]
