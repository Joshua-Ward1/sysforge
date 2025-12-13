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
pip install -e ".[dev]"
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

## Development
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
ruff check .
pytest
```

## Next steps
- Add more collectors (network, GPU, package manager info) and checks (network reachability, service statuses).
- Add configurable thresholds and profiles for CI vs. local runs.
- Export additional formats (Markdown summary) and optional anonymization.
