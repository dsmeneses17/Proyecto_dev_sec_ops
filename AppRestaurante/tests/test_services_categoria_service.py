from __future__ import annotations

from app.services import categoria_service


class _FakeResponse:
    def __init__(self, status_code: int, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = {"content-type": "application/json"}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            # mimic requests raising
            import requests

            raise requests.exceptions.HTTPError(response=self)


def test_get_headers_strips_quotes_and_spaces():
    h = categoria_service.get_headers(" 'abc' ")
    assert h["Authorization"] == "Bearer abc"


def test_list_categorias_non_200_returns_error(monkeypatch):
    monkeypatch.setattr(
        categoria_service.requests,
        "get",
        lambda *_a, **_k: _FakeResponse(401, {"detail": "bad"}, text="bad"),
    )

    resp = categoria_service.list_categorias("token")
    assert resp["error"] is True
    assert resp["status_code"] == 401


def test_create_categoria_http_401_message(monkeypatch):
    def _post(*_a, **_k):
        return _FakeResponse(401, {"detail": "bad"}, text="bad")

    monkeypatch.setattr(categoria_service.requests, "post", _post)

    resp = categoria_service.create_categoria("token", {"nombre": "X"})
    assert resp["error"] is True
    assert resp["status_code"] == 401
    assert "Token inválido" in resp["detalle"]
