from unittest.mock import Mock

import pytest

from app.services import auth_service


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


def test_authenticate_invalid_password(monkeypatch):
    db = Mock()
    user = Mock(password="hashed")

    monkeypatch.setattr(auth_service.users_repo, "get_by_username", lambda _db, _u: user)
    monkeypatch.setattr(auth_service, "verify_password", lambda _p, _h: False)

    with pytest.raises(auth_service.InvalidCredentials):
        auth_service.authenticate(db, usuario="u", password="bad")
