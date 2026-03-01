from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.deps import get_db
from app.models.restaurant import Restaurant
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantOut
)

from app.core.security import get_current_user



router = APIRouter(
    prefix="",  # Sin prefijo aquí
    tags=["restaurantes"]
)

@router.get("", response_model=RestaurantOut)
def get_my_restaurant(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print("llego a api resturanr")
    restaurant = db.query(Restaurant).filter(
        Restaurant.admin_id == user["id"]
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    return restaurant




@router.get("/restaurant/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant_by_id(
    restaurant_id: UUID = Path(..., description="ID del restaurante a consultar"),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un restaurante específico por su ID.
    Solo accesible para admins.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    #restringir acceso solo al admin dueño del restaurante
    if restaurant.admin_id != user["id"] and user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado para ver este restaurante")

    return restaurant

@router.post("/restaurant", response_model=RestaurantOut)
def create_or_update_restaurant(
    data: RestaurantCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"token admin_restaurante: {user}")
    print(f"datos que llegan: {data.dict()}")

    if user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    # Convertimos todo a formato JSON serializable
    data_dict = data.model_dump(mode="json")  
    # Esto convierte automáticamente UUID y HttpUrl a str

    # 🔹 UPDATE
    if data.id:
        restaurant = db.query(Restaurant).filter(
            Restaurant.id == data.id,
            Restaurant.admin_id == user["id"]
        ).first()

        if not restaurant:
            raise HTTPException(
                status_code=404,
                detail=f"Restaurante con id {data.id} no existe"
            )

        # Actualizar solo los campos enviados
        for field, value in data_dict.items():
            setattr(restaurant, field, value)

        db.commit()
        db.refresh(restaurant)
        return restaurant

    # CREATE
    existing = db.query(Restaurant).filter(
        Restaurant.admin_id == user["id"]
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Este usuario ya tiene un restaurante"
        )

    restaurant = Restaurant(
        **data_dict,
        admin_id=user["id"]
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.put("/restaurant", response_model=RestaurantOut)
def update_restaurant(
    data: RestaurantUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.admin_id == user["id"]
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/restaurant/{restaurant_id}")
def delete_restaurant(
    restaurant_id: UUID = Path(..., description="ID del restaurante a eliminar"),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if restaurant.admin_id != user["id"] and user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado para eliminar este restaurante")

    db.delete(restaurant)
    db.commit()

    return {"message": "Restaurante eliminado correctamente"}
