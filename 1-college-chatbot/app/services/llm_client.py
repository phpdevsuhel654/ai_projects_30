from flask import current_app
import requests


class LLMClient:
    def __init__(self):
        self.enabled = current_app.config.get("ENABLE_LLM_FALLBACK", False)
        self.base_url = current_app.config.get("OPENAI_BASE_URL", "").rstrip("/")
        self.api_key = current_app.config.get("OPENAI_API_KEY", "")
        self.model = current_app.config.get("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = current_app.config.get("OPENAI_TIMEOUT_SECONDS", 20)
        self.max_tokens = current_app.config.get("OPENAI_MAX_TOKENS", 120)

    def can_use(self):
        return self.enabled and bool(self.base_url) and bool(self.api_key)

    def generate(self, user_query, context_text, knowledge_snippet):
        if not self.can_use():
            return None

        system_prompt = (
            "You are a helpful college enquiry assistant. "
            "Give concise, factual, student-friendly answers. "
            "If unsure, suggest contacting official college desk."
        )

        user_prompt = (
            f"Conversation context:\n{context_text}\n\n"
            f"Knowledge snippet:\n{knowledge_snippet}\n\n"
            f"Student question:\n{user_query}\n\n"
            "Answer in 2-4 short sentences."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": self.max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        endpoint = f"{self.base_url}/chat/completions"

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
        except requests.RequestException:
            return None
