from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List


from app.deps import get_db
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.core.security import get_current_user, get_current_user_debug



router = APIRouter(
    prefix="",  # Sin prefijo aquí
    tags=["categorias"]
)

@router.get("/", response_model=List[CategoryOut])  # <- sin slash
async def list_categories(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
   
    restaurant = db.query(Restaurant).filter(
        Restaurant.admin_id == user["id"]
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    categorias = db.query(Category).filter(
        Category.restaurante_id == restaurant.id
    ).all()

    return categorias


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: UUID,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Buscar restaurante del admin autenticado
    restaurant = db.query(Restaurant).filter(
        Restaurant.admin_id == user["id"]
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    # Buscar la categoría que pertenezca a ese restaurante
    categoria = db.query(Category).filter(
        Category.id == category_id,
        Category.restaurante_id == restaurant.id
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return categoria

@router.post("/", response_model=CategoryOut)
async def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    restaurant = db.query(Restaurant).filter(
        Restaurant.admin_id == current_user["id"]
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Este usuario no tiene restaurante asociado"
        )

    existing = db.query(Category).filter(
        Category.restaurante_id == restaurant.id,
        Category.nombre == data.nombre
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una categoría con ese nombre"
        )

    new_category = Category(
        **data.model_dump()
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.put("/{id}", response_model=CategoryOut)
async def update_category(
    id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{id}")
async def delete_category(
    id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    db.delete(category)
    db.commit()
    return {"message": "Categoría eliminada"}
