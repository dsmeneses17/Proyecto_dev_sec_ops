from unittest.mock import Mock

import pytest

from app.services import category_service


def test_create_category_raises_when_name_exists(monkeypatch):
    db = Mock()
    existing = [Mock(nombre="Entradas")]
    monkeypatch.setattr(category_service.categories_repo, "list_by_restaurant_id", lambda *_: existing)

    with pytest.raises(category_service.CategoryNameAlreadyExists):
        category_service.create_category(
            db,
            category_service.CreateCategoryInput(
                restaurante_id="rid",
                nombre="entradas",
                posicion=1,
            ),
        )


def test_create_category_calls_repo_create(monkeypatch):
    db = Mock()
    monkeypatch.setattr(category_service.categories_repo, "list_by_restaurant_id", lambda *_: [])

    created = Mock(nombre="Postres")

    def _create(_db, **kwargs):
        assert kwargs["nombre"] == "Postres"
        assert kwargs["posicion"] == 1
        return created

    monkeypatch.setattr(category_service.categories_repo, "create", _create)

    result = category_service.create_category(
        db,
        category_service.CreateCategoryInput(
            restaurante_id="rid",
            nombre="Postres",
            posicion=1,
        ),
    )
    assert result is created
