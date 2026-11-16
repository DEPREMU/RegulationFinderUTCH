# Week 4 model review and presentation segment (Zaid)

This document reviews the frozen Week 3 model release for the final two-page report and provides Zaid's presentation segment for the live demo.

## Model section review (verified against frozen artifacts)

- **Algorithm & constraints**: From-scratch Multinomial Naive Bayes implemented with NumPy (`src/regulation_finder/classifier.py`), using Laplace smoothing ($\alpha = 1.0$) and log-space inference with a numerically stable softmax. No pretrained models, embeddings, LLMs, or external AI APIs are used.
- **Training-only vocabulary**: `489` tokens learned exclusively from the `120` training questions (`60` original Week 2 questions + `60` Week 3 questions in `data/real/week3-questions.csv`, all marked `train` and mapped to canonical catalog topics).
- **Deterministic closed-form fit**: Parameters are computed directly from token counts and smoothed frequencies (`random_seed: null`, `loss_history: null` in `artifacts/training/week3-training-manifest.json`).
- **Retrieval & fallback pipeline** (`src/regulation_finder/retrieval.py`):
  1. Normalize query tokens (NFKD, casefold, accent removal, alphanumeric tokenization).
  2. Predict topic probability distribution; abstain with `"I don't find this in the regulation"` if the top topic probability is below `0.35` or if no query tokens appear in the training vocabulary.
  3. Filter to articles in the predicted topic (`22` articles across `20` topics in `data/real/week3-prepared`).
  4. Rank candidates by query-token lexical coverage (`unique overlapping article tokens / unique query tokens`), requiring coverage $\ge 0.25$, and return up to `3` articles with their **exact original text**.
- **Calibration & evaluation evidence**:
  - **Development calibration** (`20` examples, `21`-step grid): selected `min_topic_probability = 0.35`, `min_lexical_score = 0.25`, achieving `14/20` (`70%`) top-three hits and `3/20` (`15%`) abstentions (`artifacts/training/week3-selected-settings.json`).
  - **Frozen independent evaluation** (`60` user-designated answerable questions, `0` out-of-scope questions): `32/60` (`53.3%`) top-three hits, `19/60` (`31.7%`) abstentions, `9/60` wrong-article misses (`artifacts/training/week3-independent-evaluation.json`). Misses concentrated in articles `47` (`8`), `48` (`11`), and `6` (`5`), plus `2` (`2`), `8` (`1`), and `20` (`1`).
- **Linked release identifiers**:
  - Dataset: `utch-week3-train120-dev20-v1.0` (fingerprint `80f42de07c942a7ef0f5db28a76dabccbcb7a0678b8dd3edc06e33ba8eaa19ed`)
  - Model: `artifacts/training/week3-real-model.json` (SHA-256 `986ea56a5ebac58f1da7857e4e38c27d7be73c9ab0b555955b55dbefcb261ae4`)

## Presentation segment (~2 minutes)

1. **Problem & design choice**:
   - Our goal is offline, exact-text retrieval of UTCH regulation articles—never generating or paraphrasing answers.
   - Because the target environment is a Raspberry Pi with strict offline and from-scratch constraints, we built a lightweight Multinomial Naive Bayes topic classifier in NumPy paired with lexical coverage ranking.
2. **How a query flows**:
   - A student's question is normalized and tokenized. Using only the `489`-word training vocabulary, the classifier predicts the most likely regulation topic.
   - Two confidence gates protect precision: the predicted topic probability must be at least `0.35`, and at least `25%` of the query's unique tokens must appear in a candidate article within that topic.
   - If either gate fails—for example, on an out-of-scope question—the system abstains rather than guessing. Otherwise, it returns up to three articles with their exact original text.
3. **Calibration & honest evaluation**:
   - Thresholds (`0.35` topic, `0.25` lexical) were tuned exclusively on our `20` development questions (`14/20` hits, `70%`), then frozen before final testing.
   - On the `60`-question independent evaluation set, the frozen model achieved `32/60` top-three hits (`53.3%`) and abstained on `19/60` (`31.7%`).
   - Most misses occurred on articles `47`, `48`, and `6` (student rights, student obligations, and admissions documents), where Naive Bayes's token-independence assumption and vocabulary mismatch caused topic confusion or conservative abstention.
4. **Live demo transition**:
   - The packaged release links the exact evaluated model (`week3-real-model.json`) to the Flask + React web interface, ready for live queries and out-of-scope abstention checks.

