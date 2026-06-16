from app.chatbot.rag_engine import RAGEngine


class Entry:
    def __init__(self, title, content, tags=""):
        self.title = title
        self.content = content
        self.tags = tags


def test_rag_engine_best_match_returns_relevant_entry():
    entries = [
        Entry("Admission Process", "Submit form and documents for admission."),
        Entry("Placements", "Top companies visit campus for hiring and placements."),
    ]

    entry, score = RAGEngine().best_match("Which companies visit for hiring?", entries)

    assert entry is not None
    assert entry.title == "Placements"
    assert score > 0
