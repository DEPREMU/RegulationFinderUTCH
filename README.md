# RegulationFinderUTCH

University Nano-AI track #5, Regulation Finder. A lightweight offline application retrieves up to three articles with their identifiers and **exact original text**. It does not generate answers. Informational only; not an official university source.

This repository is preparation, not the completed assignment. Everything under `data/synthetic/` is **invented synthetic demo data**, not UTCH regulation. The real training and development files in `data/real/` were supplied for this project; the project team confirmed authorization to publish and redistribute the regulation data and derived artifacts on 21 November 2026. External evaluation questions, student contributions, and Pi results are not implied.

## Setup and synthetic demo

Target Python 3.10+ on Linux, including Raspberry Pi with compatible wheels; actual Pi compatibility is pending. Development was verified on Python 3.12.3. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (resolution tooling used: 0.12.5) and Node.js/npm (to build the local React UI served by Flask), then from the repository root:

```sh
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run --frozen regulation-finder validate
uv run --frozen regulation-finder train
uv run --frozen regulation-finder search 'library books return receipt'
uv run --frozen regulation-finder web
```

Open http://127.0.0.1:5000. Stop with Ctrl-C. All application assets are local; after dependency installation the demo requires no network. No API keys or environment variables are required. Flask's local development server is sufficient for the class demo; debug mode is disabled.

```sh
uv run --frozen regulation-finder evaluate --split development
uv run --frozen regulation-finder calibrate --steps 11
uv run --frozen regulation-finder evaluate
uv run --frozen regulation-finder measure --iterations 100 --hardware-label 'local development host; not Raspberry Pi'
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen pytest
```

Outputs are JSON. To retain a report locally, redirect it to `artifacts/`. `measure` records actual OS, architecture, Python, NumPy, dataset hash, model hash, warm-search median/p95 latency and process peak RSS. These are local synthetic smoke measurements, never assignment accuracy or Raspberry Pi claims.

Global options precede the subcommand:

```sh
uv run --frozen regulation-finder --data data/synthetic --model artifacts/synthetic-model.json --min-topic-probability 0.55 --min-lexical-score 0.15 search 'laboratory goggles'
```

Missing or stale artifacts require `train`; invalid datasets exit with a clear error. Empty questions request input. Unseen vocabulary, failed probability gates or no useful lexical overlap produce `I don't find this in the regulation`. At most three articles from the predicted topic appear; fewer candidates yield fewer results without crossing topics. Synthetic-demo commands can pass explicit thresholds; the real Week 2 defaults below are the selected settings from the documented development-only calibration. `calibrate` reports a threshold grid but does not select a setting or read the out-of-scope/final evaluation splits.

The current real-data Week 2 run is organized under `data/real/train/`, `data/real/dev/` and `data/real/prepared/`; the saved model and calibration outputs are under `artifacts/training/`. `.gitignore` allows these files to be added for repository-level reproducibility. The project team confirmed authorization to publish the regulation data and derived artifacts. The separate final evaluation file is not included.

Reproduce the Week 2 model and development-only calibration with:

```sh
uv sync --frozen
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json validate
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json train
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json calibrate --steps 21 > artifacts/training/development-calibration-grid.json
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json evaluate --split development > artifacts/training/development-evaluation.json
```

The selected thresholds (`0.25` topic probability and `0.25` lexical coverage) are recorded in `artifacts/training/selected-settings.json` and used by default. On the 20 development examples, this setting retrieves a correct article in the top three for 14 queries; 4 answerable queries abstain. The grid and evaluation reports are reproducible with the commands above. No out-of-scope development examples were available to measure false returns, and the final evaluation set remains separate and unused.

The Week 3 release adds the user-supplied 60 questions marked `train` to the original 60, mapping each question to the prepared catalog topic for its article number. Its dataset is `data/real/week3-prepared/`, and the frozen model is `artifacts/training/week3-real-model.json`. The Week 3 configuration uses topic probability `0.35` and lexical coverage `0.25`; pass both values explicitly when searching or evaluating with this model. Reproduction commands and development results are in [the Week 3 model release record](docs/week-3-model-release.md). These questions are training data, not an independent test set.

## Submission-ready release and live demo launch (Week 4)

To reproduce the evaluated Week 3 model release and launch the live demo on any team member's machine (after `uv sync --frozen` and `npm --prefix frontend ci && npm --prefix frontend run build` above):

