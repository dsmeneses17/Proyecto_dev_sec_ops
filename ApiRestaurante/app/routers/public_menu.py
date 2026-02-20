# app/routers/public_menu.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish
from datetime import datetime
import json
import redis

router = APIRouter(prefix="/api/v1/public/menu", tags=["public"])

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@router.get("/{slug}")
async def get_public_menu(slug: str, db: Session = Depends(get_db)):

    cache_key = f"public_menu:{slug}"

    # 🔥 1️⃣ Cache Hit
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 🔍 2️⃣ Cache Miss → consulta BD
    restaurant = db.query(Restaurant).filter(
        Restaurant.slug == slug,
        Restaurant.activo == True
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    categorias = db.query(Category).filter(
        Category.restaurante_id == restaurant.id
    ).order_by(Category.posicion.asc()).all()

    response = {
        "restaurant": {
            "id": str(restaurant.id),
            "nombre": restaurant.nombre,
            "logo_url": restaurant.logo_url,
            "slug": restaurant.slug,
        },
        "categorias": []
    }

    for cat in categorias:
        platos = db.query(Dish).filter(
            Dish.categoria_id == cat.id,
            Dish.disponible == True
        ).order_by(Dish.posicion.asc()).all()

        if not platos:
            continue

        response["categorias"].append({
            "id": str(cat.id),
            "nombre": cat.nombre,
            "platos": [
                {
                    "id": str(p.id),
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "precio": p.precio,
                    "precio_oferta": p.precio_oferta,
                    "imagen_url": p.imagen_url,
                    "destacado": p.destacado,
                    "etiquetas": p.etiquetas,
                }
                for p in platos
            ]
        })

    # 💾 Guardar en cache por 5 minutos
    redis_client.setex(cache_key, 300, json.dumps(response))

    return response
