"""Model for tracking public menu visualizations (RF22 / CU-08)."""

import hashlib
import uuid

from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from app.db import Base


def _hash_ip(ip: str | None) -> str | None:
    """Return a SHA-256 hex-digest of an IP address (anonymisation)."""
    if not ip:
        return None
    return hashlib.sha256(ip.encode()).hexdigest()


class MenuView(Base):
    __tablename__ = "menu_views"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(pgUUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(120), nullable=False, index=True)

    # Where the view came from: "menu", "qr", "direct"
    source = Column(String(20), nullable=False, default="menu")

    # Optional metadata
    user_agent = Column(String(512), nullable=True)
    ip_hash = Column(String(64), nullable=True)  # SHA-256 of the real IP (anonymised)
    referrer = Column(String(512), nullable=True)  # HTTP Referer header

    viewed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)
