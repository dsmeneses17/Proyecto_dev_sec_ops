"""Tests for app.utils.slug — pure slugify + DB-aware unique slug generation."""

from unittest.mock import MagicMock

import pytest

from app.utils.slug import generate_unique_slug, slugify

pytestmark = pytest.mark.no_db


# ── slugify (pure function, no DB) ──────────────────────────────────────────


class TestSlugify:
    def test_basic(self):
        assert slugify("Mi Restaurante") == "mi-restaurante"

    def test_accents(self):
        assert slugify("Café Córdoba Ñoño") == "cafe-cordoba-nono"

    def test_special_chars(self):
        assert slugify("Hello!!! @World#123") == "hello-world-123"

    def test_consecutive_hyphens(self):
        assert slugify("a --- b") == "a-b"

    def test_leading_trailing(self):
        assert slugify("  --Hola--  ") == "hola"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_only_special_chars(self):
        assert slugify("!!!@@@###") == ""

    def test_numbers(self):
        assert slugify("Restaurante 2026") == "restaurante-2026"

    def test_unicode_emoji(self):
        # Emojis should be stripped
        assert slugify("🍕 Pizza Place") == "pizza-place"


# ── generate_unique_slug (needs DB mock) ────────────────────────────────────


class TestGenerateUniqueSlug:
    def _mock_db(self, existing_slugs: set[str]):
        """Return a mock DB session that 'finds' rows for slugs in the set."""
        db = MagicMock()

        def _query_chain(*_args, **_kwargs):
            chain = MagicMock()

            def _filter(*filter_args, **_kw):
                inner = MagicMock()

                def _first():
                    # Extract the slug being compared from the binary expression
                    for arg in filter_args:
                        # arg is a BinaryExpression; right side is the value
                        try:
                            val = arg.right.effective_value
                        except AttributeError:
                            continue
                        return object() if val in existing_slugs else None
                    return None

                inner.first = _first
                inner.filter = _filter  # allow chaining
                return inner

            chain.filter = _filter
            return chain

        db.query = _query_chain
        return db

    def test_slug_generated_from_name(self):
        db = self._mock_db(set())  # nothing exists
        result = generate_unique_slug(db, "Mi Restaurante")
        assert result == "mi-restaurante"

    def test_slug_appends_suffix_on_collision(self):
        db = self._mock_db({"mi-restaurante"})
        result = generate_unique_slug(db, "Mi Restaurante")
        assert result == "mi-restaurante-2"

    def test_slug_increments_until_free(self):
        db = self._mock_db({"pizza", "pizza-2", "pizza-3"})
        result = generate_unique_slug(db, "Pizza")
        assert result == "pizza-4"

    def test_empty_name_defaults_to_restaurante(self):
        db = self._mock_db(set())
        result = generate_unique_slug(db, "")
        assert result == "restaurante"

    def test_accented_name(self):
        db = self._mock_db(set())
        result = generate_unique_slug(db, "Café París")
        assert result == "cafe-paris"
