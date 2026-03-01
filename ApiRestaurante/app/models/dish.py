import uuid

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship

from app.db import Base


class Dish(Base):
    __tablename__ = "dishes"   # en minúsculas y plural

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    categoria_id = Column(pgUUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    precio_oferta = Column(Numeric(10, 2), nullable=True)
    imagen_url = Column(String, nullable=True)

    disponible = Column(Boolean, nullable=False, default=True)
    destacado = Column(Boolean, nullable=False, default=False)
    etiquetas = Column(ARRAY(String), nullable=True)
    posicion = Column(Integer, nullable=True)

    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())
    actualizado_en = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    eliminado_en = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relación inversa con Category
    categoria = relationship("Category", back_populates="dishes")
