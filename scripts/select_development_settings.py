"""Select frozen thresholds from a development-only calibration grid."""

import argparse
import json
from pathlib import Path

OBJECTIVE = (
    "Maximize development top-three hits; among tied settings, choose the highest "
    "combined thresholds, then the higher topic threshold and lexical threshold."
)


def select(input_path: Path, output_path: Path) -> dict:
    grid = json.loads(input_path.read_text(encoding="utf-8"))
    if grid.get("split") != "development" or not grid.get("threshold_sweep"):
        raise ValueError("Input must contain a non-empty development-only threshold sweep")
    results = grid["threshold_sweep"]
    best = max(
        results,
        key=lambda row: (
            row["top_three_hits"],
            row["min_topic_probability"] + row["min_lexical_score"],
            row["min_topic_probability"],
            row["min_lexical_score"],
        ),
    )
    settings = {
        "dataset_id": grid["dataset_id"],
        "dataset_fingerprint": grid["dataset_fingerprint"],
        "calibration_split": "development",
        "development_examples": best["eligible_questions"],
        "grid_steps_per_threshold": grid["grid_steps_per_threshold"],
        "selection_objective": OBJECTIVE,
        "min_topic_probability": best["min_topic_probability"],
        "min_lexical_score": best["min_lexical_score"],
        "top_three_hits": best["top_three_hits"],
        "top_three_hit_rate": best["top_three_hit_rate"],
        "answerable_abstentions": best["answerable_abstentions"],
        "answerable_abstention_rate": best["answerable_abstention_rate"],
        "selection_is_development_only": True,
        "final_evaluation_used": False,
        "out_of_scope_examples_used": 0,
        "limitation": (
            "No out-of-scope development examples were available for calibration; "
            "the independent final evaluation remains sealed."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Development calibration grid JSON")
    parser.add_argument("output", type=Path, help="Path for selected settings JSON")
    args = parser.parse_args()
    try:
        print(json.dumps(select(args.input, args.output), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
