from __future__ import annotations


def test_public_menu_restaurants_contract(client, make_user, make_restaurant):
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    make_restaurant(admin_id=admin.id, slug="proyecto-materia", nombre="Proyecto materia")

    r = client.get("/api/v1/public/menu/restaurants")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first = data[0]
    assert "id" in first
    assert "nombre" in first
    assert "slug" in first


def test_public_menu_by_slug_contract(client, make_user, make_restaurant, make_category, make_dish):
    admin = make_user(usuario="admin", password="adminpass", rol="admin")
    restaurant = make_restaurant(admin_id=admin.id, slug="proyecto-materia", nombre="Proyecto materia")

    cat = make_category(restaurante_id=restaurant.id, nombre="sopas", posicion=1)
    make_dish(categoria_id=cat.id, nombre="ajiaco", precio=25.0, disponible=True, posicion=1)

    r = client.get("/api/v1/public/menu/proyecto-materia")
    assert r.status_code == 200

    payload = r.json()
    assert payload["restaurant"]["slug"] == "proyecto-materia"
    assert isinstance(payload.get("categorias"), list)
    assert len(payload["categorias"]) >= 1

    categorias = payload["categorias"]
    assert categorias[0]["nombre"]
    assert isinstance(categorias[0]["platos"], list)
    assert len(categorias[0]["platos"]) >= 1

    plato = categorias[0]["platos"][0]
    assert plato["nombre"].lower() == "ajiaco"
    assert "precio" in plato


def test_public_menu_unknown_slug_is_404(client):
    r = client.get("/api/v1/public/menu/no-existe")
    assert r.status_code == 404
    body = r.json()
    assert body.get("detail")
