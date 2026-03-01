"""In-memory and Redis cache management for public menu."""

import threading
from datetime import datetime, timedelta

import redis


class InMemoryCache:
    """Simple thread-safe in-memory cache with TTL (Time-To-Live)."""

    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        self.lock = threading.Lock()

    def get(self, key: str) -> dict | None:
        """Get cached value if not expired."""
        with self.lock:
            if key not in self.cache:
                return None

            value, timestamp = self.cache[key]
            if datetime.utcnow() - timestamp > timedelta(seconds=self.ttl_seconds):
                del self.cache[key]
                return None

            return value

    def set(self, key: str, value: dict) -> None:
        """Store value in cache with current timestamp."""
        with self.lock:
            self.cache[key] = (value, datetime.utcnow())

    def clear(self, key: str) -> None:
        """Remove specific key from cache."""
        with self.lock:
            self.cache.pop(key, None)

    def clear_all(self) -> None:
        """Clear all cache."""
        with self.lock:
            self.cache.clear()


# Global cache instances
memory_cache = InMemoryCache(ttl_seconds=300)
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
