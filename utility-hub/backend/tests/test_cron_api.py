def test_create_and_list_cron(client):
    payload = {
        "name": "Test Cron",
        "url": "https://example.com/cron",
        "execution_count": 2,
        "schedule_type": "daily",
    }

    create_response = client.post("/api/cron", json=payload)
    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["name"] == payload["name"]

    list_response = client.get("/api/cron")
    assert list_response.status_code == 200
    assert len(list_response.get_json()) >= 1


def test_create_custom_schedule_requires_expression(client):
    payload = {
        "name": "Custom Cron",
        "url": "https://example.com/cron",
        "execution_count": 1,
        "schedule_type": "custom",
    }

    response = client.post("/api/cron", json=payload)
    assert response.status_code == 400
    assert "schedule_expression" in response.get_json()["error"]
