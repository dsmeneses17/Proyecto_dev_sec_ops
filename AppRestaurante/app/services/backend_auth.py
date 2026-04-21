import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token

from app.core.config import settings


logger = logging.getLogger(__name__)

_TOKEN_CACHE: Dict[str, Any] = {"token": None, "expires_at": 0.0}


def _sanitize_token(token: str) -> str:
    return token.strip().strip("\"").strip("'")


def _backend_audience() -> str:
    parsed = urlparse(settings.BACKEND_URL)
    if not parsed.scheme or not parsed.netloc:
        return settings.BACKEND_URL.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}"


def _get_backend_id_token() -> Optional[str]:
    now = time.time()
    token = _TOKEN_CACHE.get("token")
    expires_at = float(_TOKEN_CACHE.get("expires_at") or 0.0)
    if token and now < expires_at:
        return str(token)

    audience = _backend_audience()
    try:
        fresh = id_token.fetch_id_token(GoogleAuthRequest(), audience)
        _TOKEN_CACHE["token"] = fresh
        _TOKEN_CACHE["expires_at"] = now + 50 * 60
        return fresh
    except Exception as exc:
        logger.warning("Could not fetch backend IAM token for audience=%s: %s", audience, exc)
        return None


def build_backend_headers(user_token: Optional[str] = None, content_type_json: bool = False) -> Dict[str, str]:
    headers: Dict[str, str] = {}

    backend_token = _get_backend_id_token()
    if backend_token:
        # Cloud Run IAM auth while preserving app-level Authorization header for user JWT.
        headers["X-Serverless-Authorization"] = f"Bearer {backend_token}"

    if user_token:
        headers["Authorization"] = f"Bearer {_sanitize_token(user_token)}"

    if content_type_json:
        headers["Content-Type"] = "application/json"

    return headers


def request_backend(method: str, url: str, *, user_token: Optional[str] = None, timeout: int = 10, **kwargs):
    headers = kwargs.pop("headers", {}) or {}
    merged = {**build_backend_headers(user_token=user_token), **headers}
    return requests.request(method=method, url=url, headers=merged, timeout=timeout, **kwargs)
