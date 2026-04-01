import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
sys.path.append(str(Path(__file__).resolve().parents[1]))

from auth_utils import get_password_hash


# Auth security playbook regression checks
def test_bcrypt_hash_uses_2b_prefix():
    hashed = get_password_hash("TEST_password_123")
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$")


# Auth login cookie hardening check
def test_auth_login_sets_http_only_cookie(api_client, base_url, auth_payload):
    response = api_client.post(f"{base_url}/api/auth/login", json=auth_payload, timeout=30)

    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    cookie_lower = set_cookie.lower()
    assert "httponly" in cookie_lower
    assert any(keyword in cookie_lower for keyword in ["access", "token", "session", "auth"])


# CORS credentials + explicit origin behavior check
def test_auth_cors_credentials_and_explicit_origin(api_client, base_url):
    frontend_origin = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
    if not frontend_origin:
        pytest.skip("REACT_APP_BACKEND_URL not set")

    response = api_client.options(
        f"{base_url}/api/auth/login",
        headers={
            "Origin": frontend_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
        timeout=30,
    )

    assert response.headers.get("access-control-allow-credentials") == "true"
    assert response.headers.get("access-control-allow-origin") == frontend_origin


# Brute force lockout behavior after repeated failures
def test_auth_lockout_after_five_failed_attempts(api_client, base_url):
    payload = {"email": "demo@arogyaai.app", "password": "WrongPass123!"}
    statuses = []

    for _ in range(6):
        response = api_client.post(f"{base_url}/api/auth/login", json=payload, timeout=30)
        statuses.append(response.status_code)

    assert statuses[-1] in [423, 429]