```sh
sha256sum artifacts/training/week3-real-model.json
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json validate
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json --min-topic-probability 0.35 --min-lexical-score 0.25 search '¿Cuál es la calificación mínima aprobatoria?'
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json --min-topic-probability 0.35 --min-lexical-score 0.25 web
```

- Frozen evaluated model: `artifacts/training/week3-real-model.json` (SHA-256 `986ea56a5ebac58f1da7857e4e38c27d7be73c9ab0b555955b55dbefcb261ae4`)
- Dataset: `data/real/week3-prepared` (`utch-week3-train120-dev20-v1.0`, fingerprint `80f42de07c942a7ef0f5db28a76dabccbcb7a0678b8dd3edc06e33ba8eaa19ed`)
- Selected settings: `artifacts/training/week3-selected-settings.json` (`min_topic_probability = 0.35`, `min_lexical_score = 0.25`)
- Training/calibration manifest: `artifacts/training/week3-training-manifest.json`
- Independent evaluation record: `artifacts/training/week3-independent-evaluation.json` (32/60 top-three hits, 53.3%)
- Model review & presentation segment: [Week 4 model presentation](docs/week-4-model-presentation.md)

The legacy flat query/article-pair adapter can still be used with:

```sh
uv run --frozen python scripts/prepare_pair_dataset.py \
  --pairs /path/to/dataset_v1.0_train_dev.json \
  --articles /path/to/reglas_reglamento_utch.json \
  --output data/real
```

The adapter preserves the `train`/`dev` assignments, allows multiple queries to reference one article, and refuses to write output when an article topic has no training example. Publication of the supplied regulation data and derived artifacts is authorized by the project team.

## V2 grouped 3,600-question experiment

V2 keeps the same 22 articles and 20 canonical topics. It audits the supplied 3,600-question
bank, holds out complete article+intention families, trains a lightweight word+Spanish-suffix
Naive Bayes model, and adds optional article retrieval profiles. The frozen V2 release uses
topic probability `0.55`, lexical score `0.45` and article profile weight `1.0`:

```sh
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --min-topic-probability 0.55 --min-lexical-score 0.45 --article-profile-weight 1.0 search '¿Cuál es la calificación mínima aprobatoria?'
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --min-topic-probability 0.55 --min-lexical-score 0.45 --article-profile-weight 1.0 web
```

The leakage-corrected grouped development comparison is V1 `330/708` (46.61%) versus V2
`439/708` (62.01%) Top-3, with the same 3/30 local out-of-scope false returns. V2 excludes 52
historical questions that overlap held-out intentions; 5 conservative exclusions still require
human review. This is development, not a new independent final evaluation. See
[the complete V2 audit and release report](docs/v2-training-3600-report.md).

## Assignment checklist and pending inputs

- Classifier: direct multinomial Naive Bayes, trained from scratch; no pretrained models, embeddings, LLMs or external AI APIs. No autocomplete.
- One row per article, original text retained: 22 articles are included in the prepared dataset.
- The project team confirmed authorization to publish and redistribute the regulation data and derived artifacts on 21 November 2026. Software licensing remains a separate team decision; no license is selected here.
- Training/development runs: Week 2 used 60 training questions; Week 3 combines those with 60 additional training questions. Both use 20 development pairs; the final evaluation set remains separate and unused.
- User-designated 60-question evaluation returned 32/60 top-three hits (53.3%) with the frozen Week 3 model. The CSV does not identify the authoring team, so that provenance remains unconfirmed; no out-of-scope questions were included.
- Actual Raspberry Pi model, OS, installation, latency and memory measurements: **pending Betsy**.
- Live demo, dataset, code and two-page technical report: templates and procedures ready; final deliverables **pending**.
- Everyone codes, presents and maintains short weekly logs: blank templates provided; actual contributions/presentation evidence **pending**.
- Instructor deadline and calendar dates: **pending**. Plan covers four relative weeks, not the assignment's original seven weeks.

Read [data contracts](data/README.md), [architecture](docs/architecture.md), [four-week plan](docs/project-plan.md), [evaluation](docs/evaluation.md), [Week 3 model release](docs/week-3-model-release.md), [Pi procedure](docs/raspberry-pi.md) and [report outline](docs/report-template.md).

The team supplied the [Trello AI board](https://trello.com/b/bNahlyvm/ai). It was not accessed or modified during initialization. Git work is local only; do not push, deploy or change remotes without new authorization. GitHub workflow is supplied but remote execution remains pending while commits stay local.
