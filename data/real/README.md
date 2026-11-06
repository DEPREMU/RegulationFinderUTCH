# Real data

These files are tracked to reproduce the project runs on another device. Public redistribution permission for the regulation has not been confirmed.

- `train/questions.csv`: 60 questions assigned to `train`.
- `dev/dataset_v1.0_all_dev.json`: 20 original pairs, all assigned to `dev`.
- `prepared/`: normalized dataset consumed by the CLI.
- `week3-questions.csv`: user-supplied 60-question file. Its records are marked `train`; authoring-team provenance is not provided. These questions are included in `week3-prepared/training.json`; they are not an independent final evaluation set.
- `week3-prepared/`: expanded dataset with 120 training examples and the unchanged 20-question development split. The separate final evaluation set is not copied here.
- `review/`: earlier draft and review notes; not part of the training dataset.
- `artifacts/training/`: Week 2 and Week 3 models, manifests, calibration grids, selected settings, and development reports. `week3-questions-diagnostic.json` is a historical pre-training check and is not a score for the current model.

To include the missing articles in the trained catalog, these labels were consolidated: Article 2 → `Calificación mínima aprobatoria`; Article 5 → `Examen de ingreso`. The decision is reflected in `prepared/articles.json`.

The separate final evaluation file remains isolated; it was not included or opened.
