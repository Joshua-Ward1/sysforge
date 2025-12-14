from __future__ import annotations

from pathlib import Path
from typing import Any

from .checks import run_checks
from .collectors import run_collectors
from .utils import iso_timestamp, write_json_file, write_text_file


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


def _format_bytes(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{int(value):,} bytes"
    return "unknown"


def _format_percent(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value * 100:.1f}%"
    return "unknown"


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|")


def render_report_markdown(report: dict[str, Any]) -> str:
    """
    Render the combined report dictionary as Markdown.
    """
    collected = report.get("collected") or {}
    system = collected.get("system") or {}
    os_info = system.get("os") or {}
    python_info = system.get("python") or {}
    hardware = system.get("hardware") or {}
    disk = system.get("disk") or {}
    checks = report.get("checks") or {}
    results = checks.get("results") or []
    summary = checks.get("summary") or {}

    def _value(value: Any) -> str:
        if value is None or value == "":
            return "unknown"
        return str(value)

    os_parts = [str(part) for part in (os_info.get("name"), os_info.get("release")) if part]
    os_line = " ".join(os_parts) if os_parts else "unknown"
    version = os_info.get("version")
    if version:
        os_line = f"{os_line} ({version})"

    content: list[str] = [
        "# sysforge report",
        "",
        f"Generated: {_value(report.get('timestamp'))}",
        "",
        "## System",
        "",
        f"- OS: {os_line}",
        f"- Machine: {_value(os_info.get('machine'))}",
        f"- CPU count: {_value(hardware.get('cpu_count'))}",
        f"- Memory: {_format_bytes(hardware.get('memory_bytes'))}",
        "",
        "## Python",
        "",
        f"- Version: {_value(python_info.get('version'))}",
        f"- Implementation: {_value(python_info.get('implementation'))}",
        f"- Executable: {_value(python_info.get('executable'))}",
        "",
        "## Disk",
        "",
        f"- Path: {_value(disk.get('path'))}",
        f"- Free space: {_format_bytes(disk.get('free_bytes'))}",
        f"- Percent free: {_format_percent(disk.get('percent_free'))}",
        "",
        "## Doctor Results",
        "",
        "Name | Status | Message",
        "--- | --- | ---",
    ]

    for result in results:
        name = _value(result.get("name"))
        status = _value(result.get("status"))
        message = _value(result.get("message"))
        content.append(
            f"{_escape_table(name)} | {_escape_table(status)} | {_escape_table(message)}"
        )

    content.extend(
        [
            "",
            "## Summary",
            "",
            f"- Pass: {_value(summary.get('pass'))}",
            f"- Warn: {_value(summary.get('warn'))}",
            f"- Fail: {_value(summary.get('fail'))}",
        ]
    )

    markdown = "\n".join(content).rstrip()
    return f"{markdown}\n"


def write_report_markdown(report: dict[str, Any], path: Path) -> None:
    """
    Persist the Markdown rendering of a report to disk.
    """
    write_text_file(render_report_markdown(report), path)
