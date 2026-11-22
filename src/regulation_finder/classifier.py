"""Multinomial Naive Bayes implemented directly using NumPy and JSON artifacts."""

import json
from pathlib import Path

import numpy as np

from .preprocessing import classification_features


class TopicClassifier:
    def fit(self, examples, alpha: float = 1.0, feature_mode: str = "word"):
        if not examples or not np.isfinite(alpha) or alpha <= 0:
            raise ValueError("Training examples and positive finite smoothing are required")
        if feature_mode not in {"word", "word_stem", "word_char4"}:
            raise ValueError("Feature mode must be word, word_stem or word_char4")
        self.feature_mode = feature_mode
        self.labels = sorted({e.topic for e in examples})
        self.vocabulary = sorted(
            {
                token
                for example in examples
                for token in classification_features(example.question, self.feature_mode)
            }
        )
        if not self.vocabulary:
            raise ValueError("Training vocabulary must not be empty")
        self._index = {word: i for i, word in enumerate(self.vocabulary)}
        counts = np.full((len(self.labels), len(self.vocabulary)), alpha)
        documents = np.zeros(len(self.labels))
        for example in examples:
            row = self.labels.index(example.topic)
            documents[row] += 1
            for token in classification_features(example.question, self.feature_mode):
                counts[row, self._index[token]] += 1
        self.log_prior = np.log(documents / documents.sum())
        self.log_likelihood = np.log(counts / counts.sum(axis=1, keepdims=True))
        return self

    def predict(self, question: str) -> tuple[str, float]:
        counts = np.zeros(len(self.vocabulary))
        for token in classification_features(question, self.feature_mode):
            if token in self._index:
                counts[self._index[token]] += 1
        if not counts.any():
            return self.labels[0], 0.0
        scores = self.log_prior + self.log_likelihood @ counts
        probabilities = np.exp(scores - scores.max())
        probabilities /= probabilities.sum()
        best = int(np.argmax(probabilities))
        return self.labels[best], float(probabilities[best])

    def save(self, path: str | Path, dataset_fingerprint: str):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "version": 2 if self.feature_mode != "word" else 1,
                    "feature_mode": self.feature_mode,
                    "dataset_fingerprint": dataset_fingerprint,
                    "labels": self.labels,
                    "vocabulary": self.vocabulary,
                    "log_prior": self.log_prior.tolist(),
                    "log_likelihood": self.log_likelihood.tolist(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path, dataset_fingerprint: str):
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Model artifact must be a JSON object")
        if (
            payload.get("version") not in {1, 2}
            or payload.get("dataset_fingerprint") != dataset_fingerprint
        ):
            raise ValueError("Model version or dataset fingerprint mismatch; retrain the model")
        model = cls()
        model.feature_mode = payload.get("feature_mode", "word")
        if model.feature_mode not in {"word", "word_stem", "word_char4"}:
            raise ValueError("Invalid model feature mode")
        model.labels, model.vocabulary = payload["labels"], payload["vocabulary"]
        for values in (model.labels, model.vocabulary):
            if (
                not isinstance(values, list)
                or not values
                or any(not isinstance(v, str) or not v for v in values)
                or len(set(values)) != len(values)
            ):
                raise ValueError("Invalid model labels or vocabulary")
        model._index = {word: i for i, word in enumerate(model.vocabulary)}
        model.log_prior = np.asarray(payload["log_prior"], dtype=float)
        model.log_likelihood = np.asarray(payload["log_likelihood"], dtype=float)
        if (
            model.log_prior.shape != (len(model.labels),)
            or model.log_likelihood.shape != (len(model.labels), len(model.vocabulary))
            or not np.isfinite(model.log_prior).all()
            or not np.isfinite(model.log_likelihood).all()
        ):
            raise ValueError("Invalid model parameter dimensions or values")
        return model
