# Zaid — weekly contribution log

Responsibility: classifier, training, ranking and fallback. Calendar dates below follow the project work recorded in Git; confirm them against the instructor's official week schedule if it differs. Everyone contributes code and presents; presentation delivery is recorded only when completed.

Implementation note: coding-assistant support was used for repository changes. The entries below record work completed under Zaid's assigned responsibilities; Zaid supplied the task direction and real data files and approved the article-topic consolidation for articles 2 and 5.

| Week | Actual dates | Code/work completed and commit references | Validation/evidence | Presentation preparation | Next step/blocker |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-10-20–2026-10-26 | Implemented the baseline from-scratch Multinomial Naive Bayes classifier with Laplace smoothing and log-space inference; added training-only vocabulary, JSON model persistence, topic narrowing, lexical ranking, CLI/web search and synthetic fixtures. | Baseline commit `af65326`; `docs/verification.md` records 25 passing tests on synthetic fixtures and CLI/web checks. No real-data accuracy is claimed. | Added CLI and web demo commands; no presentation delivery recorded. | Integrate the supplied real train/dev data and calibrate only on development examples. |
| 2 | 2026-10-27–2026-10-30 | Assigned the supplied 60-question CSV to train and all 20 source pairs to dev; prepared the 22-article dataset, including the approved topic mappings for articles 2 and 5. Retrained the classifier, saved model weights and run settings, added dev-only threshold calibration/evaluation, set the abstention defaults and kept the final evaluation set separate. | Week 2 commit `57328ba`; validation passed for 22 articles; fingerprint `15377631d6b485455d6b0567dd95cee36ec9ad843a217c73d4daa4cb2f02821a`. Development result: 14/20 top-three hits and 4/20 abstentions at topic `0.25`, lexical `0.25`. Manifest records seed and iterative loss history as not applicable because fitting is deterministic and closed-form. | Documented CLI and web usage in `README.md`; no presentation delivery recorded. | Week 3: confirm institutional permission and obtain/freeze independent evaluation questions; do not tune against final evaluation. |
| 3 | | | | | |
| 4 | | | | | |
