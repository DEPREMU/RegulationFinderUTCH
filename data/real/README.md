# Real data

These files are tracked to reproduce the project runs on another device. Public redistribution permission for the regulation has not been confirmed.

- `train/questions.csv`: 60 questions assigned to `train`.
- `dev/dataset_v1.0_all_dev.json`: 20 original pairs, all assigned to `dev`.
- `prepared/`: normalized dataset consumed by the CLI.
- `week3-questions.csv`: user-supplied 60-question file. Its records are marked `train`; authoring-team provenance is not provided. The frozen-model diagnostic is in `artifacts/training/week3-questions-diagnostic.json`. This file is not treated as an independent final evaluation set.
- `review/`: earlier draft and review notes; not part of the training dataset.
- `artifacts/training/`: model, manifest, calibration grid, selected settings, and development reports.

To include the missing articles in the trained catalog, these labels were consolidated: Article 2 → `Calificación mínima aprobatoria`; Article 5 → `Examen de ingreso`. The decision is reflected in `prepared/articles.json`.

The separate final evaluation file remains isolated; it was not included or opened.
