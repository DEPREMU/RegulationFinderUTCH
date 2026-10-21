"""JSON dataset contracts and cross-file validation, without changing source text."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .preprocessing import tokens


@dataclass(frozen=True)
class Article:
    article_id: str
    text: str
    topic: str
    source: str


@dataclass(frozen=True)
class TrainingExample:
    example_id: str
    question: str
    topic: str
    provenance: str


@dataclass(frozen=True)
class EvaluationExample:
    question_id: str
    question: str
    accepted_article_ids: list[str]
    provenance: str


@dataclass(frozen=True)
class Dataset:
    articles: list[Article]
    training: list[TrainingExample]
    development: list[EvaluationExample]
    evaluation: list[EvaluationExample]
    out_of_scope: list[EvaluationExample]
    metadata: dict
    fingerprint: str


def _rows(path: Path, cls, id_field: str):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"{path.name}: expected an array")
    result, seen = [], set()
    for row in raw:
        if not isinstance(row, dict) or set(row) != set(cls.__dataclass_fields__):
            raise ValueError(f"{path.name}: missing or unexpected fields")
        for key, value in row.items():
            if key == "accepted_article_ids":
                if (
                    not isinstance(value, list)
                    or any(not isinstance(v, str) or not v.strip() for v in value)
                    or len(value) != len(set(value))
                ):
                    raise ValueError(f"{path.name}: invalid accepted article identifiers")
            elif not isinstance(value, str) or not value.strip():
                raise ValueError(f"{path.name}: {key} must be nonempty text")
        if row[id_field] in seen:
            raise ValueError(f"{path.name}: duplicate identifier {row[id_field]}")
        seen.add(row[id_field])
        result.append(cls(**row))
    return result


def load_dataset(directory: str | Path) -> Dataset:
    directory = Path(directory)
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or not isinstance(metadata.get("synthetic"), bool):
        raise ValueError("metadata.json requires a boolean synthetic flag")
    for key in ("dataset_id", "permission_status", "evaluation_origin"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError(f"metadata.json requires {key}")
    articles = _rows(directory / "articles.json", Article, "article_id")
    training = _rows(directory / "training.json", TrainingExample, "example_id")
    splits = [
        _rows(directory / f"{name}.json", EvaluationExample, "question_id")
        for name in ("development", "evaluation", "out_of_scope")
    ]
    if not articles or not training:
        raise ValueError("Articles and training examples must not be empty")
    topics = {a.topic for a in articles}
    if {t.topic for t in training} != topics:
        raise ValueError("Training topic labels must cover exactly the article topics")
    if any(not tokens(t.question) for t in training):
        raise ValueError("Training questions must contain searchable tokens")
    article_ids = {a.article_id for a in articles}
    seen_ids, seen_questions = set(), set()
    for split in (training, *splits):
        for row in split:
            identifier = getattr(row, "example_id", getattr(row, "question_id", None))
            normalized = " ".join(tokens(row.question))
            if not normalized or identifier in seen_ids or normalized in seen_questions:
                raise ValueError("Empty question, duplicate ID, or question leakage across splits")
            seen_ids.add(identifier)
            seen_questions.add(normalized)
    for split in splits[:2]:
        if any(not e.accepted_article_ids for e in split):
            raise ValueError("Answerable examples require accepted article identifiers")
    for split in splits:
        if any(set(e.accepted_article_ids) - article_ids for e in split):
            raise ValueError("Unknown article reference")
    if any(e.accepted_article_ids for e in splits[2]):
        raise ValueError("Out-of-scope examples must have no accepted articles")
    names = ("metadata", "articles", "training", "development", "evaluation", "out_of_scope")
    digest = hashlib.sha256()
    for name in names:
        digest.update(name.encode())
        digest.update((directory / f"{name}.json").read_bytes())
    return Dataset(articles, training, *splits, metadata, digest.hexdigest())
