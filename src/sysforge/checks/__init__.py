from __future__ import annotations

from .base import BaseCheck

_check_registry: list[BaseCheck] = []


def register_check(check: BaseCheck) -> None:
    """
    Register a check instance.
    """
    if any(existing.name == check.name for existing in _check_registry):
        return
    _check_registry.append(check)


def get_checks() -> list[BaseCheck]:
    """
    Return registered checks.
    """
    return list(_check_registry)


def run_checks(*, disk_threshold: float = 0.10) -> dict[str, object]:
    """
    Execute all registered checks and return results plus summary counts.
    """
    summary = {"pass": 0, "warn": 0, "fail": 0}
    results: list[dict[str, object]] = []
    for check in get_checks():
        result = check.run(disk_threshold=disk_threshold)
        results.append(result.to_dict())
        summary[result.status] += 1
    return {"results": results, "summary": summary}


# Register built-in checks
from .core import DiskSpaceCheck, GitInstalledCheck, PythonVersionCheck  # noqa: E402

register_check(DiskSpaceCheck())
register_check(GitInstalledCheck())
register_check(PythonVersionCheck())
