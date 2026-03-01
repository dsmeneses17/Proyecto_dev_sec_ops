import uuid

from sqlalchemy import JSON, TIMESTAMP, Column, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship

from app.db import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    logo = Column(String, nullable=True)  # URL
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    horarios = Column(JSON, nullable=True)
    qr_color_fg = Column(String(7), default="#000000", nullable=False)  # QR foreground color (hex)
    qr_color_bg = Column(String(7), default="#FFFFFF", nullable=False)  # QR background color (hex)
    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())
    actualizado_en = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    admin_id = Column(Integer, ForeignKey("users.id"))
    admin = relationship("User", back_populates="restaurants")
    categorias = relationship("Category", back_populates="restaurante", cascade="all, delete-orphan")
