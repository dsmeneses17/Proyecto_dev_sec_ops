from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cambia usuario, contraseña, host, puerto y nombre_db según tu configuración
DATABASE_URL = "postgresql+psycopg2://postgres:1234@postgres_db:5432/Restaurante"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()