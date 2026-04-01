import uuid


# Symptom analysis module live/fallback contract checks
def test_analyze_symptoms_returns_response_and_severity(api_client, base_url, auth_headers):
    payload = {"message": f"I have mild sore throat and fatigue {uuid.uuid4()}"}
    response = api_client.post(f"{base_url}/api/analyze-symptoms", headers=auth_headers, json=payload, timeout=60)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("response"), str) and len(data["response"].strip()) > 0
    assert data.get("severity") in ["Low", "Medium", "High"]


# Emergency keyword rule should force high severity in analyze endpoint
def test_analyze_symptoms_high_risk_keywords_force_high(api_client, base_url, auth_headers):
    payload = {"message": f"I have chest pain and breathing issues now {uuid.uuid4()}"}
    response = api_client.post(f"{base_url}/api/analyze-symptoms", headers=auth_headers, json=payload, timeout=60)

    assert response.status_code == 200
    data = response.json()
    assert data.get("severity") == "High"
    assert isinstance(data.get("response"), str) and len(data["response"].strip()) > 0


# Input validation guard for blank message
def test_analyze_symptoms_blank_message_returns_400(api_client, base_url, auth_headers):
    response = api_client.post(f"{base_url}/api/analyze-symptoms", headers=auth_headers, json={"message": "   "}, timeout=30)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
