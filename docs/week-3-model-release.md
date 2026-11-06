# Week 3 model release

Status: the expanded training run is frozen for independent evaluation. The final independent evaluation has not been run. The Week 3 questions supplied by the project owner are now training data and cannot be reused as a final test set.

## Training data and frozen release

The Week 3 prepared dataset combines the original 60 training questions with the 60 rows in `data/real/week3-questions.csv`. All rows in that CSV were marked `train`. Their article numbers were mapped to the canonical topic labels in the prepared article catalog; the original source topic labels are preserved in each row's provenance. The original Week 2 dataset and model remain available as the earlier release.

| Item | Week 3 frozen value |
| --- | --- |
| Dataset | `utch-week3-train120-dev20-v1.0` |
| Dataset fingerprint | `80f42de07c942a7ef0f5db28a76dabccbcb7a0678b8dd3edc06e33ba8eaa19ed` |
| Training / development examples | 120 / 20 |
| Articles / topics | 22 / 20 |
| Classifier | Multinomial Naive Bayes, implemented directly with NumPy |
| Smoothing | Laplace alpha `1.0` |
| Vocabulary | 489 tokens, learned from training questions only |
| Minimum topic probability | `0.35` |
| Minimum lexical coverage | `0.25` |
| Model SHA-256 | `986ea56a5ebac58f1da7857e4e38c27d7be73c9ab0b555955b55dbefcb261ae4` |
| Week 3 source CSV SHA-256 | `24890592f13e014932598d199de8e19942a2b9c37f3c382c088167c6834922c4` |
| Development file SHA-256 | `167f6d237c26181530a7215775e8a51192669ef98d54b6f7ad2de53b6839b4e5` |
| Training manifest | `artifacts/training/week3-training-manifest.json` |

Thresholds were selected only from the 20 development questions by maximizing top-three hits; ties favored higher combined thresholds, then the higher topic threshold and lexical threshold. The complete grid and selected settings are in `artifacts/training/week3-development-calibration-grid.json` and `artifacts/training/week3-selected-settings.json`.

The classifier computes parameters directly from token counts and smoothed frequencies. It has no iterative optimizer, so there is no loss curve. The training manifest records `loss_history: null` and explains why. The model, manifest, calibration grid, selected settings and development report are the exported run record.

## Reproduction

Run from the repository root:

```sh
uv sync --frozen
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json validate
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json train
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json calibrate --steps 21 > artifacts/training/week3-development-calibration-grid.json
uv run --frozen python scripts/select_development_settings.py artifacts/training/week3-development-calibration-grid.json artifacts/training/week3-selected-settings.json
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json --min-topic-probability 0.35 --min-lexical-score 0.25 evaluate --split development > artifacts/training/week3-development-evaluation.json
sha256sum artifacts/training/week3-real-model.json
```

The calibration command reads development examples only. The selection script accepts only a development grid and applies the documented objective. These commands do not read the separate final evaluation file.

## Development result and errors

At the frozen settings, the model returned a correct article in the displayed top three for 14/20 development questions (70%) and abstained on 3/20. Six questions missed:

| Question | Observed result | Explanation |
| --- | --- | --- |
| `UTCH-ART-006` | Returned article 9; expected article 8. | Classified as `Cambio de carrera y turno`; the lexical ranking preferred the general change article over the first-term rule. |
| `UTCH-ART-012` | Abstained at topic probability `0.336769`, below the `0.35` threshold. | Predicted `Examen de ingreso`; the expected article concerns reincorporation. |
| `UTCH-ART-014` | Returned articles 21 and 2; expected article 20. | Predicted `Calificación mínima aprobatoria`; the expected article concerns academic evaluation. |
| `UTCH-ART-017` | Returned article 4; expected article 33. | Predicted `Examen de ingreso`; the expected article concerns attendance required for an ordinary exam. |
| `UTCH-ART-019` | Abstained after passing the topic threshold (`0.447731`), with no article meeting the lexical threshold. | Predicted `Examen de ingreso`; the expected article concerns student rights. |
| `UTCH-ART-020` | Abstained at topic probability `0.301461`, below the `0.35` threshold. | The query was not assigned to the catalog topic for student obligations. |

The development set has no out-of-scope questions, so it does not measure false returns for out-of-scope queries. These are development findings; no final-test errors are available yet.

The earlier `artifacts/training/week3-questions-diagnostic.json` records a run of the Week 2 model made before the 60 questions were added to training. It is retained only as a historical record and is explicitly ineligible as a measure of current model performance.

## Independent evaluation handoff

Obtain at least 60 answerable questions independently authored by another team, with accepted article IDs and provenance. Freeze that file and record its SHA-256 before running it once with the Week 3 model hash, dataset fingerprint, dependency lock, code revision and selected settings. Keep answerable abstentions in the headline denominator. Do not tune using final evaluation results.

After evaluation, document observed errors and limitations without changing the model based on those questions. Any change after final testing requires a fresh independent test set for a new headline result.
