"""Tests for in-memory cache and cache invalidation."""

import time

from app.cache import InMemoryCache, memory_cache
from app.utils.cache_manager import invalidate_menu_cache


class TestInMemoryCache:
    """Test the InMemoryCache class."""

    def test_cache_set_and_get(self):
        """Test setting and retrieving values from cache."""
        cache = InMemoryCache(ttl_seconds=300)
        test_data = {"key": "value", "nested": {"data": 123}}

        cache.set("test_key", test_data)
        result = cache.get("test_key")

        assert result == test_data

    def test_cache_expiration(self):
        """Test that cached values expire after TTL."""
        cache = InMemoryCache(ttl_seconds=1)  # 1 second TTL
        test_data = {"key": "value"}

        cache.set("test_key", test_data)
        assert cache.get("test_key") == test_data

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("test_key") is None

    def test_cache_clear_specific_key(self):
        """Test clearing a specific cache key."""
        cache = InMemoryCache(ttl_seconds=300)
        cache.set("key1", {"data": 1})
        cache.set("key2", {"data": 2})

        cache.clear("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == {"data": 2}

    def test_cache_clear_all(self):
        """Test clearing all cache."""
        cache = InMemoryCache(ttl_seconds=300)
        cache.set("key1", {"data": 1})
        cache.set("key2", {"data": 2})
        cache.set("key3", {"data": 3})

        cache.clear_all()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_cache_thread_safety(self):
        """Test that cache operations are thread-safe."""
        import threading
        cache = InMemoryCache(ttl_seconds=300)
        results = []

        def worker(thread_id):
            for i in range(100):
                cache.set(f"key_{thread_id}_{i}", {"data": i})
                value = cache.get(f"key_{thread_id}_{i}")
                if value is not None:
                    results.append(True)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All operations should succeed without race conditions
        assert len(results) == 500

    def test_cache_get_nonexistent_key(self):
        """Test getting a non-existent key returns None."""
        cache = InMemoryCache(ttl_seconds=300)
        assert cache.get("nonexistent") is None


class TestMenuCacheInvalidation:
    """Test cache invalidation for menu updates."""

    def test_invalidate_specific_menu_cache(self):
        """Test invalidating cache for a specific restaurant."""
        # Set some cache
        cache_key = "public_menu:test-restaurant"
        test_data = {"restaurant": {"id": "123"}, "categorias": []}
        memory_cache.set(cache_key, test_data)

        assert memory_cache.get(cache_key) == test_data

        # Invalidate
        invalidate_menu_cache("test-restaurant")

        assert memory_cache.get(cache_key) is None

    def test_invalidate_all_menu_caches(self):
        """Test invalidating all menu caches."""
        from app.utils.cache_manager import invalidate_all_menu_caches

        # Set multiple cache entries
        memory_cache.set("public_menu:restaurant-1", {"data": 1})
        memory_cache.set("public_menu:restaurant-2", {"data": 2})
        memory_cache.set("public_menu:restaurant-3", {"data": 3})

        # Invalidate all
        invalidate_all_menu_caches()

        assert memory_cache.get("public_menu:restaurant-1") is None
        assert memory_cache.get("public_menu:restaurant-2") is None
        assert memory_cache.get("public_menu:restaurant-3") is None
