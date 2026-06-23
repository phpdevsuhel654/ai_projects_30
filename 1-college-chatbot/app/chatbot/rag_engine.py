import math
from collections import Counter

from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize


class RAGEngine:
    def __init__(self):
        self.stemmer = PorterStemmer()

    def best_match(self, query_text, knowledge_entries):
        entries = list(knowledge_entries or [])
        if not entries:
            return None, 0.0

        docs = [self._doc_text(entry) for entry in entries]
        doc_tokens = [self._tokenize(text) for text in docs]
        query_tokens = self._tokenize(query_text)

        if not query_tokens:
            return None, 0.0

        idf = self._idf(doc_tokens)
        query_vec = self._tfidf_vector(query_tokens, idf)

        best_index = -1
        best_score = 0.0

        for idx, tokens in enumerate(doc_tokens):
            doc_vec = self._tfidf_vector(tokens, idf)
            score = self._cosine_similarity(query_vec, doc_vec)
            if score > best_score:
                best_score = score
                best_index = idx

        if best_index < 0:
            return None, 0.0

        return entries[best_index], round(best_score, 4)

    def _doc_text(self, entry):
        title = getattr(entry, "title", "") or ""
        content = getattr(entry, "content", "") or ""
        tags = getattr(entry, "tags", "") or ""
        return f"{title} {content} {tags}".strip()

    def _tokenize(self, text):
        words = [w.lower() for w in wordpunct_tokenize(text or "") if w.isalpha()]
        return [self.stemmer.stem(word) for word in words]

    def _idf(self, corpus_tokens):
        total_docs = len(corpus_tokens)
        doc_freq = Counter()
        for tokens in corpus_tokens:
            for term in set(tokens):
                doc_freq[term] += 1

        return {
            term: math.log((1 + total_docs) / (1 + freq)) + 1.0
            for term, freq in doc_freq.items()
        }

    @staticmethod
    def _tfidf_vector(tokens, idf):
        term_freq = Counter(tokens)
        vec = {}
        total_terms = sum(term_freq.values()) or 1

        for term, freq in term_freq.items():
            if term in idf:
                vec[term] = (freq / total_terms) * idf[term]

        return vec

    @staticmethod
    def _cosine_similarity(vec_a, vec_b):
        if not vec_a or not vec_b:
            return 0.0

        dot = 0.0
        for key, val in vec_a.items():
            dot += val * vec_b.get(key, 0.0)

        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot / (norm_a * norm_b)
