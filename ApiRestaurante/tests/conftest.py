from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db import Base

from fastapi.testclient import TestClient

from app.main import app
from app.deps import get_db
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish

from app.utils.security import hash_password


def _database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. These tests require Postgres because the models use Postgres-specific "
            "types (e.g., ARRAY). In CI, DATABASE_URL is provided by the workflow."
        )
    return url


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(_database_url(), pool_pre_ping=True)
    Base.metadata.create_all(bind=eng)
    return eng


@pytest.fixture()
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient with DB dependency overridden to use the pytest session."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            # session lifecycle is managed by the db_session fixture
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def make_user(db_session):
    def _make_user(
        *,
        usuario: str = "user",
        password: str = "password123",
        rol: str = "cliente",
        nombre_completo: str = "Test User",
        email: str | None = None,
        activo: bool = True,
    ) -> User:
        u = User(
            nombre_completo=nombre_completo,
            usuario=usuario,
            password=hash_password(password),
            rol=rol,
            activo=activo,
            email=email,
        )
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)
        return u

    return _make_user


@pytest.fixture()
def make_restaurant(db_session):
    def _make_restaurant(
        *,
        admin_id: int,
        nombre: str = "Proyecto materia",
        slug: str = "proyecto-materia",
        logo: str | None = None,
    ) -> Restaurant:
        r = Restaurant(admin_id=admin_id, nombre=nombre, slug=slug, logo=logo)
        db_session.add(r)
        db_session.commit()
        db_session.refresh(r)
        return r

    return _make_restaurant


@pytest.fixture()
def make_category(db_session):
    def _make_category(
        *,
        restaurante_id,
        nombre: str = "sopas",
        posicion: int = 1,
        activa: bool = True,
        descripcion: str | None = None,
    ) -> Category:
        c = Category(
            restaurante_id=restaurante_id,
            nombre=nombre,
            posicion=posicion,
            activa=activa,
            descripcion=descripcion,
        )
        db_session.add(c)
        db_session.commit()
        db_session.refresh(c)
        return c

    return _make_category


@pytest.fixture()
def make_dish(db_session):
    def _make_dish(
        *,
        categoria_id,
        nombre: str = "ajiaco",
        precio=10.0,
        disponible: bool = True,
        eliminado_en=None,
        posicion: int = 1,
    ) -> Dish:
        d = Dish(
            categoria_id=categoria_id,
            nombre=nombre,
            precio=precio,
            disponible=disponible,
            eliminado_en=eliminado_en,
            posicion=posicion,
        )
        db_session.add(d)
        db_session.commit()
        db_session.refresh(d)
        return d

    return _make_dish


@pytest.fixture(autouse=True)
def _clean_db(request):
    """Truncate DB tables after each test that actually uses the database.

    Tests that only rely on mocks (no ``db_session`` or ``client`` fixture)
    can add the ``@pytest.mark.no_db`` marker to skip the cleanup (and
    avoid requiring a live database connection altogether).
    """
    if "no_db" in {m.name for m in request.node.iter_markers()}:
        yield
        return
    eng = request.getfixturevalue("engine")
    yield
    # Keep tests isolated (FK-safe via CASCADE)
    with eng.begin() as conn:
        conn.execute(
            text(
                "\n".join(
                    [
                        'TRUNCATE TABLE dishes RESTART IDENTITY CASCADE;',
                        'TRUNCATE TABLE categories RESTART IDENTITY CASCADE;',
                        'TRUNCATE TABLE restaurants RESTART IDENTITY CASCADE;',
                        'TRUNCATE TABLE users RESTART IDENTITY CASCADE;',
                    ]
                )
            )
        )
