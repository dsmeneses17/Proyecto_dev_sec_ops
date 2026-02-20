from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    usuario = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    rol = Column(String, nullable=False, default="cliente")
    activo = Column(Boolean, default=True)
    email = Column(String, unique=True, nullable=True)
    restaurants = relationship("Restaurant", back_populates="admin")
