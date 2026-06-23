import re

from app.chatbot.nlp_engine import NLPEngine
from app.chatbot.rag_engine import RAGEngine
from app.repositories.chat_repository import ChatRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.llm_client import LLMClient


DEFAULT_RESPONSE = (
    "I could not find an exact answer yet. Please rephrase your question "
    "or contact the college help desk."
)


class ChatService:
    RAG_SCORE_THRESHOLD = 0.35

    INTENT_RESPONSES = {
        "admissions": "Admissions usually include form submission, document verification, and eligibility checks.",
        "fee_structure": "Fee structure depends on program and year. Please check the latest fee circular from the accounts office.",
        "scholarships": "Scholarship options are merit-based and category-based. You can apply during admission cycles.",
        "campus_facilities": "Campus facilities include library, labs, internet, and student activity spaces.",
        "placements": "Placement support includes resume training, mock interviews, and company drives.",
        "hostel": "Hostel facilities include accommodation, mess, and basic amenities for students.",
        "important_dates": "Important dates are published in the academic calendar and admission notices.",
        "courses_programs": "The college offers multiple undergraduate and postgraduate programs.",
    }

    def __init__(self):
        self.nlp_engine = NLPEngine()
        self.rag_engine = RAGEngine()
        self.llm_client = LLMClient()

    def process_message(self, user_id, message, session_id):
        clean_message = (message or "").strip()
        if not clean_message:
            return {
                "response": "Please enter a question.",
                "source": "validation",
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0,
            }

        nlp_result = self.nlp_engine.analyze(clean_message)
        nlp_intent = nlp_result["intent"]
        entities = nlp_result["entities"]

        entries = KnowledgeRepository.get_published_entries()
        faq_intent, faq_response, faq_confidence, faq_source = self._match_faq(clean_message, entries)

        if faq_source == "faq":
            intent = faq_intent
            response = faq_response
            confidence = faq_confidence
            source = faq_source
        else:
            rag_intent, rag_response, rag_confidence, rag_source = self._match_rag(
                clean_message,
                entries,
            )
            if rag_source == "rag":
                intent = rag_intent
                response = rag_response
                confidence = rag_confidence
                source = rag_source
            elif nlp_intent != "unknown":
                intent = nlp_intent
                response = self.INTENT_RESPONSES.get(nlp_intent, DEFAULT_RESPONSE)
                confidence = 0.55
                source = "nlp"
            else:
                intent = "fallback"
                response = DEFAULT_RESPONSE
                confidence = 0.2
                source = "fallback"

                if self.llm_client.can_use():
                    context_text = self._build_context(session_id)
                    knowledge_snippet = self._knowledge_snippet(entries)
                    llm_response = self.llm_client.generate(
                        user_query=clean_message,
                        context_text=context_text,
                        knowledge_snippet=knowledge_snippet,
                    )
                    if llm_response:
                        response = llm_response
                        source = "llm"
                        confidence = 0.7
                        intent = "llm_fallback"

        ChatRepository.save_interaction(
            user_id=user_id,
            query_text=clean_message,
            detected_intent=intent,
            entities=entities,
            session_id=session_id,
            response_text=response,
            source=source,
            confidence=confidence,
        )

        return {
            "response": response,
            "source": source,
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
        }

    def _match_faq(self, text, entries):
        terms = self._tokenize(text)

        best_score = 0
        best_entry = None

        for entry in entries:
            tags = self._tokenize(entry.tags or "")
            title_terms = self._tokenize(entry.title)
            score = len(terms & (tags | title_terms))
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score > 0:
            intent = self._slugify(best_entry.title)
            confidence = min(0.95, 0.4 + (best_score * 0.15))
            return intent, best_entry.content, confidence, "faq"

        return "fallback", DEFAULT_RESPONSE, 0.2, "fallback"

    def _match_rag(self, text, entries):
        best_entry, score = self.rag_engine.best_match(text, entries)

        if not best_entry or score < self.RAG_SCORE_THRESHOLD:
            return "fallback", DEFAULT_RESPONSE, 0.2, "fallback"

        intent = self._slugify(best_entry.title)
        response = f"{best_entry.content} (Reference: {best_entry.title})"
        confidence = min(0.9, 0.5 + score)
        return intent, response, confidence, "rag"

    @staticmethod
    def _build_context(session_id):
        history = ChatRepository.get_recent_history(session_id=session_id, limit=4)
        if not history:
            return "No prior conversation."

        lines = []
        for item in history:
            lines.append(f"User: {item.user_message}")
            lines.append(f"Bot: {item.bot_response}")

        return "\n".join(lines)

    @staticmethod
    def _knowledge_snippet(entries, limit=2):
        if not entries:
            return "No knowledge entries available."

        snippets = []
        for entry in entries[:limit]:
            snippets.append(f"- {entry.title}: {entry.content}")
        return "\n".join(snippets)

    @staticmethod
    def _tokenize(text):
        return set(re.findall(r"[a-zA-Z]+", (text or "").lower()))

    @staticmethod
    def _slugify(text):
        return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
