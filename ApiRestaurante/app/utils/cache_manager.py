"""Cache invalidation utilities for public menu."""

import redis
from redis.exceptions import RedisError
from app.cache import memory_cache, redis_client


def invalidate_menu_cache(slug: str) -> None:
    """Invalidate menu cache for a specific restaurant.
    
    Args:
        slug: Restaurant slug
    """
    cache_key = f"public_menu:{slug}"
    
    # Invalidate in-memory cache
    memory_cache.clear(cache_key)
    
    # Invalidate Redis cache
    try:
        redis_client.delete(cache_key)
    except RedisError:
        # Redis not available, but in-memory cache is invalidated
        pass


def invalidate_all_menu_caches() -> None:
    """Invalidate all menu caches (use sparingly)."""
    # Invalidate all in-memory caches
    memory_cache.clear_all()
    
    # Invalidate all Redis caches with pattern
    try:
        # Find all keys matching the pattern
        keys = redis_client.keys("public_menu:*")
        if keys:
            redis_client.delete(*keys)
    except RedisError:
        # Redis not available, but in-memory caches are cleared
        pass

