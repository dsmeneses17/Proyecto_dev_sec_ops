from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant


def get_by_slug(db: Session, slug: str) -> Optional[Restaurant]:
    return db.query(Restaurant).filter(Restaurant.slug == slug).first()


def list_slugs(db: Session) -> list[str]:
    rows: list[tuple[str]] = db.query(Restaurant.slug).order_by(Restaurant.slug.asc()).all()
    return [r[0] for r in rows]
