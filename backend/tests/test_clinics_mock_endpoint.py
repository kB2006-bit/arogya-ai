import math


# Nearby clinics mock endpoint regression coverage
def test_post_clinics_returns_3_to_5_mock_clinics_with_coordinates(api_client, base_url, auth_headers):
    latitude = 28.6139
    longitude = 77.2090

    response = api_client.post(
        f"{base_url}/api/clinics",
        headers=auth_headers,
        json={"latitude": latitude, "longitude": longitude},
        timeout=30,
    )

    assert response.status_code == 200
    data = response.json()
    clinics = data.get("clinics")
    assert isinstance(clinics, list)
    assert 3 <= len(clinics) <= 5

    for clinic in clinics:
        assert isinstance(clinic.get("name"), str) and clinic["name"].strip()
        assert isinstance(clinic.get("latitude"), float)
        assert isinstance(clinic.get("longitude"), float)
        assert math.isfinite(clinic["latitude"]) and math.isfinite(clinic["longitude"])
        assert abs(clinic["latitude"] - latitude) <= 0.02
        assert abs(clinic["longitude"] - longitude) <= 0.02


# Nearby clinics endpoint auth guard coverage
def test_post_clinics_requires_auth(api_client, base_url):
    response = api_client.post(
        f"{base_url}/api/clinics",
        json={"latitude": 28.6139, "longitude": 77.2090},
        timeout=30,
    )

    assert response.status_code in [401, 403]


# Nearby clinics endpoint request validation coverage
def test_post_clinics_rejects_invalid_payload(api_client, base_url, auth_headers):
    response = api_client.post(
        f"{base_url}/api/clinics",
        headers=auth_headers,
        json={"latitude": "invalid", "longitude": 77.2090},
        timeout=30,
    )

    assert response.status_code == 422
