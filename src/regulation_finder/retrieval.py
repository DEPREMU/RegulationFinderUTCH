"""Topic narrowing then query-token coverage ranking; stable ties by article ID."""

from dataclasses import dataclass
from math import log

from .config import FALLBACK, Settings
from .preprocessing import content_tokens, morphological_features, tokens
from .schemas import Article


@dataclass(frozen=True)
class SearchResult:
    articles: list[Article]
    topic: str | None
    topic_probability: float
    message: str


class Retriever:
    def __init__(self, dataset, model, settings: Settings | None = None):
        if set(model.labels) != {a.topic for a in dataset.articles}:
            raise ValueError("Model topics do not match dataset topics")
        self.dataset, self.model, self.settings = dataset, model, settings or Settings()
        self._normalized = {a.article_id: set(tokens(a.text)) for a in dataset.articles}
        profiles = dataset.retrieval_profiles or {}
        self._profiles = {}
        for article in dataset.articles:
            profile_words = set(profiles.get(article.article_id, ())) | set(
                content_tokens(article.text)
            )
            self._profiles[article.article_id] = profile_words | set(
                morphological_features(profile_words)
            )
        document_frequency = {}
        for profile in self._profiles.values():
            for token in profile:
                document_frequency[token] = document_frequency.get(token, 0) + 1
        article_count = len(dataset.articles)
        self._idf = {
            token: log((article_count + 1) / (frequency + 1)) + 1
            for token, frequency in document_frequency.items()
        }

    def search(self, question: str) -> SearchResult:
        query = set(tokens(question))
        if not query:
            return SearchResult([], None, 0.0, "Enter a question containing words or numbers.")
        topic, probability = self.model.predict(question)
        if probability < self.settings.min_topic_probability or probability == 0:
            return SearchResult([], topic, probability, FALLBACK)
        ranked = []
        content_words = set(content_tokens(question)) or query
        content_query = content_words | set(morphological_features(content_words))
        query_weight = sum(self._idf.get(token, 1.0) for token in content_query)
        for article in self.dataset.articles:
            if article.topic == topic:
                raw_score = len(query & self._normalized[article.article_id]) / len(query)
                profile_score = (
                    sum(
                        self._idf.get(token, 1.0)
                        for token in content_query & self._profiles[article.article_id]
                    )
                    / query_weight
                    if query_weight
                    else 0.0
                )
                score = max(
                    raw_score,
                    self.settings.article_profile_weight * profile_score,
                )
                if score > 0 and score >= self.settings.min_lexical_score:
                    ranked.append((score, raw_score, article))
        ranked.sort(key=lambda pair: (-pair[0], -pair[1], pair[2].article_id))
        articles = [article for _, _, article in ranked[:3]]
        return SearchResult(articles, topic, probability, "" if articles else FALLBACK)
