import time
import uuid


# Dashboard chat + combined history module regression coverage
def test_analyze_symptoms_stores_chat_record_and_history_lists_newest_first(api_client, base_url, auth_headers):
    first_message = f"TEST_history_chat_first_{uuid.uuid4()}"
    second_message = f"TEST_history_chat_second_{uuid.uuid4()}"

    first_response = api_client.post(
        f"{base_url}/api/analyze-symptoms",
        headers=auth_headers,
        json={"message": first_message},
        timeout=60,
    )
    assert first_response.status_code == 200
    first_data = first_response.json()
    assert isinstance(first_data.get("response"), str) and first_data["response"].strip()
    assert first_data.get("severity") in ["Low", "Medium", "High"]

    time.sleep(1)

    second_response = api_client.post(
        f"{base_url}/api/analyze-symptoms",
        headers=auth_headers,
        json={"message": second_message},
        timeout=60,
    )
    assert second_response.status_code == 200
    second_data = second_response.json()
    assert isinstance(second_data.get("response"), str) and second_data["response"].strip()
    assert second_data.get("severity") in ["Low", "Medium", "High"]

    history_response = api_client.get(f"{base_url}/api/history", headers=auth_headers, timeout=30)
    assert history_response.status_code == 200
    history = history_response.json()
    assert isinstance(history, list) and len(history) > 0

    first_chat_record = next((item for item in history if item.get("message") == first_message), None)
    second_chat_record = next((item for item in history if item.get("message") == second_message), None)

    assert first_chat_record is not None
    assert second_chat_record is not None
    assert second_chat_record["summary"] == second_data["response"]
    assert second_chat_record["severity"] == second_data["severity"]

    first_idx = next(index for index, item in enumerate(history) if item.get("message") == first_message)
    second_idx = next(index for index, item in enumerate(history) if item.get("message") == second_message)
    assert second_idx < first_idx


# Dashboard history combination module (new in-memory chat + persisted symptom checks)
def test_history_contains_saved_assessments_and_new_chat_records(api_client, base_url, auth_headers):
    check_message = f"TEST_saved_assessment_{uuid.uuid4()}"
    chat_message = f"TEST_dashboard_chat_{uuid.uuid4()}"

    create_check_response = api_client.post(
        f"{base_url}/api/symptom-checker",
        headers=auth_headers,
        json={
            "message": check_message,
            "language": "en",
            "history": [],
        },
        timeout=60,
    )
    assert create_check_response.status_code == 200
    created_check = create_check_response.json()
    assert created_check.get("message") == check_message
    assert created_check.get("severity") in ["Low", "Medium", "High"]

    time.sleep(1)

    analyze_response = api_client.post(
        f"{base_url}/api/analyze-symptoms",
        headers=auth_headers,
        json={"message": chat_message},
        timeout=60,
    )
    assert analyze_response.status_code == 200
    chat_data = analyze_response.json()
    assert isinstance(chat_data.get("response"), str) and chat_data["response"].strip()

    history_response = api_client.get(f"{base_url}/api/history", headers=auth_headers, timeout=30)
    assert history_response.status_code == 200
    history = history_response.json()

    saved_assessment_item = next((item for item in history if item.get("id") == created_check["id"]), None)
    in_memory_chat_item = next((item for item in history if item.get("message") == chat_message), None)

    assert saved_assessment_item is not None
    assert in_memory_chat_item is not None
    assert isinstance(in_memory_chat_item.get("summary"), str) and in_memory_chat_item["summary"].strip()
    assert in_memory_chat_item.get("severity") in ["Low", "Medium", "High"]
