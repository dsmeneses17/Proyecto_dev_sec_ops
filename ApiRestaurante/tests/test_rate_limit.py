"""
RNF-04 – Rate Limiting: 100 requests/minute per IP.

Tests verify that:
 - Normal requests succeed (HTTP 200).
 - After the limit is exhausted the server responds with HTTP 429.

We temporarily patch the rate to "5/minute" so the test finishes quickly.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from limits import parse as parse_rate_limit

import app.main as _mod


@pytest.fixture(autouse=True)
def _low_rate_limit():
    """Temporarily lower the rate limit and clear storage between tests."""
    original_rate = _mod._rate
    _mod._rate = parse_rate_limit("5/minute")
    _mod._storage.reset()
    yield
    _mod._rate = original_rate
    _mod._storage.reset()


@pytest.fixture()
def rate_client():
    with TestClient(_mod.app) as c:
        yield c


def test_requests_within_limit_succeed(rate_client: TestClient):
    """First 5 requests should succeed."""
    for _ in range(5):
        resp = rate_client.get("/")
        assert resp.status_code == 200


def test_request_exceeding_limit_returns_429(rate_client: TestClient):
    """The 6th request should be rate-limited (429)."""
    for _ in range(5):
        rate_client.get("/")

    resp = rate_client.get("/")
    assert resp.status_code == 429


def test_429_body_contains_error_message(rate_client: TestClient):
    """The 429 response body should contain a rate-limit error message."""
    for _ in range(6):
        resp = rate_client.get("/")

    assert resp.status_code == 429
    body = resp.json()
    assert "error" in body
    assert "Rate limit exceeded" in body["error"]
