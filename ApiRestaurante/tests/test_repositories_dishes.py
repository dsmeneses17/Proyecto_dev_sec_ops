from decimal import Decimal

from app.models.category import Category
from app.models.dish import Dish
from app.models.restaurant import Restaurant
from app.repositories import dishes as dishes_repo
from app.repositories import users as users_repo
from app.utils.security import hash_password


def _category(db_session):
    admin = users_repo.create(
        db_session,
        nombre_completo="Admin",
        usuario="admin_dish",
        password_hash=hash_password("secret"),
        rol="admin",
    )
    restaurant = Restaurant(nombre="R", slug="r-dish", admin_id=admin.id)
    db_session.add(restaurant)
    db_session.commit()
    db_session.refresh(restaurant)

    category = Category(restaurante_id=restaurant.id, nombre="Platos", posicion=1, activa=True)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def test_dishes_create_and_list_by_category(db_session):
    category = _category(db_session)

    d1 = dishes_repo.create(
        db_session,
        categoria_id=category.id,
        nombre="Hamburguesa",
        precio=Decimal("20.00"),
        posicion=2,
    )
    d2 = dishes_repo.create(
        db_session,
        categoria_id=category.id,
        nombre="Pizza",
        precio=Decimal("30.00"),
        posicion=1,
    )

    dishes = dishes_repo.list_by_category_id(db_session, category.id)
    assert [d.nombre for d in dishes] == ["Pizza", "Hamburguesa"]
    assert {d.id for d in dishes} == {d1.id, d2.id}


def test_dishes_get_by_id(db_session):
    category = _category(db_session)
    dish = Dish(categoria_id=category.id, nombre="Sopa", precio=Decimal("10.00"), disponible=True)
    db_session.add(dish)
    db_session.commit()

    fetched = dishes_repo.get_by_id(db_session, dish.id)
    assert fetched is not None
    assert fetched.nombre == "Sopa"
