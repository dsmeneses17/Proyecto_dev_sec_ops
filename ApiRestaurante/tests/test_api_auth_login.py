from __future__ import annotations


def test_auth_login_success_returns_token(client, make_user):
    make_user(usuario="bob", password="secret123", rol="cliente")

    r = client.post("/api/v1/auth/login", json={"usuario": "bob", "password": "secret123"})
    assert r.status_code == 200
    body = r.json()

    assert body.get("token_type") == "bearer"
    assert isinstance(body.get("access_token"), str)
    assert body.get("rol") == "cliente"


def test_auth_login_unknown_user_is_404(client):
    r = client.post("/api/v1/auth/login", json={"usuario": "nope", "password": "x"})
    assert r.status_code == 404


def test_auth_login_wrong_password_is_401(client, make_user):
    make_user(usuario="bob", password="secret123", rol="cliente")

    r = client.post("/api/v1/auth/login", json={"usuario": "bob", "password": "wrong"})
    assert r.status_code == 401
