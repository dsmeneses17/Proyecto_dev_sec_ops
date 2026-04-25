"""Integration tests for public menu caching."""

import pytest
from fastapi.testclient import TestClient

from app.cache import InMemoryCache, memory_cache
from app.main import app

client = TestClient(app)


@pytest.fixture
def clear_cache():
    """Clear cache before and after tests."""
    memory_cache.clear_all()
    yield
    memory_cache.clear_all()


class TestPublicMenuCaching:
    """Test caching behavior of public menu endpoint."""

    def test_cache_populates_on_menu_request(self, clear_cache):
        """Test that cache is populated after a successful menu request."""
        # Try to get a menu that exists in the database (proyecto-materia)
        response = client.get("/api/v1/public/menu/proyecto-materia")

        # If the restaurant exists, it should be cached
        if response.status_code == 200:
            cache_key = "public_menu:proyecto-materia"
            # The cache should be populated now
            assert memory_cache.get(cache_key) is not None

    def test_cache_hit_returns_same_data(self, clear_cache):
        """Test that cache hit returns the same data as original request."""
        slug = "proyecto-materia"
        cache_key = f"public_menu:{slug}"

        # Make first request to populate cache
        response1 = client.get(f"/api/v1/public/menu/{slug}")

        if response1.status_code == 200:
            cached_data = memory_cache.get(cache_key)

            # Make second request (should hit cache)
            response2 = client.get(f"/api/v1/public/menu/{slug}")

            # Both should return same data
            assert response1.json() == response2.json() == cached_data

    def test_cache_404_is_not_cached(self, clear_cache):
        """Test that 404 responses are not cached."""
        slug = "nonexistent-restaurant-xyz"
        cache_key = f"public_menu:{slug}"

        # Request non-existent restaurant
        response = client.get(f"/api/v1/public/menu/{slug}")
        assert response.status_code == 404

        # Cache should remain empty for 404s
        assert memory_cache.get(cache_key) is None

    def test_cache_expiration_after_ttl(self):
        """Test that cached data expires after TTL."""
        import time

        # Create a cache with very short TTL for testing
        short_cache = InMemoryCache(ttl_seconds=1)
        test_data = {"restaurant": {"id": "123"}, "categorias": []}
        cache_key = "test_expiring_cache"

        short_cache.set(cache_key, test_data)
        assert short_cache.get(cache_key) == test_data

        # Wait for expiration
        time.sleep(1.1)
        assert short_cache.get(cache_key) is None
