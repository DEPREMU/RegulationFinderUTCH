"""Calibrate V2 on grouped development data and compare it with frozen Week 3."""

import argparse
import csv
import hashlib
import json
import platform
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import numpy as np

from regulation_finder.classifier import TopicClassifier
from regulation_finder.config import Settings
from regulation_finder.evaluation import evaluate
from regulation_finder.measurements import measure
from regulation_finder.preprocessing import tokens
from regulation_finder.retrieval import Retriever
from regulation_finder.schemas import EvaluationExample, load_dataset


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_details(path: Path, rows: list[dict]) -> None:
    fields = [
        "question_id",
        "question",
        "accepted_article_ids",
        "predicted_topic",
        "topic_probability",
        "displayed_article_ids",
        "abstained",
        "top_one_hit",
        "hit",
        "provenance",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "accepted_article_ids": " | ".join(row["accepted_article_ids"]),
                    "displayed_article_ids": " | ".join(row["displayed_article_ids"]),
                }
            )


def _summary(report: dict) -> dict:
    return {key: value for key, value in report.items() if not key.endswith("details")}


def _load_frozen_v1(dataset, model_path: Path):
    payload = json.loads(model_path.read_text(encoding="utf-8"))
    declared_fingerprint = payload["dataset_fingerprint"]
    model = TopicClassifier.load(model_path, declared_fingerprint)
    rebuilt = TopicClassifier().fit(dataset.training)
    parameter_match = (
        model.labels == rebuilt.labels
        and model.vocabulary == rebuilt.vocabulary
        and np.array_equal(model.log_prior, rebuilt.log_prior)
        and np.array_equal(model.log_likelihood, rebuilt.log_likelihood)
    )
    if not parameter_match:
        raise ValueError("Frozen V1 parameters do not match deterministic Week 3 retraining")
    return model, {
        "declared_dataset_fingerprint": declared_fingerprint,
        "current_dataset_fingerprint": dataset.fingerprint,
        "fingerprints_match": declared_fingerprint == dataset.fingerprint,
        "deterministic_parameters_match": parameter_match,
        "comparison_policy": (
            "Use the frozen artifact after proving exact equality with a deterministic rebuild; "
            "do not modify the historical artifact."
        ),
    }


def _historical_examples(path: Path) -> list[EvaluationExample]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    required = {"id", "article_number", "user_query"}
    if not rows or not required <= set(rows[0]):
        raise ValueError("Historical CSV requires id, article_number and user_query")
    return [
        EvaluationExample(
            question_id=row["id"],
            question=row["user_query"],
            accepted_article_ids=[row["article_number"]],
            provenance="Historical Week 3 final evaluation; regression only; never used for tuning",
        )
        for row in rows
    ]


def _select_settings(v2_dataset, v2_model, v1_report):
    rows = []
    allowed_false_returns = v1_report["out_of_scope_false_returns"]
    for topic_index in range(7, 19):
        topic_threshold = topic_index * 0.05
        for lexical_index in range(2, 13):
            lexical_threshold = lexical_index * 0.05
            for profile_weight in (0.25, 0.5, 0.75, 1.0):
                settings = Settings(topic_threshold, lexical_threshold, profile_weight)
                report = evaluate(
                    Retriever(v2_dataset, v2_model, settings),
                    v2_dataset.development,
                    v2_dataset.out_of_scope,
                )
                rows.append({**asdict(settings), **_summary(report)})

    eligible = [row for row in rows if row["out_of_scope_false_returns"] <= allowed_false_returns]
    if not eligible:
        raise ValueError("No V2 setting satisfies the V1 out-of-scope false-return limit")
    selected = max(
        eligible,
        key=lambda row: (
            row["top_three_hits"],
            row["top_one_hits"],
            row["out_of_scope_abstentions"],
            row["min_topic_probability"] + row["min_lexical_score"],
            row["min_topic_probability"],
            row["min_lexical_score"],
            -row["article_profile_weight"],
        ),
    )
    return rows, selected


