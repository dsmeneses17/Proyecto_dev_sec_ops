"""Utility for generating unique, URL-friendly slugs from restaurant names."""

from __future__ import annotations

import re
import unicodedata

from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant


def slugify(value: str) -> str:
    """Convert a string to a URL-friendly slug.

    1. NFD-normalise → strip accents.
    2. Lowercase.
    3. Replace non-alphanumeric chars with hyphens.
    4. Collapse consecutive hyphens and strip leading/trailing hyphens.
    """
    value = unicodedata.normalize("NFD", value)
    value = value.encode("ascii", "ignore").decode("ascii")  # strip accents
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def generate_unique_slug(db: Session, nombre: str, *, exclude_id=None) -> str:
    """Return a slug derived from *nombre* that is unique in the restaurants table.

    If ``mi-restaurante`` is taken, tries ``mi-restaurante-2``, ``-3``, etc.
    *exclude_id* can be set when updating a restaurant so that its own row
    doesn't count as a collision.
    """
    base = slugify(nombre)
    if not base:
        base = "restaurante"

    candidate = base
    counter = 2
    while True:
        query = db.query(Restaurant.id).filter(Restaurant.slug == candidate)
        if exclude_id is not None:
            query = query.filter(Restaurant.id != exclude_id)
        if query.first() is None:
            return candidate
        candidate = f"{base}-{counter}"
        counter += 1
