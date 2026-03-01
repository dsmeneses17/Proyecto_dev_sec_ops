"""API contract tests for category reordering (RF08)."""


def test_reorder_categories_success(client, make_user, make_restaurant, make_category, db_session):
    """Reorder categories by updating their posición."""
    admin = make_user(usuario="admin_reorder", rol="admin")
    restaurant = make_restaurant(admin_id=admin.id)

    cat1 = make_category(
        restaurante_id=restaurant.id,
        nombre="Cat 1",
        posicion=1
    )
    cat2 = make_category(
        restaurante_id=restaurant.id,
        nombre="Cat 2",
        posicion=2
    )
    cat3 = make_category(
        restaurante_id=restaurant.id,
        nombre="Cat 3",
        posicion=3
    )

    # Login as admin
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"usuario": admin.usuario, "password": "password123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Reorder: swap positions of cat1 and cat3
    resp = client.patch(
        "/api/v1/admin/categories/reorder",
        json={
            "categorias": [
                {"id": str(cat1.id), "posicion": 3},
                {"id": str(cat2.id), "posicion": 2},
                {"id": str(cat3.id), "posicion": 1},
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Categorías reordenadas exitosamente"

    # Verify the changes in the database
    updated_cat1 = db_session.query(type(cat1)).filter(type(cat1).id == cat1.id).first()
    updated_cat3 = db_session.query(type(cat3)).filter(type(cat3).id == cat3.id).first()

    assert updated_cat1.posicion == 3
    assert updated_cat3.posicion == 1


def test_reorder_categories_invalid_id(client, make_user, make_restaurant, make_category):
    """Reorder with non-existent category ID returns 404."""
    admin = make_user(usuario="admin_bad", rol="admin")
    restaurant = make_restaurant(admin_id=admin.id)
    make_category(restaurante_id=restaurant.id, nombre="Cat", posicion=1)

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"usuario": admin.usuario, "password": "password123"}
    )
    token = login_resp.json()["access_token"]

    # Try to reorder with invalid ID
    resp = client.patch(
        "/api/v1/admin/categories/reorder",
        json={
            "categorias": [
                {"id": "00000000-0000-0000-0000-000000000000", "posicion": 1},
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


def test_reorder_categories_missing_posicion(client, make_user, make_restaurant, make_category):
    """Reorder with missing posición field returns 400."""
    admin = make_user(usuario="admin_missing", rol="admin")
    restaurant = make_restaurant(admin_id=admin.id)
    cat = make_category(restaurante_id=restaurant.id, nombre="Cat", posicion=1)

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"usuario": admin.usuario, "password": "password123"}
    )
    token = login_resp.json()["access_token"]

    # Try to reorder with missing posición
    resp = client.patch(
        "/api/v1/admin/categories/reorder",
        json={
            "categorias": [
                {"id": str(cat.id)},  # Missing posición
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 400


def test_reorder_categories_unauthorized_non_admin(client, make_user, make_restaurant, make_category):
    """Non-admin user cannot reorder categories (403)."""
    admin = make_user(usuario="admin_for_rest", rol="admin")
    restaurant = make_restaurant(admin_id=admin.id)
    cat = make_category(restaurante_id=restaurant.id, nombre="Cat", posicion=1)

    # Create a non-admin user
    client_user = make_user(usuario="regular_user", rol="cliente")

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"usuario": client_user.usuario, "password": "password123"}
    )
    token = login_resp.json()["access_token"]

    # Try to reorder categories as non-admin
    resp = client.patch(
        "/api/v1/admin/categories/reorder",
        json={
            "categorias": [
                {"id": str(cat.id), "posicion": 1},
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403
