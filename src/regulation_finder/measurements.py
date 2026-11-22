"""Warm search latency and lifetime peak process RSS on the current machine."""

import hashlib
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import numpy as np

try:
    import resource
except ImportError:  # pragma: no cover - exercised on Windows
    resource = None


def _peak_process_rss_bytes():
    if resource is not None:
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return peak if sys.platform == "darwin" else peak * 1024
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        get_current_process = ctypes.windll.kernel32.GetCurrentProcess
        get_current_process.restype = wintypes.HANDLE
        get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        ]
        get_process_memory_info.restype = wintypes.BOOL
        process = get_current_process()
        if not get_process_memory_info(process, ctypes.byref(counters), counters.cb):
            raise OSError("GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)
    return None


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
        "peak_process_rss_bytes": _peak_process_rss_bytes(),
        "procedure": "One warmup per question; cyclic sequential search calls, no HTTP/I/O. "
        "RSS is process lifetime high-water mark including imports, loading, and warmup. "
        "Peak RSS uses resource on Unix and GetProcessMemoryInfo on Windows. "
        "Hardware label is operator supplied.",
    }
