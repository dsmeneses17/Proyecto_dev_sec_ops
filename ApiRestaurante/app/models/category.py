from sqlalchemy import Column, String, Text, Boolean, Integer, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from app.db import Base
import uuid

class Category(Base):
    __tablename__ = "categories"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurante_id = Column(pgUUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)

    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    posicion = Column(Integer, nullable=False)
    activa = Column(Boolean, nullable=False, default=True)

    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())
    actualizado_en = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    restaurante = relationship("Restaurant", back_populates="categorias")
    dishes = relationship("Dish", back_populates="categoria", cascade="all, delete-orphan")
