def test_chat_page_returns_200(client):
    response = client.get("/chat")
    assert response.status_code == 200


def test_chat_api_faq_match(client):
    response = client.post(
        "/api/chat",
        json={"message": "Tell me about admission process", "session_id": "test-session"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["source"] in {"faq", "nlp", "fallback"}
    assert "response" in data
    assert "entities" in data


def test_chat_api_nlp_response_and_entity(client):
    response = client.post(
        "/api/chat",
        json={"message": "What are scholarship options for BCA 2026?", "session_id": "test-session"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["source"] in {"faq", "rag", "nlp"}
    assert data["entities"].get("program") == "BCA"
    assert data["entities"].get("year") == "2026"


def test_chat_api_empty_message_validation(client):
    response = client.post("/api/chat", json={"message": "", "session_id": "test-session"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["source"] == "validation"
    assert data["entities"] == {}
