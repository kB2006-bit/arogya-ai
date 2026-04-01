import uuid


# Auth module and protected-route API regression coverage
def test_auth_login_success_structure(api_client, base_url, auth_payload):
    response = api_client.post(f"{base_url}/api/auth/login", json=auth_payload, timeout=30)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("token"), str) and len(data["token"]) > 10
    assert data["user"]["email"] == auth_payload["email"]
    assert isinstance(data["user"].get("id"), str)


def test_auth_me_returns_logged_in_user(api_client, base_url, auth_headers, auth_payload):
    response = api_client.get(f"{base_url}/api/auth/me", headers=auth_headers, timeout=30)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == auth_payload["email"]
    assert isinstance(data["id"], str)
    assert data["language"] in ["en", "hi"]


# Dashboard module and persistence-linked summary checks
def test_dashboard_returns_expected_shape(api_client, base_url, auth_headers):
    response = api_client.get(f"{base_url}/api/dashboard", headers=auth_headers, timeout=30)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["total_checks"], int)
    assert isinstance(data["recent_checks"], list)
    assert set(["low_alerts", "medium_alerts", "high_alerts"]).issubset(data.keys())


# Dashboard embedded chat module mock-response contract checks
def test_analyze_symptoms_mock_response_shape(api_client, base_url, auth_headers):
    response = api_client.post(
        f"{base_url}/api/analyze-symptoms",
        headers=auth_headers,
        json={"message": "I have sore throat and mild fever"},
        timeout=30,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("response"), str) and len(data["response"]) > 0
    assert data.get("severity") in ["Low", "Medium", "High"]


# Symptom-checker module and emergency severity response checks
def test_symptom_checker_returns_assessment_and_persists(api_client, base_url, auth_headers):
    message = f"I have chest pain and breathing difficulty since 1 hour {uuid.uuid4()}"
    create_response = api_client.post(
        f"{base_url}/api/symptom-checker",
        headers=auth_headers,
        json={
            "message": message,
            "language": "en",
            "history": [],
        },
        timeout=60,
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["severity"] in ["Low", "Medium", "High"]
    assert isinstance(created["diagnosis"], str) and len(created["diagnosis"]) > 0
    assert isinstance(created["next_steps"], list) and len(created["next_steps"]) > 0
    assert isinstance(created["warning_signs"], list) and len(created["warning_signs"]) > 0

    history_response = api_client.get(f"{base_url}/api/history", headers=auth_headers, timeout=30)
    assert history_response.status_code == 200
    history = history_response.json()
    assert any(item["id"] == created["id"] for item in history)


# Clinic discovery module and geocoordinate query coverage
def test_clinics_nearby_returns_map_and_cards(api_client, base_url, auth_headers):
    response = api_client.get(
        f"{base_url}/api/clinics/nearby?lat=28.6139&lng=77.2090",
        headers=auth_headers,
        timeout=60,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("map_embed_url"), str) and "google.com/maps" in data["map_embed_url"]
    assert data.get("emergency_number") == "112"
    assert isinstance(data.get("clinics"), list)
    if data["clinics"]:
        first = data["clinics"][0]
        assert isinstance(first.get("name"), str) and len(first["name"]) > 0
        assert isinstance(first.get("maps_url"), str) and "google.com/maps" in first["maps_url"]
