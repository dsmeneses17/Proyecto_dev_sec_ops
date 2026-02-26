from app.models.restaurant import Restaurant
from app.repositories import restaurants as restaurants_repo
from app.repositories import users as users_repo
from app.utils.security import hash_password


def test_restaurants_list_slugs(db_session):
    admin = users_repo.create(
        db_session,
        nombre_completo="Admin",
        usuario="admin1",
        password_hash=hash_password("secret"),
        rol="admin",
    )

    r1 = Restaurant(nombre="R1", slug="r1", admin_id=admin.id)
    r2 = Restaurant(nombre="R2", slug="r2", admin_id=admin.id)
    db_session.add_all([r2, r1])
    db_session.commit()

    assert restaurants_repo.list_slugs(db_session) == ["r1", "r2"]


def test_restaurants_get_by_slug(db_session):
    admin = users_repo.create(
        db_session,
        nombre_completo="Admin",
        usuario="admin2",
        password_hash=hash_password("secret"),
        rol="admin",
    )
    r = Restaurant(nombre="R", slug="sluggy", admin_id=admin.id)
    db_session.add(r)
    db_session.commit()

    fetched = restaurants_repo.get_by_slug(db_session, "sluggy")
    assert fetched is not None
    assert fetched.slug == "sluggy"
