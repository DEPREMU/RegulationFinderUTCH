"""Warm search latency and lifetime peak process RSS on the current machine."""

import hashlib
import platform
import resource
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import numpy as np


def measure(retriever, questions, model_path, iterations, hardware_label):
    if iterations < 1 or not questions:
        raise ValueError("Measurements require questions and at least one iteration")
    for question in questions:
        retriever.search(question)
    timings = []
    for i in range(iterations):
        question = questions[i % len(questions)]
        start = perf_counter_ns()
        retriever.search(question)
        timings.append((perf_counter_ns() - start) / 1e6)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "hardware_label": hardware_label,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "not reported by OS",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "dataset_id": retriever.dataset.metadata["dataset_id"],
        "dataset_fingerprint": retriever.dataset.fingerprint,
        "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
        "synthetic": retriever.dataset.metadata["synthetic"],
        "iterations": iterations,
        "question_count": len(questions),
        "median_ms": float(np.median(timings)),
        "p95_ms": float(np.percentile(timings, 95)),
        "peak_process_rss_bytes": peak if sys.platform == "darwin" else peak * 1024,
        "procedure": "One warmup per question; cyclic sequential search calls, no HTTP/I/O. "
        "RSS is process lifetime high-water mark including imports, loading, and warmup. "
        "Unix resource units: bytes on macOS, KiB on Linux. Hardware label is operator supplied.",
    }
