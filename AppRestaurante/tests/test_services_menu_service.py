from __future__ import annotations

from types import SimpleNamespace

from app.services import menu_service


class _FakeResponse:
    def __init__(self, status_code: int, json_data=None):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data


def test_list_public_restaurants_returns_list(monkeypatch):
    monkeypatch.setattr(
        menu_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    monkeypatch.setattr(
        menu_service.requests,
        "get",
        lambda url, timeout=10: _FakeResponse(200, [{"slug": "a", "nombre": "A"}]),
    )

    data = menu_service.list_public_restaurants()
    assert isinstance(data, list)
    assert data[0]["slug"] == "a"


def test_list_public_restaurants_handles_non_200(monkeypatch):
    monkeypatch.setattr(
        menu_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    monkeypatch.setattr(
        menu_service.requests,
        "get",
        lambda *_args, **_kwargs: _FakeResponse(500, {"detail": "boom"}),
    )

    assert menu_service.list_public_restaurants() == []


def test_get_public_menu_non_200_returns_none(monkeypatch):
    monkeypatch.setattr(
        menu_service,
        "settings",
        SimpleNamespace(BACKEND_URL="http://backend/api/v1/"),
    )

    monkeypatch.setattr(
        menu_service.requests,
        "get",
        lambda *_args, **_kwargs: _FakeResponse(404, {"detail": "not found"}),
    )

    assert menu_service.get_public_menu("missing") is None
