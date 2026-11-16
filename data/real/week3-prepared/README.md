# Week 3 prepared training dataset

This dataset combines the original 60 training questions with the 60 user-supplied Week 3 questions, for 120 training examples. All Week 3 rows were marked `train` in the source CSV. Their article numbers were mapped to the canonical topic labels in `articles.json`; original source topic labels are retained in each row’s provenance.

The 20 development examples and 22-article catalog are unchanged from the Week 2 prepared dataset. The separate independent final evaluation set is not copied here or read during training and development calibration.

Reproduce the Week 3 training and development selection from the repository root with the commands in [`docs/week-3-model-release.md`](../../../docs/week-3-model-release.md).
