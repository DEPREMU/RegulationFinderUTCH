# Initialization verification

Executed on the local Linux x86_64 development host, Python 3.12.3; not a Raspberry Pi. All data here was synthetic. No assignment performance conclusion follows from these checks.

Successful commands from the repository root:

```sh
uv lock
uv sync --frozen
uv run --frozen regulation-finder validate
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest
.venv/bin/regulation-finder validate
.venv/bin/regulation-finder train
.venv/bin/regulation-finder search 'library books return receipt'
.venv/bin/regulation-finder evaluate --split development
.venv/bin/regulation-finder evaluate
.venv/bin/regulation-finder measure --iterations 100 --hardware-label 'local Linux x86_64 development host; not Raspberry Pi'
.venv/bin/regulation-finder web --port 5055
```

Ruff lint and formatting checks passed; pytest passed **25 tests**. They cover the from-scratch counts/smoothing and serialization, training-only vocabulary, exact multiline original text, deterministic ranking/top-three limit, empty/unsupported queries, topic and lexical gates, small candidate pools, data validation/leakage, evaluation denominators/abstentions, web notices/escaping/search, missing artifacts and CLI flow.

The live Flask server returned HTTP 200 for GET and a form POST. A Python urllib smoke check asserted both notices, the expected article identifier and preserved multiline text; the server was stopped afterward. The sandbox initially blocked the listening socket; the same command succeeded with approved local socket access. Dependency cache/index access and local Git writes also needed sandbox escalation, not changes to application behavior.

Synthetic evaluation smoke output: 3 hits / 3 eligible questions, 0 answerable abstentions / 3, 2 out-of-scope abstentions / 2. These tiny author-written fixtures are not independent evaluation and do not satisfy the required 60 external questions.

One warm-search measurement run used 100 iterations over two synthetic development questions: median 0.077655 ms, p95 0.0914051 ms, lifetime peak process RSS 45,293,568 bytes. Actual OS reported Linux 7.0.0-34-generic x86_64 with glibc 2.39; NumPy 2.5.4. This single run excludes startup/HTTP and establishes no Pi performance. Raw reports and model are in ignored artifacts/ for local review.

- Dataset SHA-256: `063f5d85102786d43513bad1f3aac8fade1024f66f81a16ded85f36597ef6008`
- Model SHA-256: `704e779cdc776387277ef9258ffe0e4d9c674eac27db941d558077fed2231a82`

Pending checks: actual Raspberry Pi installation/measurements, Python 3.10 execution (only lock resolution supplied), GitHub-hosted CI, authorized real datasets and independent testing. CI has not run remotely because nothing was pushed. No Trello access or modification was performed.
