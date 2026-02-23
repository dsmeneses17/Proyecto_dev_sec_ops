# app/routers/public_menu.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish
from datetime import datetime
import json
import redis
from redis.exceptions import RedisError
from decimal import Decimal

router = APIRouter(prefix="/api/v1/public/menu", tags=["public"])

# In docker-compose we don't run Redis. Keep caching optional.
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


@router.get("/restaurants")
async def list_public_restaurants(db: Session = Depends(get_db)):
    """Return basic restaurant info for public menu discovery.

    Kept intentionally small to avoid leaking internal data.
    """

    restaurants = (
        db.query(Restaurant)
        .order_by(Restaurant.nombre.asc())
        .all()
    )

    return [
        {
            "id": str(r.id),
            "nombre": r.nombre,
            "slug": r.slug,
            "logo_url": r.logo,
        }
        for r in restaurants
    ]

@router.get("/{slug}")
async def get_public_menu(slug: str, db: Session = Depends(get_db)):

    cache_key = f"public_menu:{slug}"

    # 🔥 1️⃣ Cache Hit (optional)
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except RedisError:
        cached = None

    # 🔍 2️⃣ Cache Miss → consulta BD
    restaurant = db.query(Restaurant).filter(
        Restaurant.slug == slug
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
            "logo_url": restaurant.logo,
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
                    "precio": float(p.precio) if isinstance(p.precio, Decimal) else p.precio,
                    "precio_oferta": float(p.precio_oferta) if isinstance(p.precio_oferta, Decimal) else p.precio_oferta,
                    "imagen_url": p.imagen_url,
                    "destacado": p.destacado,
                    "etiquetas": p.etiquetas,
                }
                for p in platos
            ]
        })

    # 💾 Guardar en cache por 5 minutos (optional)
    try:
        redis_client.setex(cache_key, 300, json.dumps(response))
    except (RedisError, TypeError):
        # If Redis isn't available or response can't be serialized, just skip caching.
        pass

    return response
