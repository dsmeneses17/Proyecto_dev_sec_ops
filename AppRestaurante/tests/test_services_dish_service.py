from __future__ import annotations

from app.services import dish_service


class _FakeResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        return self._json_data


def test_get_headers_strips_quotes():
    h = dish_service.get_headers(' "tok" ')
    assert h["Authorization"] == "Bearer tok"


def test_create_dish_returns_error_on_500(monkeypatch):
    monkeypatch.setattr(
        dish_service.requests,
        "post",
        lambda *_a, **_k: _FakeResponse(500, text="boom"),
    )

    resp = dish_service.create_dish("t", {"x": 1})
    assert resp["error"] is True
    assert resp["status_code"] == 500


def test_toggle_availability_non_200(monkeypatch):
    monkeypatch.setattr(
        dish_service.requests,
        "patch",
        lambda *_a, **_k: _FakeResponse(404, text="no"),
    )

    resp = dish_service.toggle_availability("t", "1")
    assert resp["error"] is True
    assert resp["status_code"] == 404
