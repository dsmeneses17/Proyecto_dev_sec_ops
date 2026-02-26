from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db import Base


def _database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:1234@localhost:5432/Restaurante_test",
    )


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


@pytest.fixture(autouse=True)
def _clean_db(engine):
    yield
    # Keep tests isolated (FK-safe via CASCADE)
    with engine.begin() as conn:
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
