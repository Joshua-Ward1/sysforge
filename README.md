# sysforge

Modular system diagnostics and analysis CLI. Collects environment data, runs health checks, and writes structured reports for debugging and development workflows.

## Features
- `sysforge collect`: JSON snapshot of OS, Python, hardware, disk usage, safe env summary, timestamp.
- `sysforge doctor`: Runs checks (disk space threshold, git installed, Python >= 3.11) with pass/warn/fail.
- `sysforge report`: Collect + doctor, writes `sysforge-report.json`, prints a short summary.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

## Usage
```bash
sysforge --version
sysforge collect --pretty
sysforge collect --output ./collection.json
sysforge doctor --disk-threshold 0.1
sysforge report --output ./sysforge-report.json --pretty
```

Example `sysforge collect --pretty`:
```json
{
  "timestamp": "2025-01-01T00:00:00+00:00",
  "os": {"name": "Darwin", "release": "23.0", "version": "...", "platform": "...", "machine": "arm64"},
  "python": {"version": "3.11.8", "implementation": "CPython", "executable": "/usr/bin/python3"},
  "hardware": {"cpu_count": 8, "memory_bytes": 17179869184},
  "disk": {"path": "/Users/me", "total_bytes": 500000000000, "used_bytes": 200000000000, "free_bytes": 300000000000, "percent_free": 0.60},
  "environment": {"allowed": {"PATH": "/usr/bin:..."}, "total_count": 42}
}
```

Example `sysforge doctor` output:
```json
{
  "results": [
    {"name": "disk_space", "status": "pass", "message": "Disk space healthy: 60.00% free", "data": {"path": "/Users/me", "total_bytes": 500000000000, "used_bytes": 200000000000, "free_bytes": 300000000000, "percent_free": 0.6}},
    {"name": "git_installed", "status": "pass", "message": "git is available in PATH."},
    {"name": "python_version", "status": "pass", "message": "Python 3.11.8 meets requirement (>=3.11)."}
  ],
  "summary": {"pass": 3, "warn": 0, "fail": 0}
}
```

Exit codes (for `sysforge doctor` and `sysforge report`):
- `0`: all checks pass (`warn=0`, `fail=0`)
- `1`: warnings only (`warn>0`, `fail=0`)
- `2`: any failures (`fail>0`) OR malformed / missing summary data

## Development
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pip install -U pre-commit
pre-commit install
pre-commit run --all-files  # optional: run on demand
```

Run the same checks locally that CI performs:
```bash
python -m ruff format --check .
python -m ruff check .
python -m pytest -q
sysforge --version
```
