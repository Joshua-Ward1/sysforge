from __future__ import annotations

from .base import BaseCollector

_collector_registry: list[BaseCollector] = []


def register_collector(collector: BaseCollector) -> None:
    """
    Register a collector instance.
    """
    if any(existing.name == collector.name for existing in _collector_registry):
        return
    _collector_registry.append(collector)


def get_collectors() -> list[BaseCollector]:
    """
    Return registered collectors.
    """
    return list(_collector_registry)


def run_collectors() -> dict[str, object]:
    """
    Execute all collectors and combine results keyed by collector name.
    """
    results: dict[str, object] = {}
    for collector in get_collectors():
        results[collector.name] = collector.collect()
    return results


# Register built-in collectors
from .system import SystemCollector  # noqa: E402

register_collector(SystemCollector())
