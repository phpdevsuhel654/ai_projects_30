import re

from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize


INTENT_KEYWORDS = {
    "admissions": {"admission", "admissions", "apply", "eligibility", "enroll"},
    "fee_structure": {"fee", "fees", "tuition", "payment", "cost"},
    "scholarships": {"scholarship", "scholarships", "aid", "grant"},
    "campus_facilities": {"facility", "facilities", "library", "lab", "campus"},
    "placements": {"placement", "placements", "job", "internship", "recruiter"},
    "hostel": {"hostel", "accommodation", "mess", "room"},
    "important_dates": {"date", "deadline", "schedule", "calendar"},
    "courses_programs": {"course", "courses", "program", "programs", "degree"},
}

PROGRAM_PATTERNS = [
    r"\bbca\b",
    r"\bbba\b",
    r"\bbtech\b",
    r"\bmca\b",
    r"\bmba\b",
    r"computer science",
]


class NLPEngine:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self._stemmed_index = {
            intent: {self.stemmer.stem(word) for word in words}
            for intent, words in INTENT_KEYWORDS.items()
        }

    def analyze(self, text):
        tokens = self._tokens(text)
        intent = self._predict_intent(tokens)
        entities = self._extract_entities(text)

        return {
            "intent": intent,
            "entities": entities,
            "tokens": sorted(tokens),
        }

    def _tokens(self, text):
        words = [w.lower() for w in wordpunct_tokenize(text or "") if w.isalpha()]
        return {self.stemmer.stem(word) for word in words}

    def _predict_intent(self, tokens):
        best_intent = "unknown"
        best_score = 0

        for intent, intent_words in self._stemmed_index.items():
            score = len(tokens & intent_words)
            if score > best_score:
                best_intent = intent
                best_score = score

        return best_intent

    @staticmethod
    def _extract_entities(text):
        source = (text or "").lower()
        entities = {}

        years = re.findall(r"\b(20\d{2})\b", source)
        if years:
            entities["year"] = years[0]

        amount = re.search(r"\b(?:rs\.?|inr)?\s?(\d{3,7})\b", source)
        if amount:
            entities["amount"] = amount.group(1)

        for pattern in PROGRAM_PATTERNS:
            match = re.search(pattern, source)
            if match:
                entities["program"] = match.group(0).upper()
                break

        return entities
