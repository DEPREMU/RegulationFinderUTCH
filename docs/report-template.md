# Two-page technical report outline

Status: blank outline; final report PENDING Emanuel and all contributors. Keep the submitted report to two pages; adjust layout according to instructor guidance (pending).

## Page 1 — problem, data and method

- Track #5; question to original article retrieval; informational/unofficial scope.
- Authorized regulation version/source and permission evidence: **PENDING**.
- Dataset: 22 articles and 20 topics; 120 training questions (60 original plus 60 user-supplied Week 3 questions) and 20 development questions. Week 3 source rows are marked `train`; their article numbers were mapped to the prepared catalog topics. Authoring-team provenance is not provided.
- Explain train-only vocabulary, direct smoothed multinomial Naive Bayes, topic narrowing, lexical ranking, up to three original articles and low-confidence abstention.
- Week 3 frozen development-selected thresholds: topic probability `0.35`, lexical coverage `0.25`; selection objective and identifiers are recorded in `docs/week-3-model-release.md` and `artifacts/training/week3-training-manifest.json`.

## Page 2 — evaluation, deployment and limitations

- Another team's authorship/provenance; independent frozen test N (at least 60): **PENDING**.
- Headline hits H/N and percentage (abstentions included as misses): **PENDING / PENDING**.
- Answerable abstentions A/N and out-of-scope abstentions B/M: **PENDING**.
- Actual Pi model/RAM, OS/Python, iterations, procedure, latency median/p95 and process peak RSS: **PENDING**.
- Week 3 identifiers: dataset fingerprint `80f42de07c942a7ef0f5db28a76dabccbcb7a0678b8dd3edc06e33ba8eaa19ed`; model SHA-256 `986ea56a5ebac58f1da7857e4e38c27d7be73c9ab0b555955b55dbefcb261ae4`; code revision and dependency-lock hash are recorded in the training manifest. Development errors and limitations are summarized in the model-release document. Independent test result remains **PENDING**.
- Contributions/code/presentation evidence per member and weekly logs: **PENDING**.
- Final deliverable references: live demo, authorized dataset, code and report: **PENDING**.

Do not substitute synthetic demo scores for assignment results. Explain independence assumptions, vocabulary mismatch, topic errors, heuristic confidence and unmeasured conditions honestly. Include concise source references and distinguish local development evidence from Pi measurements.