def run(
    v1_data_path: Path,
    v1_model_path: Path,
    v1_settings_path: Path,
    v2_data_path: Path,
    v2_model_path: Path,
    historical_path: Path,
    output_dir: Path,
) -> dict:
    v1_dataset = load_dataset(v1_data_path, include_development=True, include_evaluation=False)
    v2_dataset = load_dataset(v2_data_path, include_development=True, include_evaluation=True)
    source_manifest = json.loads(
        (v2_data_path / "source_manifest.json").read_text(encoding="utf-8")
    )
    v1_model, v1_compatibility = _load_frozen_v1(v1_dataset, v1_model_path)
    v2_model = TopicClassifier.load(v2_model_path, v2_dataset.fingerprint)
    v1_selected = json.loads(v1_settings_path.read_text(encoding="utf-8"))
    v1_settings = Settings(
        v1_selected["min_topic_probability"],
        v1_selected["min_lexical_score"],
        0.0,
    )
    v1_retriever = Retriever(v1_dataset, v1_model, v1_settings)
    v1_report = evaluate(
        v1_retriever,
        v2_dataset.development,
        v2_dataset.out_of_scope,
    )

    calibration_rows, selected = _select_settings(v2_dataset, v2_model, v1_report)
    v2_settings = Settings(
        selected["min_topic_probability"],
        selected["min_lexical_score"],
        selected["article_profile_weight"],
    )
    v2_retriever = Retriever(v2_dataset, v2_model, v2_settings)
    v2_report = evaluate(
        v2_retriever,
        v2_dataset.development,
        v2_dataset.out_of_scope,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "development-calibration-grid.json",
        {
            "dataset_id": v2_dataset.metadata["dataset_id"],
            "dataset_fingerprint": v2_dataset.fingerprint,
            "selection_split": "grouped article+intention development and local OOS regression",
            "historical_final_evaluation_used": False,
            "selection_objective": (
                "Do not exceed V1 out-of-scope false returns; then maximize Top-3 hits, "
                "Top-1 hits, OOS abstentions and threshold strictness, in that order."
            ),
            "v1_allowed_out_of_scope_false_returns": v1_report["out_of_scope_false_returns"],
            "candidate_count": len(calibration_rows),
            "candidates": calibration_rows,
        },
    )
    settings_payload = {
        "dataset_id": v2_dataset.metadata["dataset_id"],
        "dataset_fingerprint": v2_dataset.fingerprint,
        **asdict(v2_settings),
        "development_metrics": _summary(v2_report),
        "selection_is_development_only": True,
        "historical_final_evaluation_used": False,
        "out_of_scope_constraint": (
            "V2 false returns must be no greater than V1 on the 30 local regression cases"
        ),
    }
    _write_json(output_dir / "v2-settings.json", settings_payload)
    _write_details(output_dir / "development-v1-details.csv", v1_report["details"])
    _write_details(output_dir / "development-v2-details.csv", v2_report["details"])
    _write_details(
        output_dir / "development-v2-incorrect-answered.csv",
        [row for row in v2_report["details"] if not row["hit"] and not row["abstained"]],
    )
    _write_details(
        output_dir / "development-v2-abstentions.csv",
        [row for row in v2_report["details"] if row["abstained"]],
    )
    _write_details(output_dir / "oos-v1-details.csv", v1_report["out_of_scope_details"])
    _write_details(output_dir / "oos-v2-details.csv", v2_report["out_of_scope_details"])

    article_topics = {article.article_id: article.topic for article in v2_dataset.articles}
    wrong_answered = [
        row for row in v2_report["details"] if not row["hit"] and not row["abstained"]
    ]
    abstentions = [row for row in v2_report["details"] if row["abstained"]]
    ranking_errors = [
        row
        for row in wrong_answered
        if row["predicted_topic"] == article_topics[row["accepted_article_ids"][0]]
    ]
    confusion_counts = Counter(
        (row["accepted_article_ids"][0], " | ".join(row["displayed_article_ids"]))
        for row in wrong_answered
    )
    error_analysis = {
        "development_questions": len(v2_report["details"]),
        "correct": v2_report["top_three_hits"],
        "incorrect_answered": len(wrong_answered),
        "abstentions": len(abstentions),
        "low_topic_probability_abstentions": sum(
            row["topic_probability"] < v2_settings.min_topic_probability for row in abstentions
        ),
        "lexical_gate_abstentions": sum(
            row["topic_probability"] >= v2_settings.min_topic_probability for row in abstentions
        ),
        "classification_errors": len(wrong_answered) - len(ranking_errors),
        "ranking_or_article_filter_errors": len(ranking_errors),
        "top_one_miss_but_top_three_hit": (v2_report["top_three_hits"] - v2_report["top_one_hits"]),
        "most_common_confusions": [
            {
                "expected_article": expected,
                "displayed_articles": displayed,
                "count": count,
            }
            for (expected, displayed), count in confusion_counts.most_common(15)
        ],
        "out_of_scope_false_returns": [
            {
                "question": row["question"],
                "predicted_topic": row["predicted_topic"],
                "topic_probability": row["topic_probability"],
                "displayed_article_ids": row["displayed_article_ids"],
            }
            for row in v2_report["out_of_scope_details"]
            if not row["abstained"]
        ],
    }
    _write_json(output_dir / "error-analysis.json", error_analysis)

    legacy_v1 = evaluate(v1_retriever, v1_dataset.development, [])
    legacy_v2 = evaluate(v2_retriever, v1_dataset.development, [])
    historical = _historical_examples(historical_path)
    historical_v1 = evaluate(v1_retriever, historical, [])
    historical_v2 = evaluate(v2_retriever, historical, [])
    v2_training_questions = {tuple(tokens(row.question)) for row in v2_dataset.training}
    v2_development_questions = {tuple(tokens(row.question)) for row in v2_dataset.development}
    historical_exact_overlap = sum(
        tuple(tokens(row.question)) in v2_training_questions
        or tuple(tokens(row.question)) in v2_development_questions
        for row in historical
    )
    _write_details(output_dir / "legacy-development-v1-details.csv", legacy_v1["details"])
    _write_details(output_dir / "legacy-development-v2-details.csv", legacy_v2["details"])
    _write_details(output_dir / "historical-final-v1-details.csv", historical_v1["details"])
    _write_details(output_dir / "historical-final-v2-details.csv", historical_v2["details"])

    comparison = {
        "primary_comparison": (
            "Same 708 grouped article+intention holdout questions for V1 and V2"
        ),
        "semantic_separation": {
            "known_historical_training_overlaps_excluded_from_v2": source_manifest[
                "historical_semantic_overlap_exclusions"
            ],
            "confirmed_exclusions": source_manifest["historical_overlap_exclusions_confirmed"],
            "review_pending_exclusions": source_manifest[
                "historical_overlap_exclusions_pending_review"
            ],
            "complete_human_adjudication_claimed": False,
        },
        "v1": _summary(v1_report),
        "v2": _summary(v2_report),
        "delta": {
            "top_one_percentage_points": 100
            * (v2_report["top_one_hit_rate"] - v1_report["top_one_hit_rate"]),
            "top_three_percentage_points": 100
            * (v2_report["top_three_hit_rate"] - v1_report["top_three_hit_rate"]),
            "answerable_abstentions": (
                v2_report["answerable_abstentions"] - v1_report["answerable_abstentions"]
            ),
            "out_of_scope_false_returns": (
                v2_report["out_of_scope_false_returns"] - v1_report["out_of_scope_false_returns"]
            ),
        },
        "legacy_week3_development_regression": {
            "used_for_v2_selection": False,
            "v1": _summary(legacy_v1),
            "v2": _summary(legacy_v2),
        },
        "historical_final_regression": {
            "used_for_v2_selection": False,
            "independent_claim": False,
            "limitation": (
                "Previously used final questions are reported only as historical regression. "
                "They are not a new independent evaluation and may overlap semantically with "
                "the generated bank."
            ),
            "exact_normalized_overlap_with_v2_train_or_development": historical_exact_overlap,
            "v1": _summary(historical_v1),
            "v2": _summary(historical_v2),
        },
        "v1_fingerprint_compatibility": v1_compatibility,
    }
    _write_json(output_dir / "v1-v2-comparison.json", comparison)

    measurement_questions = [row.question for row in v2_dataset.development]
    v1_measurement = measure(
        v1_retriever,
        measurement_questions,
        v1_model_path,
        1000,
        "Windows development host",
    )
    v2_measurement = measure(
        v2_retriever,
        measurement_questions,
        v2_model_path,
        1000,
        "Windows development host",
    )
    measurements = {
        "same_process_peak_rss_limitation": (
            "Windows peak working set is process-lifetime high-water mark; compare latency and "
            "artifact size directly, and remeasure memory in separate Pi processes."
        ),
        "v1": {
            **v1_measurement,
            "model_size_bytes": v1_model_path.stat().st_size,
        },
        "v2": {
            **v2_measurement,
            "model_size_bytes": v2_model_path.stat().st_size,
        },
    }
    _write_json(output_dir / "measurements-windows.json", measurements)

    manifest = {
        "dataset_id": v2_dataset.metadata["dataset_id"],
        "dataset_fingerprint": v2_dataset.fingerprint,
        "training_examples": len(v2_dataset.training),
        "historical_training_examples_received": source_manifest[
            "historical_training_questions_received"
        ],
        "historical_training_examples_included": source_manifest[
            "legacy_training_questions_preserved"
        ],
        "historical_semantic_overlap_exclusions": source_manifest[
            "historical_semantic_overlap_exclusions"
        ],
        "historical_overlap_exclusions_confirmed": source_manifest[
            "historical_overlap_exclusions_confirmed"
        ],
        "historical_overlap_exclusions_pending_review": source_manifest[
            "historical_overlap_exclusions_pending_review"
        ],
        "development_examples": len(v2_dataset.development),
        "out_of_scope_development_examples": len(v2_dataset.out_of_scope),
        "article_count": len(v2_dataset.articles),
        "topic_count": len(v2_model.labels),
        "vocabulary_size": len(v2_model.vocabulary),
        "algorithm": "Multinomial Naive Bayes from scratch",
        "feature_mode": v2_model.feature_mode,
        "laplace_alpha": 1.0,
        "model_path": str(v2_model_path),
        "model_sha256": _sha256(v2_model_path),
        "model_size_bytes": v2_model_path.stat().st_size,
        "settings_path": str(output_dir / "v2-settings.json"),
        "settings_sha256": _sha256(output_dir / "v2-settings.json"),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "historical_final_used_for_tuning": False,
        "deterministic_training": True,
    }
    _write_json(output_dir / "v2-training-manifest.json", manifest)
    return {"comparison": comparison, "measurements": measurements, "manifest": manifest}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v1-data", type=Path, default=Path("data/real/week3-prepared"))
    parser.add_argument(
        "--v1-model", type=Path, default=Path("artifacts/training/week3-real-model.json")
    )
    parser.add_argument(
        "--v1-settings",
        type=Path,
        default=Path("artifacts/training/week3-selected-settings.json"),
    )
    parser.add_argument("--v2-data", type=Path, default=Path("data/real/v2-prepared"))
    parser.add_argument(
        "--v2-model", type=Path, default=Path("artifacts/training/v2/v2-model.json")
    )
    parser.add_argument(
        "--historical",
        type=Path,
        default=Path("data/real/week3-independent-questions.csv"),
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/training/v2"))
    args = parser.parse_args(argv)
    try:
        result = run(
            args.v1_data,
            args.v1_model,
            args.v1_settings,
            args.v2_data,
            args.v2_model,
            args.historical,
            args.output,
        )
        print(json.dumps(result["comparison"], ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
