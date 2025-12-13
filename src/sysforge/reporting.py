from __future__ import annotations

from pathlib import Path
from typing import Any

from .checks import run_checks
from .collectors import run_collectors
from .utils import iso_timestamp, write_json_file


def assemble_report(*, disk_threshold: float = 0.10) -> dict[str, Any]:
    """
    Collect system data and run health checks in a single payload.
    """
    collected = run_collectors()
    checks = run_checks(disk_threshold=disk_threshold)
    return {
        "timestamp": iso_timestamp(),
        "collected": collected,
        "checks": checks,
    }


def write_report_file(data: dict[str, Any], path: Path, *, pretty: bool = False) -> None:
    """
    Persist report data to disk.
    """
    write_json_file(data, path, pretty=pretty)
