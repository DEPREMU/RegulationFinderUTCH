#!/usr/bin/env python3
"""Normalize the supplied flat query/article pairs for RegulationFinderUTCH.

The tool refuses to create output unless every article topic has a training
example. It never changes or merges train/development assignments.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


def _read_array(path: Path, required_fields: set[str]) -> list[dict]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, list):
        raise ValueError(f"{path}: expected a JSON array")
    for index, row in enumerate(value, start=1):
        if not isinstance(row, dict) or not required_fields <= row.keys():
            raise ValueError(f"{path}: record {index} is missing required fields")
        for field in required_fields:
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"{path}: record {index} has empty or non-text {field}")
    return value


def _normalized_question(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


def prepare(pair_path: Path, article_path: Path, output_dir: Path) -> dict:
    pairs = _read_array(
        pair_path,
        {
            "id",
            "article_number",
            "topic",
            "user_query",
            "original_text",
            "source_version",
            "split",
        },
    )
    source_articles = _read_array(
        article_path,
        {"article_number", "topic", "original_text", "page", "source_version"},
    )
    articles_by_number = {}
    for article in source_articles:
        number = article["article_number"]
        if number in articles_by_number:
            raise ValueError(f"Duplicate source article number: {number}")
        articles_by_number[number] = article

    ids, questions = set(), set()
    split_rows = {"train": [], "dev": []}
    for pair in pairs:
        identifier = pair["id"]
        if identifier in ids:
            raise ValueError(f"Duplicate pair id: {identifier}")
        ids.add(identifier)
        if pair["split"] not in split_rows:
            raise ValueError(f"Record {identifier}: split must be train or dev")
        normalized = _normalized_question(pair["user_query"])
        if not normalized or normalized in questions:
            raise ValueError(f"Record {identifier}: empty or duplicate normalized question")
        questions.add(normalized)

        article = articles_by_number.get(pair["article_number"])
        if article is None:
            raise ValueError(f"Record {identifier}: unknown article {pair['article_number']}")
        for field in ("topic", "original_text", "source_version"):
            if pair[field] != article[field]:
                raise ValueError(
                    f"Record {identifier}: {field} disagrees with source article "
                    f"{pair['article_number']}"
                )
        split_rows[pair["split"]].append(pair)

    article_topics = {row["topic"] for row in source_articles}
    train_topics = {row["topic"] for row in split_rows["train"]}
    missing_train = sorted(article_topics - train_topics)
    dev_topics = {row["topic"] for row in split_rows["dev"]}
    missing_dev = sorted(article_topics - dev_topics)
    if missing_train:
        message = "No training example for article topic(s): " + "; ".join(missing_train)
        if missing_dev:
            message += ". Development also lacks topic(s): " + "; ".join(missing_dev)
        raise ValueError(message)
    if missing_dev:
        print(
            "Warning: development has no examples for topic(s): " + "; ".join(missing_dev),
            file=sys.stderr,
        )

    article_rows = [
        {
            "article_id": article["article_number"],
            "text": article["original_text"],
            "topic": article["topic"],
            "source": f"{article['source_version']}; {article['page']}",
        }
        for article in source_articles
    ]
    training_rows = [
        {
            "example_id": pair["id"],
            "question": pair["user_query"],
            "topic": pair["topic"],
            "provenance": "User-provided annotated pair dataset; individual author unspecified",
        }
        for pair in split_rows["train"]
    ]
    development_rows = [
        {
            "question_id": pair["id"],
            "question": pair["user_query"],
            "accepted_article_ids": [pair["article_number"]],
            "provenance": "User-provided annotated pair dataset; individual author unspecified",
        }
        for pair in split_rows["dev"]
    ]
    payloads = {
        "metadata.json": {
            "dataset_id": "utch-pairs-v1.0",
            "synthetic": False,
            "permission_status": "Pending confirmation; local use only",
            "evaluation_origin": "No independent final evaluation included",
        },
        "articles.json": article_rows,
        "training.json": training_rows,
        "development.json": development_rows,
        "evaluation.json": [],
        "out_of_scope.json": [],
    }

    if output_dir.exists():
        raise ValueError(f"Refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True)
    for name, payload in payloads.items():
        (output_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return {
        "output": str(output_dir),
        "articles": len(article_rows),
        "training_examples": len(training_rows),
        "development_examples": len(development_rows),
        "training_topics": len(train_topics),
        "development_topics": len(dev_topics),
        "topics_without_development_examples": missing_dev,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True, type=Path)
    parser.add_argument("--articles", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(
            json.dumps(
                prepare(args.pairs, args.articles, args.output), ensure_ascii=False, indent=2
            )
        )
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
