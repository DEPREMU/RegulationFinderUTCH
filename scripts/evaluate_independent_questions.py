"""Evaluate a frozen model against a frozen, user-designated CSV question set."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from regulation_finder.classifier import TopicClassifier
from regulation_finder.config import Settings
from regulation_finder.evaluation import evaluate
from regulation_finder.preprocessing import tokens
from regulation_finder.retrieval import Retriever
from regulation_finder.schemas import EvaluationExample, load_dataset


def run(
    data_dir: Path,
    source_path: Path,
    model_path: Path,
    settings_path: Path,
    freeze_path: Path,
) -> dict:
    dataset = load_dataset(data_dir, include_development=True, include_evaluation=False)
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    settings_hash = hashlib.sha256(settings_path.read_bytes()).hexdigest()
    if freeze.get("result_status") != "pending":
        raise ValueError(
            "Evaluation freeze is not pending; use a new independent set for another result"
        )
    if freeze.get("source_sha256") != source_hash:
        raise ValueError("Question file hash does not match the frozen set")
    if freeze.get("model_sha256") != model_hash or freeze.get("settings_sha256") != settings_hash:
        raise ValueError("Model or selected settings do not match the frozen release")
    if freeze.get("dataset_fingerprint") != dataset.fingerprint:
        raise ValueError("Prepared dataset does not match the frozen dataset fingerprint")
    with source_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    required = {"id", "article_number", "user_query"}
    if not rows or not required <= set(rows[0]):
        raise ValueError("Question CSV requires id, article_number and user_query columns")
    if len(rows) < 60:
        raise ValueError("Independent evaluation requires at least 60 answerable questions")

    article_ids = {article.article_id for article in dataset.articles}
    examples = []
    for row in rows:
        if row["article_number"] not in article_ids:
            raise ValueError(f"Unknown article number for {row['id']}: {row['article_number']}")
        examples.append(
            EvaluationExample(
                question_id=row["id"],
                question=row["user_query"],
                accepted_article_ids=[row["article_number"]],
                provenance=f"User-designated independent set: {source_path.name}",
            )
        )

    ids = [example.question_id for example in examples]
    queries = [tuple(tokens(example.question)) for example in examples]
    training = {tuple(tokens(example.question)) for example in dataset.training}
    development = {tuple(tokens(example.question)) for example in dataset.development}
    if len(set(ids)) != len(ids) or len(set(queries)) != len(queries):
        raise ValueError("Evaluation set contains duplicate IDs or normalized questions")
    if any(query in training or query in development for query in queries):
        raise ValueError("Evaluation set overlaps training or development questions")

    selected = json.loads(settings_path.read_text(encoding="utf-8"))
    if selected.get("dataset_fingerprint") != dataset.fingerprint:
        raise ValueError("Selected settings do not match the frozen dataset fingerprint")
    model = TopicClassifier.load(model_path, dataset.fingerprint)
    settings = Settings(selected["min_topic_probability"], selected["min_lexical_score"])
    retriever = Retriever(dataset, model, settings)
    report = evaluate(retriever, examples, [])

    return {
        "evaluation_type": "user-designated independent evaluation",
        "source_file": str(source_path),
        "source_sha256": source_hash,
        "source_authorship_provenance": (
            "The user designated this as independent. The CSV does not identify the authoring team."
        ),
        "dataset_id": dataset.metadata["dataset_id"],
        "dataset_fingerprint": dataset.fingerprint,
        "development_file_sha256": hashlib.sha256(
            (data_dir / "development.json").read_bytes()
        ).hexdigest(),
        "model_file": str(model_path),
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "settings_file": str(settings_path),
        "settings_sha256": settings_hash,
        "freeze_manifest": str(freeze_path),
        "freeze_manifest_sha256": hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
        "evaluation_runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "settings": {
            "min_topic_probability": settings.min_topic_probability,
            "min_lexical_score": settings.min_lexical_score,
        },
        "headline_definition": (
            "Top-three hits divided by all answerable questions; abstentions are misses."
        ),
        "independent_evaluation_used_for_tuning": False,
        **report,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError("Refusing to overwrite an existing independent evaluation report")
        report = run(args.data, args.questions, args.model, args.settings, args.freeze)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {k: v for k, v in report.items() if k != "details"},
                ensure_ascii=False,
                indent=2,
            )
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
