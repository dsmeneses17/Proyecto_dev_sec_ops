from __future__ import annotations


def test_register_client_success(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "nombre_completo": "Juan Pérez",
            "usuario": "juanp",
            "email": "juan@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "Usuario registrado"
    assert body["rol"] == "cliente"
    assert "user_id" in body


def test_register_client_duplicate_username(client, make_user):
    make_user(usuario="existing", email="a@example.com")

    r = client.post(
        "/api/v1/auth/register",
        json={
            "nombre_completo": "Otro User",
            "usuario": "existing",
            "email": "b@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 400
    assert "ya existe" in r.json()["detail"].lower()


def test_register_client_duplicate_email(client, make_user):
    make_user(usuario="user1", email="dup@example.com")

    r = client.post(
        "/api/v1/auth/register",
        json={
            "nombre_completo": "Otro User",
            "usuario": "user2",
            "email": "dup@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 400
    assert "email" in r.json()["detail"].lower()


def test_register_client_missing_nombre_completo(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "usuario": "test",
            "email": "test@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 422


def test_register_client_invalid_email(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "nombre_completo": "Test",
            "usuario": "test",
            "email": "not-an-email",
            "password": "secret123",
        },
    )
    assert r.status_code == 422


def test_register_client_short_password(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "nombre_completo": "Test",
            "usuario": "test",
            "email": "test@example.com",
            "password": "12",
        },
    )
    assert r.status_code == 422


def test_register_client_short_username(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "nombre_completo": "Test",
            "usuario": "ab",
            "email": "test@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 422


def test_register_then_login(client):
    """Full RF02 flow: register → login → get token."""
    # Register
    r = client.post(
        "/api/v1/auth/register",
        json={
            "nombre_completo": "María López",
            "usuario": "marialopez",
            "email": "maria@example.com",
            "password": "Segura123",
        },
    )
    assert r.status_code == 200

    # Login with the new account
    r = client.post(
        "/api/v1/auth/login",
        json={"usuario": "marialopez", "password": "Segura123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["rol"] == "cliente"
    assert isinstance(body["access_token"], str)
