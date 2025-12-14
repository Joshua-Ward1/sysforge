from __future__ import annotations

from pathlib import Path

import pytest

from sysforge.reporting import assemble_report, render_report_markdown, write_report_markdown


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


def test_write_report_file_delegates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called: dict[str, object] = {}

    def fake_write_json_file(data, path, *, pretty: bool) -> None:
        called["data"] = data
        called["path"] = path
        called["pretty"] = pretty

    monkeypatch.setattr("sysforge.reporting.write_json_file", fake_write_json_file)
    target = tmp_path / "out.json"

    sample = {"a": 1}
    from sysforge.reporting import write_report_file

    write_report_file(sample, target, pretty=True)

    assert called == {"data": sample, "path": target, "pretty": True}


def test_render_report_markdown_includes_sections() -> None:
    report = {
        "timestamp": "2024-01-02T03:04:05Z",
        "collected": {
            "system": {
                "os": {"name": "TestOS", "release": "1.0", "version": "build-1", "machine": "x86"},
                "python": {
                    "version": "3.11.0",
                    "implementation": "CPython",
                    "executable": "/usr/bin/python",
                },
                "hardware": {"cpu_count": 8, "memory_bytes": 16_000_000_000},
                "disk": {"path": "/data", "free_bytes": 1000, "percent_free": 0.5},
            }
        },
        "checks": {
            "results": [
                {"name": "disk", "status": "pass", "message": "ok"},
                {"name": "python", "status": "warn", "message": "old"},
            ],
            "summary": {"pass": 1, "warn": 1, "fail": 0},
        },
    }

    rendered = render_report_markdown(report)

    assert "# sysforge report" in rendered
    assert "Generated: 2024-01-02T03:04:05Z" in rendered
    assert "## System" in rendered
    assert "- OS: TestOS 1.0 (build-1)" in rendered
    assert "## Python" in rendered
    assert "## Disk" in rendered
    assert "## Doctor Results" in rendered
    assert "disk | pass | ok" in rendered
    assert "## Summary" in rendered
    assert "- Warn: 1" in rendered


def test_write_report_markdown_delegates_to_text_writer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    called: dict[str, object] = {}

    def fake_render(report: dict[str, object]) -> str:
        called["report"] = report
        return "content"

    def fake_write_text(text: str, path: Path) -> None:
        called["text"] = text
        called["path"] = path

    monkeypatch.setattr("sysforge.reporting.render_report_markdown", fake_render)
    monkeypatch.setattr("sysforge.reporting.write_text_file", fake_write_text)

    target = tmp_path / "out.md"
    sample = {"checks": {}}
    write_report_markdown(sample, target)

    assert called["report"] == sample
    assert called["text"] == "content"
    assert called["path"] == target
