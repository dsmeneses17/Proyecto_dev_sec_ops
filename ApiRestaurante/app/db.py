import os
from urllib.parse import quote

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    cloud_sql_connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")

    if db_user and db_password and db_name and cloud_sql_connection_name:
        # Secret-rotated passwords can contain reserved URL chars; encode credentials before building DSN.
        encoded_user = quote(db_user, safe="")
        encoded_password = quote(db_password, safe="")
        return (
            f"postgresql+psycopg2://{encoded_user}:{encoded_password}@/{db_name}"
            f"?host=/cloudsql/{cloud_sql_connection_name}"
        )

    raise RuntimeError(
        "DATABASE_URL is not set. Configure DATABASE_URL directly or provide DB_USER, DB_PASSWORD, "
        "DB_NAME and CLOUD_SQL_CONNECTION_NAME."
    )


def _build_engine():
    return create_engine(_get_database_url())


def _build_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=_build_engine())


class _LazyEngine:
    """Proxy that creates the real engine on first use, so importing db.py
    without DATABASE_URL set doesn't crash (useful for unit tests that mock
    the DB layer)."""

    _real = None

    def __getattr__(self, name):
        if _LazyEngine._real is None:
            _LazyEngine._real = _build_engine()
        return getattr(_LazyEngine._real, name)


class _LazySessionLocal:
    _real = None

    def __call__(self, **kw):
        if _LazySessionLocal._real is None:
            _LazySessionLocal._real = _build_session_factory()
        return _LazySessionLocal._real(**kw)

    def __getattr__(self, name):
        if _LazySessionLocal._real is None:
            _LazySessionLocal._real = _build_session_factory()
        return getattr(_LazySessionLocal._real, name)


engine = _LazyEngine()
SessionLocal = _LazySessionLocal()

Base = declarative_base()
