from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.deps import get_db
from app.models.category import Category
from app.models.restaurant import Restaurant
from app.schemas.category import CategoryCreate, CategoryOut, CategoryReorder, CategoryUpdate
from app.utils.cache_manager import invalidate_menu_cache

router = APIRouter(
    prefix="",  # Sin prefijo aquí
    tags=["categorias"],
)


@router.get("/", response_model=list[CategoryOut])  # <- sin slash
async def list_categories(user=Depends(get_current_user), db: Session = Depends(get_db)):

    restaurant = db.query(Restaurant).filter(Restaurant.admin_id == user["id"]).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    categorias = db.query(Category).filter(Category.restaurante_id == restaurant.id).all()

    return categorias


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(category_id: UUID, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Buscar restaurante del admin autenticado
    restaurant = db.query(Restaurant).filter(Restaurant.admin_id == user["id"]).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    # Buscar la categoría que pertenezca a ese restaurante
    categoria = db.query(Category).filter(Category.id == category_id, Category.restaurante_id == restaurant.id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return categoria


@router.post("/", response_model=CategoryOut)
async def create_category(
    data: CategoryCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    if current_user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    restaurant = db.query(Restaurant).filter(Restaurant.admin_id == current_user["id"]).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Este usuario no tiene restaurante asociado")

    existing = (
        db.query(Category).filter(Category.restaurante_id == restaurant.id, Category.nombre == data.nombre).first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")

    new_category = Category(**data.model_dump())

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    # Invalidate menu cache for this restaurant
    invalidate_menu_cache(restaurant.slug)

    return new_category


@router.put("/{id}", response_model=CategoryOut)
async def update_category(
    id: UUID, data: CategoryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
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

    # Invalidate menu cache for this restaurant
    restaurant = db.query(Restaurant).filter(Restaurant.id == category.restaurante_id).first()
    if restaurant:
        invalidate_menu_cache(restaurant.slug)

    return category


@router.delete("/{id}")
async def delete_category(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    # Get restaurant before deleting category
    restaurant = db.query(Restaurant).filter(Restaurant.id == category.restaurante_id).first()

    db.delete(category)
    db.commit()

    # Invalidate menu cache for this restaurant
    if restaurant:
        invalidate_menu_cache(restaurant.slug)

    return {"message": "Categoría eliminada"}


@router.patch("/reorder", response_model=dict)
async def reorder_categories(data: CategoryReorder, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Reordenar categorías de un restaurante."""

    if user["rol"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    # Obtener el restaurante del admin
    restaurant = db.query(Restaurant).filter(Restaurant.admin_id == user["id"]).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    # Actualizar las posiciones de las categorías
    for item in data.categorias:
        category_id = item.get("id")
        posicion = item.get("posicion")

        if not category_id or posicion is None:
            raise HTTPException(status_code=400, detail="Falta id o posición en reorder")

        category = (
            db.query(Category)
            .filter(Category.id == UUID(category_id), Category.restaurante_id == restaurant.id)
            .first()
        )

        if not category:
            raise HTTPException(status_code=404, detail=f"Categoría {category_id} no encontrada")

        category.posicion = posicion

    db.commit()

    # Invalidate menu cache for this restaurant
    invalidate_menu_cache(restaurant.slug)

    return {"message": "Categorías reordenadas exitosamente"}
