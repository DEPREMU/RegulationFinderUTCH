# Generated artifacts

This directory is ignored except this README. Never commit trained artifacts, measurement outputs, secrets or unapproved regulation.

From root: `uv run --frozen regulation-finder train` writes synthetic-model.json. Each search/web/evaluation command loads it. The versioned JSON contains training vocabulary, sorted topic labels, learned log priors/likelihoods and a SHA-256 fingerprint of all dataset files. It is not a pickle and executes no code. Any dataset edit, including holdout edits, invalidates the fingerprint and requires retraining; only training rows reach fit. That conservative check ties a run to a complete snapshot without learning from holdouts.

Reproduce with `uv sync --frozen`, validate, train, then evaluate. Save outputs with shell redirection here, e.g. `uv run --frozen regulation-finder evaluate > artifacts/synthetic-evaluation.json`. Save settings, code commit, uv.lock, dataset fingerprint and model hash alongside final evaluation. Training is deterministic for identical files, NumPy/tool versions and settings. No final real-data artifact exists yet.
