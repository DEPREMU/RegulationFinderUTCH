# Week 3 model release

Status: the development model and search settings are frozen for independent evaluation. The independent evaluation has not been run; its headline result is pending a frozen set of at least 60 independently authored answerable questions.

## Frozen release

| Item | Frozen value |
| --- | --- |
| Dataset | `utch-week2-train60-dev20-v1.1` |
| Dataset fingerprint | `15377631d6b485455d6b0567dd95cee36ec9ad843a217c73d4daa4cb2f02821a` |
| Training / development examples | 60 / 20 |
| Articles / topics | 22 / 20 |
| Classifier | Multinomial Naive Bayes, implemented directly with NumPy |
| Smoothing | Laplace alpha `1.0` |
| Vocabulary | 312 tokens, learned from training questions only |
| Minimum topic probability | `0.25` |
| Minimum lexical coverage | `0.25` |
| Model SHA-256 | `79e62ddd6f22f8f8021a44d542c680bc481d0d199ca584dacbf32f8e335e07f5` |
| Code revision used for the release | `8b2dba9` |

Settings were selected on development data by maximizing top-three hits; ties favored higher combined thresholds, then the higher topic threshold and lexical threshold. The full grid and selected values are in `artifacts/training/development-calibration-grid.json` and `artifacts/training/selected-settings.json`. The training configuration and run metadata are in `artifacts/training/real-training-manifest.json`.

The classifier computes its parameters directly from token counts and smoothed frequencies. It has no iterative optimizer, so there is no loss curve to export. The manifest records `loss_history: null` and explains this. The model file, manifest, selected settings, calibration grid and development evaluation are the exported release log.

## Reproduction

Run these commands from the repository root with the locked dependencies:

```sh
uv sync --frozen
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json validate
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json train
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json calibrate --steps 21 > artifacts/training/development-calibration-grid.json
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json evaluate --split development > artifacts/training/development-evaluation.json
sha256sum artifacts/training/real-model.json
```

The calibration command reports a development-only grid. It does not select thresholds automatically; the committed selection is documented above. The final evaluation split is not read by these commands.

## Integration and development findings

Validation accepted the prepared dataset and its 22 articles. Training completed and reproduced the frozen model hash. Development evaluation at the frozen settings returned 14 top-three hits from 20 answerable questions (70%) and abstained on 4/20. The development set contains no out-of-scope examples, so it cannot estimate out-of-scope false returns.

The six development misses were:

| Question | Observed result | Evidence-based explanation |
| --- | --- | --- |
| `UTCH-ART-001` | Returned article 13; accepted article 2. Predicted topic `Periodos escolares` at `0.279746`. | Topic classification selected a different subject, and retrieval stayed within that topic. Article 2 defines SA, DE and AU; article 13 describes school periods. |
| `UTCH-ART-006` | Returned article 9; accepted article 8. Predicted topic `Cambio de carrera y turno` at `0.606898`. | Topic selection was plausible, but lexical ranking preferred the general career/shift change article 9 over article 8, which specifically covers first-term students and the first 10 business days. |
| `UTCH-ART-012` | Abstained. Predicted topic probability `0.216189`, below the `0.25` gate. | The query was assigned to `Cambio de carrera de nuevo ingreso`; the accepted article is about reincorporation after an interruption. |
| `UTCH-ART-014` | Abstained with predicted topic `Periodos escolares` at `0.545581`. | The topic gate passed, but no article in the predicted topic met the lexical retrieval requirements. The accepted article concerns competency-based learning evaluation. |
| `UTCH-ART-019` | Abstained at topic probability `0.193785`, below the gate. | The query was assigned to `Examen de ingreso`; the accepted article concerns student rights. |
| `UTCH-ART-020` | Abstained at topic probability `0.137666`, below the gate. | The query was assigned to `Estudios en el extranjero`; the accepted article concerns student obligations. |

These cases describe the existing development run; they do not justify changing the frozen settings. No final-test errors are available to explain yet.

## Independent evaluation handoff

Before evaluation, preserve the independently authored questions and accepted article IDs in a separate frozen file, record their provenance and SHA-256, and confirm that the set contains at least 60 answerable questions. Record the exact code revision, dependency lock, dataset fingerprint, model hash and frozen settings with the one-time evaluation output. Keep answerable abstentions in the headline denominator. Do not inspect evaluation results to choose model or search settings.

After the run, document observed errors and limitations without tuning on those questions. If the classifier, preprocessing, ranking, thresholds or model changes after final testing, use a fresh independent test set for any new headline result.
