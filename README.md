# sysforge

A modular system diagnostics and analysis CLI for collecting environment data, running health checks, and generating structured reports for debugging and development workflows.

## Features

* **`sysforge collect`**
  Collects a structured JSON snapshot of:

  * OS and platform details
  * Python runtime
  * Hardware (CPU, memory)
  * Disk usage
  * Safe environment variable summary
  * Timestamp

* **`sysforge doctor`**
  Runs health checks with `pass` / `warn` / `fail` statuses:

  * Disk space threshold
  * Git availability
  * Python version (>= 3.11)

* **`sysforge report`**
  Runs `collect` + `doctor`, writes a JSON report, and prints a short summary.

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Usage

### Version

```bash
sysforge --version
```

### Collect

```bash
sysforge collect --pretty
sysforge collect --output ./collection.json
```

### Doctor

```bash
sysforge doctor --disk-threshold 0.1
```

### Report

```bash
sysforge report --output ./sysforge-report.json --pretty
```

---

## Example: `sysforge collect --pretty`

```json
{
  "timestamp": "2025-01-01T00:00:00+00:00",
  "os": {
    "name": "Darwin",
    "release": "23.0",
    "version": "...",
    "platform": "...",
    "machine": "arm64"
  },
  "python": {
    "version": "3.11.8",
    "implementation": "CPython",
    "executable": "/usr/bin/python3"
  },
  "hardware": {
    "cpu_count": 8,
    "memory_bytes": 17179869184
  },
  "disk": {
    "path": "/Users/me",
    "total_bytes": 500000000000,
    "used_bytes": 200000000000,
    "free_bytes": 300000000000,
    "percent_free": 0.60
  },
  "environment": {
    "allowed": {
      "PATH": "/usr/bin:..."
    },
    "total_count": 42
  }
}
```

---

## Example: `sysforge doctor`

```json
{
  "results": [
    {
      "name": "disk_space",
      "status": "pass",
      "message": "Disk space healthy: 60.00% free"
    },
    {
      "name": "git_installed",
      "status": "pass",
      "message": "git is available in PATH."
    },
    {
      "name": "python_version",
      "status": "pass",
      "message": "Python 3.11.8 meets requirement (>=3.11)."
    }
  ],
  "summary": {
    "pass": 3,
    "warn": 0,
    "fail": 0
  }
}
```

---

## Disk Space Check Contract

The disk space check uses explicit, deterministic boundaries:

Let:

* `disk_threshold` = user-provided threshold (default: `0.10`)
* `WARN_THRESHOLD_MARGIN` = internal margin (default: `0.05`)
* `warn_limit = min(disk_threshold + WARN_THRESHOLD_MARGIN, 1.0)`

Then:

* `percent_free <= disk_threshold` → **fail**
* `disk_threshold < percent_free <= warn_limit` → **warn**
* `percent_free > warn_limit` → **pass**

This ensures predictable behavior at boundary values.

---

## Exit Codes

Used by both `sysforge doctor` and `sysforge report`:

| Exit Code | Meaning                                    |
| --------- | ------------------------------------------ |
| `0`       | All checks pass                            |
| `1`       | Warnings only                              |
| `2`       | Any failures **or malformed summary data** |

---

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pre-commit install
pre-commit run --all-files
ruff check .
pytest
```

---

## Design Goals

* Deterministic, machine-readable output
* Minimal dependencies
* Cross-platform behavior
* Safe-by-default environment inspection
* Easy to embed in CI and debugging workflows

---

## License

MIT License
