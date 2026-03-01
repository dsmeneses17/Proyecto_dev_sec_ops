from unittest.mock import Mock

import pytest

from app.services import auth_service

pytestmark = pytest.mark.no_db  # These tests use mocks only — no DB needed


def test_register_user_raises_when_username_exists(monkeypatch):
    db = Mock()
    monkeypatch.setattr(
        auth_service.users_repo,
        "get_by_username",
        lambda _db, _u: object(),
    )

    with pytest.raises(auth_service.UsernameAlreadyExists):
        auth_service.register_user(
            db,
            auth_service.RegisterUserInput(
                nombre_completo="X",
                usuario="taken",
                password="pw",
            ),
        )


def test_register_user_raises_when_email_exists(monkeypatch):
    db = Mock()
    monkeypatch.setattr(
        auth_service.users_repo,
        "get_by_username",
        lambda _db, _u: None,
    )
    monkeypatch.setattr(
        auth_service.users_repo,
        "get_by_email",
        lambda _db, _e: object(),  # simulate existing email
    )

    with pytest.raises(auth_service.EmailAlreadyExists):
        auth_service.register_user(
            db,
            auth_service.RegisterUserInput(
                nombre_completo="X",
                usuario="new_user",
                password="pw",
                email="taken@example.com",
            ),
        )


def test_register_user_success_calls_repo(monkeypatch):
    db = Mock()
    monkeypatch.setattr(auth_service.users_repo, "get_by_username", lambda _db, _u: None)
    monkeypatch.setattr(auth_service.users_repo, "get_by_email", lambda _db, _e: None)

    created = Mock(id=1, usuario="new_user")

    def _create(_db, **kwargs):
        assert kwargs["nombre_completo"] == "Test User"
        assert kwargs["usuario"] == "new_user"
        assert kwargs["email"] == "test@example.com"
        assert kwargs["rol"] == "cliente"
        assert kwargs["password_hash"]  # should be hashed
        return created

    monkeypatch.setattr(auth_service.users_repo, "create", _create)

    result = auth_service.register_user(
        db,
        auth_service.RegisterUserInput(
            nombre_completo="Test User",
            usuario="new_user",
            password="secret",
            email="test@example.com",
            rol="cliente",
        ),
    )
    assert result is created


def test_authenticate_invalid_password(monkeypatch):
    db = Mock()
    user = Mock(password="hashed")

    monkeypatch.setattr(auth_service.users_repo, "get_by_username", lambda _db, _u: user)
    monkeypatch.setattr(auth_service, "verify_password", lambda _p, _h: False)

    with pytest.raises(auth_service.InvalidCredentials):
        auth_service.authenticate(db, usuario="u", password="bad")
