"""Command line entry point for validation, training, retrieval and measurement."""

import argparse
import json
from dataclasses import asdict

from .calibration import sweep_development_thresholds
from .classifier import TopicClassifier
from .config import NOTICE, Settings
from .evaluation import evaluate
from .measurements import measure
from .retrieval import Retriever
from .schemas import load_dataset
from .training import train
from .web import create_app


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/synthetic")
    parser.add_argument("--model", default="artifacts/synthetic-model.json")
    parser.add_argument("--min-topic-probability", type=float, default=0.55)
    parser.add_argument("--min-lexical-score", type=float, default=0.15)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    commands.add_parser("train")
    search = commands.add_parser("search")
    search.add_argument("question")
    evaluation = commands.add_parser("evaluate")
    evaluation.add_argument("--split", choices=["development", "evaluation"], default="evaluation")
    calibration = commands.add_parser("calibrate")
    calibration.add_argument(
        "--steps",
        type=int,
        default=11,
        help="Number of evenly spaced development-only values per threshold (2-101)",
    )
    measurement = commands.add_parser("measure")
    measurement.add_argument("--iterations", type=int, default=100)
    measurement.add_argument("--hardware-label", required=True)
    web = commands.add_parser("web")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=5000)
    args = parser.parse_args(argv)
    try:
        settings = Settings(args.min_topic_probability, args.min_lexical_score)
        dataset = load_dataset(
            args.data,
            include_development=args.command in {"validate", "evaluate", "calibrate", "measure"},
            include_evaluation=args.command in {"validate", "evaluate"},
        )
        common = {
            "dataset_id": dataset.metadata["dataset_id"],
            "dataset_fingerprint": dataset.fingerprint,
            "synthetic": dataset.metadata["synthetic"],
            "notice": NOTICE,
        }
        if args.command == "validate":
            output = {**common, "valid": True, "articles": len(dataset.articles)}
        elif args.command == "train":
            train(dataset, args.model)
            output = {**common, "model_saved": args.model}
        else:
            retriever = Retriever(
                dataset, TopicClassifier.load(args.model, dataset.fingerprint), settings
            )
            if args.command == "search":
                output = {**common, **asdict(retriever.search(args.question))}
            elif args.command == "evaluate":
                output = {
                    **common,
                    "split": args.split,
                    "settings": asdict(settings),
                    "evaluation_origin": dataset.metadata["evaluation_origin"],
                    **evaluate(retriever, getattr(dataset, args.split), dataset.out_of_scope),
                }
            elif args.command == "calibrate":
                output = {
                    **common,
                    **sweep_development_thresholds(dataset, retriever.model, args.steps),
                }
            elif args.command == "measure":
                output = {
                    **common,
                    "settings": asdict(settings),
                    **measure(
                        retriever,
                        [e.question for e in dataset.development],
                        args.model,
                        args.iterations,
                        args.hardware_label,
                    ),
                }
            else:
                create_app(retriever).run(host=args.host, port=args.port, debug=False)
                return 0
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Error: {error}. Validate the dataset and train the model first.\n")


if __name__ == "__main__":
    raise SystemExit(main())
