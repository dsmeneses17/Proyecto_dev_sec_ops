import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Set it via your local .env file or GitHub Actions secrets/vars."
        )
    return url


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