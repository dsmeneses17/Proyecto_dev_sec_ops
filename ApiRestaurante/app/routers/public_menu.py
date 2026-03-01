# app/routers/public_menu.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish
from datetime import datetime, timedelta
import json
import redis
from redis.exceptions import RedisError
from decimal import Decimal
import threading
from typing import Optional
from app.cache import memory_cache, redis_client

router = APIRouter(prefix="/api/v1/public/menu", tags=["public"])


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
    """Get public menu for a restaurant by slug.
    
    Uses multi-layer caching strategy:
    1. In-memory cache (fastest)
    2. Redis cache (distributed, if available)
    3. Database (cache miss)
    """

    cache_key = f"public_menu:{slug}"

    # Layer 1: Try in-memory cache
    cached = memory_cache.get(cache_key)
    if cached:
        return cached

    # Layer 2: Try Redis cache
    try:
        redis_cached = redis_client.get(cache_key)
        if redis_cached:
            result = json.loads(redis_cached)
            # Repopulate in-memory cache
            memory_cache.set(cache_key, result)
            return result
    except (RedisError, json.JSONDecodeError):
        pass

    # Layer 3: Query database
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
            Dish.disponible == True,
            Dish.eliminado_en == None
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

    # Store in caches
    memory_cache.set(cache_key, response)
    
    try:
        redis_client.setex(cache_key, 300, json.dumps(response))
    except (RedisError, TypeError):
        # If Redis isn't available, in-memory cache is sufficient
        pass

    return response
