import os

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if not url:
        pytest.skip("REACT_APP_BACKEND_URL is not set")
    return url.rstrip("/")


@pytest.fixture(scope="session")
def api_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def auth_payload() -> dict:
    return {
        "email": "demo@arogyaai.app",
        "password": "Arogya123!",
    }


@pytest.fixture(scope="session")
def auth_token(api_client: requests.Session, base_url: str, auth_payload: dict) -> str:
    response = api_client.post(f"{base_url}/api/auth/login", json=auth_payload, timeout=30)
    if response.status_code != 200:
        pytest.skip(f"Auth login failed: {response.status_code} {response.text}")

    data = response.json()
    token = data.get("token")
    if not token:
        pytest.skip("Auth token missing in login response")
    return token


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}
