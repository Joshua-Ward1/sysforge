from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from sysforge.cli import app

runner = CliRunner()


def test_collect_writes_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("sysforge.cli.run_collectors", lambda: {"hello": "world"})
    out_path = tmp_path / "collect.json"

    result = runner.invoke(app, ["collect", "--output", str(out_path)])
    assert result.exit_code == 0
    payload = json.loads(out_path.read_text())
    assert payload == {"hello": "world"}


def test_doctor_success_exit(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": {"pass": 1, "warn": 0, "fail": 0}},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "summary" in result.stdout.lower()


def test_doctor_failure_exit(monkeypatch) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": {"pass": 0, "warn": 0, "fail": 1}},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 2


def test_doctor_warn_exit(monkeypatch) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": {"pass": 0, "warn": 1, "fail": 0}},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1


def test_doctor_malformed_summary_not_dict_exits_2(monkeypatch) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": None},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 2


def test_doctor_malformed_summary_string_exits_2(monkeypatch) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": "bad"},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 2


def test_doctor_malformed_summary_bool_values_exits_2(monkeypatch) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": {"pass": 0, "warn": True, "fail": False}},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 2


def test_doctor_malformed_summary_missing_keys_exits_2(monkeypatch) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": {}},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 2


def test_doctor_malformed_summary_wrong_types_exits_2(monkeypatch) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": {"warn": "1", "fail": 0}},
    )
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 2


def test_doctor_respects_pretty_option(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sysforge.cli.run_checks",
        lambda disk_threshold: {"results": [], "summary": {"pass": 1, "warn": 0, "fail": 0}},
    )
    out_path = tmp_path / "doctor.json"

    result = runner.invoke(app, ["doctor", "--output", str(out_path), "--pretty"])
    assert result.exit_code == 0
    content = out_path.read_text()
    assert content.startswith("{\n")
    assert '  "summary"' in content


def test_report_writes_combined(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sysforge.cli.assemble_report",
        lambda disk_threshold: {
            "timestamp": "2025-01-01T00:00:00Z",
            "collected": {"ok": True},
            "checks": {"results": [], "summary": {"pass": 1, "warn": 0, "fail": 0}},
        },
    )
    report_path = tmp_path / "report.json"
    result = runner.invoke(app, ["report", "--output", str(report_path), "--pretty"])
    assert result.exit_code == 0
    data = json.loads(report_path.read_text())
    assert data["collected"]["ok"] is True
    assert "summary" in result.stderr.lower()


def test_report_warn_exit(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sysforge.cli.assemble_report",
        lambda disk_threshold: {
            "timestamp": "2025-01-01T00:00:00Z",
            "collected": {"ok": True},
            "checks": {"results": [], "summary": {"pass": 0, "warn": 1, "fail": 0}},
        },
    )
    report_path = tmp_path / "report.json"
    result = runner.invoke(app, ["report", "--output", str(report_path)])
    assert result.exit_code == 1
    assert report_path.exists()


def test_report_fail_exit(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sysforge.cli.assemble_report",
        lambda disk_threshold: {
            "timestamp": "2025-01-01T00:00:00Z",
            "collected": {"ok": True},
            "checks": {"results": [], "summary": {"pass": 0, "warn": 0, "fail": 1}},
        },
    )
    report_path = tmp_path / "report.json"
    result = runner.invoke(app, ["report", "--output", str(report_path)])
    assert result.exit_code == 2
    assert report_path.exists()


def test_report_malformed_summary_exits_2_and_writes_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sysforge.cli.assemble_report",
        lambda disk_threshold: {
            "timestamp": "2025-01-01T00:00:00Z",
            "collected": {"ok": True},
            "checks": {"results": [], "summary": {}},
        },
    )
    report_path = tmp_path / "report.json"
    result = runner.invoke(app, ["report", "--output", str(report_path)])
    assert result.exit_code == 2
    assert report_path.exists()


def test_report_markdown_output(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("sysforge.reporting.iso_timestamp", lambda: "2024-01-01T00:00:00Z")
    monkeypatch.setattr(
        "sysforge.reporting.run_collectors",
        lambda: {
            "system": {
                "os": {"name": "TestOS", "release": "1.0", "version": "build-1", "machine": "x86"},
                "python": {
                    "version": "3.11.0",
                    "implementation": "CPython",
                    "executable": "/usr/bin/python",
                },
                "hardware": {"cpu_count": 4, "memory_bytes": 1024},
                "disk": {"path": "/tmp", "free_bytes": 500, "percent_free": 0.5},
            }
        },
    )

    def fake_run_checks(*, disk_threshold: float) -> dict[str, object]:
        return {
            "results": [
                {"name": "disk", "status": "pass", "message": "ok"},
                {"name": "python", "status": "pass", "message": "current"},
            ],
            "summary": {"pass": 2, "warn": 0, "fail": 0},
        }

    monkeypatch.setattr("sysforge.reporting.run_checks", fake_run_checks)

    out_path = tmp_path / "report.md"
    result = runner.invoke(app, ["report", "--format", "md", "--output", str(out_path)])
    assert result.exit_code == 0
    content = out_path.read_text()
    assert "# sysforge report" in content
    assert "## System" in content
    assert "## Python" in content
    assert "## Doctor Results" in content
    assert "## Summary" in content


def test_report_rejects_invalid_format() -> None:
    result = runner.invoke(app, ["report", "--format", "xml"])
    assert result.exit_code != 0
    assert "format must be either" in result.stderr
    assert "'json' or 'md'" in result.stderr
