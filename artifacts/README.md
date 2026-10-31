# Generated artifacts

Most artifacts are ignored. `.gitignore` allows `artifacts/training/` to be added for reproducible Week 2 training and development calibration; it contains the model, its manifest, the development threshold grid, selected settings and development report. Push the local commit before another device can retrieve these files. The separate final evaluation set and its results are not included. School permission and external redistribution terms remain pending.

From root: `uv run --frozen regulation-finder train` writes the synthetic demo model. Each search/web/evaluation command loads its selected model. A versioned JSON artifact contains training vocabulary, sorted topic labels, learned log priors/likelihoods and a SHA-256 fingerprint of metadata, articles and training rows. It is not a pickle and executes no code. Changes to those training inputs require retraining; development and final evaluation rows do not enter fit.

Reproduce synthetic demo outputs with `uv sync --frozen`, validate, train, then evaluate. Save settings, code commit, uv.lock, dataset fingerprint and model hash alongside results. Training is deterministic for identical files, NumPy/tool versions and settings. The Week 2 final evaluation remains sealed and is not represented by these artifacts.
