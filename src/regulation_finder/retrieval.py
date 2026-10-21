"""Topic narrowing then query-token coverage ranking; stable ties by article ID."""

from dataclasses import dataclass

from .config import FALLBACK, Settings
from .preprocessing import tokens
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

    def search(self, question: str) -> SearchResult:
        query = set(tokens(question))
        if not query:
            return SearchResult([], None, 0.0, "Enter a question containing words or numbers.")
        topic, probability = self.model.predict(question)
        if probability < self.settings.min_topic_probability or probability == 0:
            return SearchResult([], topic, probability, FALLBACK)
        ranked = []
        for article in self.dataset.articles:
            if article.topic == topic:
                score = len(query & self._normalized[article.article_id]) / len(query)
                if score > 0 and score >= self.settings.min_lexical_score:
                    ranked.append((score, article))
        ranked.sort(key=lambda pair: (-pair[0], pair[1].article_id))
        articles = [article for _, article in ranked[:3]]
        return SearchResult(articles, topic, probability, "" if articles else FALLBACK)
