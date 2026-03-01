from fastapi import APIRouter, Depends, HTTPException
from app.utils.jwt_handler import get_current_user
from app.deps import get_db

from sqlalchemy.orm import Session,  joinedload
from app.models.dish import Dish
from app.models.category import Category
from app.models.restaurant import Restaurant
from app.schemas.dish import DishCreate, DishUpdate, DishOut
from app.core.security import get_current_user
from app.utils.cache_manager import invalidate_menu_cache
from typing import List
from uuid import UUID
from datetime import datetime

router = APIRouter(
    prefix="",  # Sin prefijo aquí
    tags=["dishes"]
)


@router.get("/by_category")
async def list_dishes_by_category(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.category import Category
    from app.models.dish import Dish

    restaurant_id = user.get("restaurant_id")
    if not restaurant_id:
        restaurant = db.query(Restaurant).filter(Restaurant.admin_id == user.get("id")).first()
        restaurant_id = restaurant.id if restaurant else None

    if not restaurant_id:
        return []

    categorias = db.query(Category).filter(
        Category.restaurante_id == restaurant_id
    ).all()
    result = []

    for cat in categorias:
        platos = db.query(Dish).filter(
            Dish.categoria_id == cat.id,
            Dish.eliminado_en == None
        ).all()

        result.append({
            "id": str(cat.id),
            "nombre": cat.nombre,
            "platos": [
                {
                    "id": str(p.id),
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "precio": p.precio,
                    "precio_oferta": p.precio_oferta,
                    "categoria_id": str(p.categoria_id),
                    "disponible": p.disponible,
                    "destacado": p.destacado,
                    "etiquetas": p.etiquetas,
                    "posicion": p.posicion,
                    "imagen_url": p.imagen_url,
                }
                for p in platos
            ]
        })

    return result

# Listar platos
@router.get("", response_model=List[DishOut])
async def list_dishes(
    user=Depends(get_current_user), 
     db: Session = Depends(get_db)):
    return db.query(Dish).filter(Dish.eliminado_en == None).all()

# Obtener plato por ID
@router.get("/{dish_id}", response_model=DishOut)
async def get_dish(
    dish_id: UUID, 
    user=Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    dish = db.query(Dish).filter(Dish.id == dish_id, Dish.eliminado_en == None).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    return dish



# Crear plato
@router.post("/", response_model=DishOut)
async def create_dish(payload: DishCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    new_dish = Dish(**payload.model_dump())
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    
    # Invalidate menu cache for the restaurant of this category
    category = db.query(Category).filter(Category.id == new_dish.categoria_id).first()
    if category:
        restaurant = db.query(Restaurant).filter(Restaurant.id == category.restaurante_id).first()
        if restaurant:
            invalidate_menu_cache(restaurant.slug)
    
    return new_dish

# Actualizar plato
@router.put("/{dish_id}", response_model=DishOut)
async def update_dish(dish_id: UUID, payload: DishUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id, Dish.eliminado_en == None).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    for key, value in payload.model_dump().items():
        setattr(dish, key, value)
    db.commit()
    db.refresh(dish)
    
    # Invalidate menu cache for the restaurant of this category
    category = db.query(Category).filter(Category.id == dish.categoria_id).first()
    if category:
        restaurant = db.query(Restaurant).filter(Restaurant.id == category.restaurante_id).first()
        if restaurant:
            invalidate_menu_cache(restaurant.slug)
    
    return dish

# Soft delete
@router.delete("/{dish_id}")
async def delete_dish(dish_id: UUID, user=Depends(get_current_user), db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id, Dish.eliminado_en == None).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    dish.eliminado_en = datetime.utcnow()
    db.commit()
    
    # Invalidate menu cache for the restaurant of this category
    category = db.query(Category).filter(Category.id == dish.categoria_id).first()
    if category:
        restaurant = db.query(Restaurant).filter(Restaurant.id == category.restaurante_id).first()
        if restaurant:
            invalidate_menu_cache(restaurant.slug)
    
    return {"detail": "Plato eliminado correctamente"}

# Cambiar disponibilidad
@router.patch("/{dish_id}/toggle_availability", response_model=DishOut)
async def toggle_availability(dish_id: UUID, user=Depends(get_current_user), db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id, Dish.eliminado_en == None).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    dish.disponible = not dish.disponible
    db.commit()
    db.refresh(dish)
    
    # Invalidate menu cache for the restaurant of this category
    category = db.query(Category).filter(Category.id == dish.categoria_id).first()
    if category:
        restaurant = db.query(Restaurant).filter(Restaurant.id == category.restaurante_id).first()
        if restaurant:
            invalidate_menu_cache(restaurant.slug)
    
    return dish