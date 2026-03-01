"""Model for tracking public menu visualizations (RF22)."""

from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from app.db import Base
import uuid


class MenuView(Base):
    __tablename__ = "menu_views"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(pgUUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(120), nullable=False, index=True)

    # Where the view came from: "menu", "qr", "direct"
    source = Column(String(20), nullable=False, default="menu")

    # Optional metadata
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)  # supports IPv6

    viewed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)
