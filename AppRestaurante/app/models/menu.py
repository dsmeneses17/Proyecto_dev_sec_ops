from pydantic import BaseModel


class DishPublic(BaseModel):
    id: str
    nombre: str
    descripcion: str | None
    precio: float
    precio_oferta: float | None
    imagen_url: str | None
    destacado: bool | None
    # Backend may return etiquetas as a list
    etiquetas: str | list[str] | None


class CategoryPublic(BaseModel):
    id: str
    nombre: str
    platos: list[DishPublic]


class RestaurantPublic(BaseModel):
    id: str
    nombre: str
    logo_url: str | None
    slug: str
    qr_color_fg: str = "#000000"
    qr_color_bg: str = "#FFFFFF"


class PublicMenuResponse(BaseModel):
    restaurant: RestaurantPublic
    categorias: list[CategoryPublic]
