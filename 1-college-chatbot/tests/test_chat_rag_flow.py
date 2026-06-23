def test_chat_api_rag_path(client):
    response = client.post(
        "/api/chat",
        json={"message": "Which companies visit for hiring?", "session_id": "test-session"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["source"] in {"rag", "faq", "nlp"}
    assert "response" in data
