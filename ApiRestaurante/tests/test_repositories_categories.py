from app.models.category import Category
from app.models.restaurant import Restaurant
from app.repositories import categories as categories_repo
from app.repositories import users as users_repo
from app.utils.security import hash_password


def _admin_and_restaurant(db_session):
    admin = users_repo.create(
        db_session,
        nombre_completo="Admin",
        usuario="admin_cat",
        password_hash=hash_password("secret"),
        rol="admin",
    )
    restaurant = Restaurant(nombre="R", slug="r-cat", admin_id=admin.id)
    db_session.add(restaurant)
    db_session.commit()
    db_session.refresh(restaurant)
    return admin, restaurant


def test_categories_create_and_list_by_restaurant(db_session):
    _admin, restaurant = _admin_and_restaurant(db_session)

    c2 = categories_repo.create(
        db_session,
        restaurante_id=restaurant.id,
        nombre="Bebidas",
        posicion=2,
    )
    c1 = categories_repo.create(
        db_session,
        restaurante_id=restaurant.id,
        nombre="Entradas",
        posicion=1,
    )

    cats = categories_repo.list_by_restaurant_id(db_session, restaurant.id)
    assert [c.nombre for c in cats] == ["Entradas", "Bebidas"]
    assert {c.id for c in cats} == {c1.id, c2.id}


def test_categories_get_by_id(db_session):
    _admin, restaurant = _admin_and_restaurant(db_session)
    cat = Category(restaurante_id=restaurant.id, nombre="Postres", posicion=1, activa=True)
    db_session.add(cat)
    db_session.commit()

    fetched = categories_repo.get_by_id(db_session, cat.id)
    assert fetched is not None
    assert fetched.nombre == "Postres"
