from __future__ import annotations

import json
import os
import shutil
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def json_dump(data: Any, *, pretty: bool = False) -> str:
    """
    Serialize data to JSON with optional indentation.
    """
    return json.dumps(data, indent=2 if pretty else None, default=str)


def write_json_file(data: Any, path: Path, *, pretty: bool = False) -> None:
    """
    Write JSON data to disk, creating parent directories if needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_dump(data, pretty=pretty))


def write_text_file(text: str, path: Path) -> None:
    """
    Write raw text data to disk, creating parent directories if needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def iso_timestamp() -> str:
    """
    Return an ISO 8601 timestamp in UTC.
    """
    return datetime.now(UTC).isoformat()


def safe_env_summary(allowlist: Iterable[str]) -> dict[str, Any]:
    """
    Return a safe environment summary with an allowlisted subset of keys and total count.
    """
    env = os.environ
    allowed = {key: env[key] for key in allowlist if key in env}
    return {
        "allowed": allowed,
        "total_count": len(env),
    }


def memory_bytes() -> int | None:
    """
    Best-effort physical memory detection using stdlib only.
    Returns None if unavailable.
    """
    if hasattr(os, "sysconf"):
        try:
            page_size = os.sysconf("SC_PAGE_SIZE")  # type: ignore[attr-defined]
            phys_pages = os.sysconf("SC_PHYS_PAGES")  # type: ignore[attr-defined]
            if isinstance(page_size, int) and isinstance(phys_pages, int):
                return page_size * phys_pages
        except (ValueError, OSError, AttributeError):
            pass

    if sys.platform.startswith("win"):
        try:
            import ctypes

            class MemoryStatus(ctypes.Structure):  # type: ignore[misc]
                _fields_ = [
                    ("length", ctypes.c_uint32),
                    ("memory_load", ctypes.c_uint32),
                    ("total_physical", ctypes.c_uint64),
                    ("avail_physical", ctypes.c_uint64),
                    ("total_page_file", ctypes.c_uint64),
                    ("avail_page_file", ctypes.c_uint64),
                    ("total_virtual", ctypes.c_uint64),
                    ("avail_virtual", ctypes.c_uint64),
                    ("avail_extended", ctypes.c_uint64),
                ]

            status = MemoryStatus()
            status.length = ctypes.sizeof(MemoryStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))  # type: ignore[attr-defined]
            return int(status.total_physical)
        except Exception:
            return None

    return None


def disk_usage_summary(path: Path) -> dict[str, Any]:
    """
    Return total/used/free and percent free for the given path.
    """
    usage = shutil.disk_usage(path)
    total = usage.total
    free = usage.free
    used = usage.used
    percent_free = (free / total) if total else 0.0
    return {
        "path": str(path),
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
        "percent_free": percent_free,
    }
