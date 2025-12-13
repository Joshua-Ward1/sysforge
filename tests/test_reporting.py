from __future__ import annotations

import pytest

from sysforge.reporting import assemble_report


def test_assemble_report_calls_collectors_and_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sysforge.reporting.iso_timestamp", lambda: "2024-01-01T00:00:00Z")
    monkeypatch.setattr("sysforge.reporting.run_collectors", lambda: {"collected": True})

    calls: dict[str, float] = {}

    def fake_run_checks(*, disk_threshold: float) -> dict[str, object]:
        calls["disk_threshold"] = disk_threshold
        return {"checks": True}

    monkeypatch.setattr("sysforge.reporting.run_checks", fake_run_checks)

    report = assemble_report(disk_threshold=0.2)

    assert set(report.keys()) == {"timestamp", "collected", "checks"}
    assert report["timestamp"] == "2024-01-01T00:00:00Z"
    assert report["collected"] == {"collected": True}
    assert report["checks"] == {"checks": True}
    assert calls["disk_threshold"] == 0.2
