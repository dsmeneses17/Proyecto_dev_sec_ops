from app.repositories import users as users_repo

from app.utils.security import hash_password


def test_users_create_and_get_by_username(db_session):
    created = users_repo.create(
        db_session,
        nombre_completo="Test User",
        usuario="testuser",
        password_hash=hash_password("secret"),
        rol="cliente",
    )

    fetched = users_repo.get_by_username(db_session, "testuser")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.usuario == "testuser"


def test_users_get_by_email(db_session):
    users_repo.create(
        db_session,
        nombre_completo="Email User",
        usuario="emailuser",
        password_hash=hash_password("secret"),
        rol="cliente",
        email="Test@Example.com",
    )

    # Case-insensitive lookup
    fetched = users_repo.get_by_email(db_session, "test@example.com")
    assert fetched is not None
    assert fetched.usuario == "emailuser"


def test_users_get_by_email_not_found(db_session):
    fetched = users_repo.get_by_email(db_session, "nope@example.com")
    assert fetched is None
