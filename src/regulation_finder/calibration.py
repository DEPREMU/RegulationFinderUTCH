"""Threshold sweeps that use development examples only."""

from .config import Settings
from .evaluation import evaluate
from .retrieval import Retriever


def sweep_development_thresholds(dataset, model, steps: int = 11):
    """Report development-only results for a uniform probability/lexical grid.

    This deliberately returns the full sweep instead of selecting a setting:
    the project has not defined a calibration objective or acceptable trade-off.
    Out-of-scope and final evaluation examples are never read here.
    """
    if not isinstance(steps, int) or not 2 <= steps <= 101:
        raise ValueError("Calibration steps must be an integer from 2 through 101")
    if not dataset.development:
        raise ValueError("Development examples are required for threshold calibration")

    thresholds = [round(index / (steps - 1), 10) for index in range(steps)]
    results = []
    for topic_threshold in thresholds:
        for lexical_threshold in thresholds:
            retriever = Retriever(
                dataset,
                model,
                Settings(topic_threshold, lexical_threshold),
            )
            report = evaluate(retriever, dataset.development, [])
            results.append(
                {
                    "min_topic_probability": topic_threshold,
                    "min_lexical_score": lexical_threshold,
                    "top_three_hits": report["top_three_hits"],
                    "eligible_questions": report["eligible_questions"],
                    "top_three_hit_rate": report["top_three_hit_rate"],
                    "answerable_abstentions": report["answerable_abstentions"],
                    "answerable_abstention_rate": report["answerable_abstention_rate"],
                }
            )

    return {
        "split": "development",
        "selection": None,
        "selection_note": (
            "No threshold was selected. Compare these development-only results and choose "
            "an objective before freezing settings."
        ),
        "grid_steps_per_threshold": steps,
        "threshold_sweep": results,
    }
