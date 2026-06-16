from app.services.chat_service import ChatService


class FakeLLMClient:
    def can_use(self):
        return True

    def generate(self, user_query, context_text, knowledge_snippet):
        return "This is an LLM-generated answer."


def test_llm_used_on_fallback_path(monkeypatch, app):
    with app.app_context():
        service = ChatService()

        monkeypatch.setattr(service, "llm_client", FakeLLMClient())

        # Force fallback from FAQ, RAG, and NLP.
        monkeypatch.setattr(service, "_match_faq", lambda _text, _entries: ("fallback", "", 0.0, "fallback"))
        monkeypatch.setattr(service, "_match_rag", lambda _text, _entries: ("fallback", "", 0.0, "fallback"))
        monkeypatch.setattr(service.nlp_engine, "analyze", lambda _text: {"intent": "unknown", "entities": {}})

        result = service.process_message(user_id=None, message="random unknown question", session_id="s1")

        assert result["source"] == "llm"
        assert "LLM-generated" in result["response"]
