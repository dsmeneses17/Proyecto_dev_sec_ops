from __future__ import annotations

from types import SimpleNamespace

import requests

from app.services import auth_service


class _FakeResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = {"content-type": "application/json"}

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data
        return self._json_data


def test_autenticar_usuario_success(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    def _post(url, json):
        assert url == "http://backend/api/v1/auth/login"
        assert json == {"usuario": "u", "password": "p"}
        return _FakeResponse(
            200,
            {
                "access_token": " token ",
                "rol": "admin",
                "user_id": 1,
                "restaurant_id": 2,
                "restaurant_slug": "slug",
            },
        )

    monkeypatch.setattr(auth_service.requests, "post", _post)

    data = auth_service.autenticar_usuario("u", "p")
    assert data["token"] == "token"
    assert data["rol"] == "admin"
    assert data["user_id"] == 1
    assert data["restaurant_id"] == 2
    assert data["restaurant_slug"] == "slug"


def test_autenticar_usuario_invalid_credentials(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    monkeypatch.setattr(
        auth_service.requests,
        "post",
        lambda *_args, **_kwargs: _FakeResponse(401, {"detail": "bad"}, text="bad"),
    )

    data = auth_service.autenticar_usuario("u", "bad")
    assert data == {"error": "Credenciales inválidas"}


def test_register_owner_with_restaurant_backend_error_detail(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    monkeypatch.setattr(
        auth_service.requests,
        "post",
        lambda *_args, **_kwargs: _FakeResponse(400, {"detail": "no"}, text="no"),
    )

    resp = auth_service.register_owner_with_restaurant({"x": 1})
    assert resp == {"error": "no"}


def test_register_owner_with_restaurant_connection_error(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    def _raise(*_a, **_k):
        raise requests.exceptions.ConnectionError("down")

    monkeypatch.setattr(auth_service.requests, "post", _raise)

    resp = auth_service.register_owner_with_restaurant({"x": 1})
    assert resp == {"error": "No se pudo conectar al servidor"}


# ---------- register_client ----------


def test_register_client_success(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    def _post(url, json, timeout=15):
        assert url == "http://backend/api/v1/auth/register"
        assert json["nombre_completo"] == "Juan"
        assert json["usuario"] == "juanp"
        assert json["email"] == "juan@x.com"
        assert json["rol"] == "cliente"
        return _FakeResponse(200, {"message": "Usuario registrado", "user_id": "1", "rol": "cliente"})

    monkeypatch.setattr(auth_service.requests, "post", _post)

    data = auth_service.register_client(
        nombre_completo="Juan",
        usuario="juanp",
        email="juan@x.com",
        password="secret",
    )
    assert data["message"] == "Usuario registrado"


def test_register_client_duplicate_returns_error(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    monkeypatch.setattr(
        auth_service.requests,
        "post",
        lambda *_a, **_k: _FakeResponse(400, {"detail": "Usuario ya existe"}, text="Usuario ya existe"),
    )

    data = auth_service.register_client(
        nombre_completo="X",
        usuario="dup",
        email="dup@x.com",
        password="secret",
    )
    assert data == {"error": "Usuario ya existe"}


def test_register_client_validation_422(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    monkeypatch.setattr(
        auth_service.requests,
        "post",
        lambda *_a, **_k: _FakeResponse(
            422,
            {"detail": [{"msg": "Value error, La contraseña debe tener al menos 6 caracteres"}]},
            text="validation error",
        ),
    )

    data = auth_service.register_client(
        nombre_completo="X",
        usuario="user",
        email="x@x.com",
        password="12",
    )
    assert "error" in data
    assert "contraseña" in data["error"].lower() or "6 caracteres" in data["error"].lower()


def test_register_client_connection_error(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    def _raise(*_a, **_k):
        raise requests.exceptions.ConnectionError("down")

    monkeypatch.setattr(auth_service.requests, "post", _raise)

    data = auth_service.register_client(
        nombre_completo="X",
        usuario="user",
        email="x@x.com",
        password="secret",
    )
    assert data == {"error": "No se pudo conectar al servidor"}
