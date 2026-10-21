# RegulationFinderUTCH

University Nano-AI track #5, Regulation Finder. A lightweight offline application retrieves up to three articles with their identifiers and **exact original text**. It does not generate answers. Informational only; not an official university source.

This repository is preparation, not the completed assignment. Everything under `data/synthetic/` is **invented synthetic demo data**, not UTCH regulation. No permission, school articles, external questions, student contributions, or Pi results are implied.

## Setup and synthetic demo

Target Python 3.10+ on Linux, including Raspberry Pi with compatible wheels; actual Pi compatibility is pending. Development was verified on Python 3.12.3. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (resolution tooling used: 0.12.5), then from the repository root:

```sh
uv sync --frozen
uv run --frozen regulation-finder validate
uv run --frozen regulation-finder train
uv run --frozen regulation-finder search 'library books return receipt'
uv run --frozen regulation-finder web
```

Open http://127.0.0.1:5000. Stop with Ctrl-C. All application assets are local; after dependency installation the demo requires no network. No API keys or environment variables are required. Flask's local development server is sufficient for the class demo; debug mode is disabled.

```sh
uv run --frozen regulation-finder evaluate --split development
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

Missing or stale artifacts require `train`; invalid datasets exit with a clear error. Empty questions request input. Unseen vocabulary, failed probability gates or no useful lexical overlap produce `I don't find this in the regulation`. At most three articles from the predicted topic appear; fewer candidates yield fewer results without crossing topics. Threshold defaults are arbitrary demo values, **not calibrated confidence estimates**. Choose real settings only on development data.

## Assignment checklist and pending inputs

- Classifier: direct multinomial Naive Bayes, trained from scratch; no pretrained models, embeddings, LLMs or external AI APIs. No autocomplete.
- One row per article, original text retained: schema and synthetic fixtures ready; authorized regulation and real labels **pending Karen**.
- School permission confirmed with instructor, source/provenance and redistribution terms: **pending Karen/instructor**. Software license is also a team decision; no license selected.
- Training/development data and reviewed topics: **pending Karen/Zaid**.
- At least 60 independent questions from another team, frozen test and measured top-three evaluation: **pending Emanuel**. Fixtures do not satisfy this requirement.
- Actual Raspberry Pi model, OS, installation, latency and memory measurements: **pending Betsy**.
- Live demo, dataset, code and two-page technical report: templates and procedures ready; final deliverables **pending**.
- Everyone codes, presents and maintains short weekly logs: blank templates provided; actual contributions/presentation evidence **pending**.
- Instructor deadline and calendar dates: **pending**. Plan covers four relative weeks, not the assignment's original seven weeks.

Read [data contracts](data/README.md), [architecture](docs/architecture.md), [four-week plan](docs/project-plan.md), [evaluation](docs/evaluation.md), [Pi procedure](docs/raspberry-pi.md) and [report outline](docs/report-template.md).

The team supplied the [Trello AI board](https://trello.com/b/bNahlyvm/ai). It was not accessed or modified during initialization. Git work is local only; do not push, deploy or change remotes without new authorization. GitHub workflow is supplied but remote execution remains pending while commits stay local.
