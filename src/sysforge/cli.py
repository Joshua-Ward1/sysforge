from __future__ import annotations

import sys
from pathlib import Path

import typer

from . import __version__
from .checks import run_checks
from .collectors import run_collectors
from .reporting import assemble_report, write_report_file, write_report_markdown
from .utils import json_dump

app = typer.Typer(
    add_completion=False,
    help="sysforge — collect environment data, run health checks, and write reports.",
)

def _exit_code_from_summary(summary: object) -> int:
    """Map doctor `summary` to CLI exit codes.

    - 0: all checks pass
    - 1: warnings only
    - 2: failures OR malformed/missing summary data
    """
    if not isinstance(summary, dict):
        return 2
    warn = summary.get("warn")
    fail = summary.get("fail")
    if (
        not isinstance(warn, int)
        or isinstance(warn, bool)
        or not isinstance(fail, int)
        or isinstance(fail, bool)
    ):
        return 2
    if fail > 0:
        return 2
    if warn > 0:
        return 1
    return 0


def _validate_threshold(value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise typer.BadParameter("disk-threshold must be between 0.0 and 1.0")
    return value


def _validate_report_format(value: str) -> str:
    normalized = value.lower()
    if normalized not in {"json", "md"}:
        raise typer.BadParameter("format must be either 'json' or 'md'")
    return normalized


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the sysforge version and exit.",
        is_eager=True,
    ),
) -> None:
    """
    Entry callback to support --version.
    """
    if version:
        typer.echo(f"sysforge {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def collect(
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output."),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional file path to write the JSON collection.",
        path_type=Path,
    ),
) -> None:
    """
    Collect system information and emit JSON.
    """
    try:
        data = run_collectors()
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"Error collecting system info: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if output:
        try:
            write_report_file(data, output, pretty=pretty)
            typer.echo(f"Wrote collection to {output}")
        except Exception as exc:  # pragma: no cover - defensive
            typer.echo(f"Failed to write output: {exc}", err=True)
            raise typer.Exit(code=1) from exc
    else:
        typer.echo(json_dump(data, pretty=pretty))


@app.command()
def doctor(
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output."),
    disk_threshold: float = typer.Option(
        0.10,
        "--disk-threshold",
        min=0.0,
        max=1.0,
        callback=_validate_threshold,
        help="Minimum free disk fraction before warning/fail.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional file path to write the JSON check results.",
        path_type=Path,
    ),
) -> None:
    """
    Run health checks and report pass/warn/fail statuses.
    """
    try:
        checks = run_checks(disk_threshold=disk_threshold)
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"Error running checks: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if output:
        try:
            write_report_file(checks, output, pretty=pretty)
            typer.echo(f"Wrote doctor results to {output}")
        except Exception as exc:  # pragma: no cover - defensive
            typer.echo(f"Failed to write output: {exc}", err=True)
            raise typer.Exit(code=1) from exc
    else:
        typer.echo(json_dump(checks, pretty=pretty))

    exit_code = _exit_code_from_summary(checks.get("summary"))
    if exit_code:
        raise typer.Exit(code=exit_code)


@app.command()
def report(
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="File path for the combined report.",
        path_type=Path,
    ),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON in the file."),
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Report output format.",
        callback=_validate_report_format,
    ),
    disk_threshold: float = typer.Option(
        0.10,
        "--disk-threshold",
        min=0.0,
        max=1.0,
        callback=_validate_threshold,
        help="Minimum free disk fraction before warning/fail.",
    ),
) -> None:
    """
    Collect system data, run checks, and write a combined report.
    """
    report_format = output_format

    try:
        report_data = assemble_report(disk_threshold=disk_threshold)
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"Error generating report: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    output_path = output
    if output_path is None:
        default_name = "sysforge-report.md" if report_format == "md" else "sysforge-report.json"
        output_path = Path(default_name)

    try:
        if report_format == "md":
            write_report_markdown(report_data, output_path)
        else:
            write_report_file(report_data, output_path, pretty=pretty)
        typer.echo(f"Wrote report to {output_path}")
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"Failed to write report: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    try:
        summary = report_data["checks"]["summary"]
        typer.echo(
            f"Summary: {summary['pass']} pass, {summary['warn']} warn, {summary['fail']} fail",
            file=sys.stderr,
        )
    except Exception as exc:
        raise typer.Exit(code=2) from exc

    exit_code = _exit_code_from_summary(summary)
    if exit_code:
        raise typer.Exit(code=exit_code)
