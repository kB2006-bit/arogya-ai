import uuid


# Emergency severity + SOS-related analyze endpoint regression checks
def test_analyze_symptoms_high_severity_sets_emergency_true(api_client, base_url, auth_headers):
    payload = {
        "message": f"I have severe chest pain, shortness of breath, and dizziness right now {uuid.uuid4()}"
    }
    response = api_client.post(
        f"{base_url}/api/analyze-symptoms",
        headers=auth_headers,
        json=payload,
        timeout=60,
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("severity") == "High"
    assert data.get("emergency") is True
    assert isinstance(data.get("response"), str) and data["response"].strip()


# Non-high severity should not set emergency=true
def test_analyze_symptoms_non_high_does_not_set_emergency_true(api_client, base_url, auth_headers):
    payload = {
        "message": f"I have mild runny nose and slight throat irritation for one day {uuid.uuid4()}"
    }
    response = api_client.post(
        f"{base_url}/api/analyze-symptoms",
        headers=auth_headers,
        json=payload,
        timeout=60,
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("severity") in ["Low", "Medium", "High"]
    if data.get("severity") != "High":
        assert data.get("emergency") is False