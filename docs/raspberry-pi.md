# Raspberry Pi target and measurement procedure

Status: **target only, not hardware verified**. Model, CPU, RAM, architecture, OS/release, Python version, installation and hardware measurements are PENDING Betsy. Python 3.10+ is required; prefer a supported 64-bit OS with compatible NumPy wheels. Availability on the actual Pi must be checked; never assume the development host represents the Pi.

On the actual device, record board model (`cat /proc/device-tree/model` when present), `uname -a`, `cat /etc/os-release`, `lscpu`, `free -h`, `python3 --version`, power/cooling, CPU governor and background load. Avoid collecting hostnames or other personal details into public datasets. Install uv and copy the permitted repository/data offline as needed, then:

```sh
uv sync --frozen
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen pytest
uv run --frozen regulation-finder validate
uv run --frozen regulation-finder train
uv run --frozen regulation-finder web
```

Use a local browser at http://127.0.0.1:5000. If demonstrating over a trusted LAN, `web --host 0.0.0.0` exposes the demo server; record which access method was used. No cloud services, Docker or API keys are needed. Network is required for initial dependency installation unless compatible wheels/cache have already been transferred. If dependencies cannot install, record the exact error and leave compatibility pending.

```sh
uv run --frozen regulation-finder measure --iterations 100 --hardware-label 'ACTUAL verified board model and RAM' > artifacts/pi-synthetic-measurement.json
```

Replace the label with observed hardware facts; do not leave the placeholder as a claim. For authorized real data also pass global --data and --model paths before `measure`. Keep the dataset/model hashes, code commit, settings and lockfile. Label synthetic measurements even when on Pi. Repeat at least three fresh process runs with a fixed dataset, question order and iteration count; retain each raw report and describe load/power conditions.

Each run warms every development question once, then cycles sequentially through them for timed `perf_counter_ns` search calls. JSON reports median and p95 milliseconds, sample count and lifetime peak process RSS in bytes (Linux ru_maxrss KiB converted to bytes). RSS includes interpreter/imports/loading/warmup; it is not incremental model memory. Timing excludes startup, file loading, HTTP and browser rendering. Measure these separately if needed and describe the new procedure. No latency or memory limits are invented here.

Local development runs are evidence only about the host where they ran. Raspberry Pi latency, RSS, installation and live demo verification remain pending until performed on that device.
