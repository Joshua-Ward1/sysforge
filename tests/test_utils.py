from __future__ import annotations

import os
from pathlib import Path

import pytest

from sysforge import utils


def test_safe_env_summary_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", "/tmp/bin")
    monkeypatch.setenv("USER", "tester")
    monkeypatch.setenv("SECRET_TOKEN", "hidden")

    summary = utils.safe_env_summary(["PATH", "USER"])
    assert summary["allowed"]["PATH"] == "/tmp/bin"
    assert "USER" in summary["allowed"]
    assert "SECRET_TOKEN" not in summary["allowed"]
    assert summary["total_count"] == len(os.environ)


def test_disk_usage_summary_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_usage = shutil_fake_usage(total=1000, used=400, free=600)

    monkeypatch.setattr(utils.shutil, "disk_usage", lambda _: fake_usage)
    result = utils.disk_usage_summary(tmp_path)

    assert set(result.keys()) == {
        "path",
        "total_bytes",
        "used_bytes",
        "free_bytes",
        "percent_free",
    }
    assert result["path"] == str(tmp_path)
    assert result["percent_free"] == pytest.approx(0.6)


def shutil_fake_usage(total: int, used: int, free: int):
    class Usage:
        def __init__(self, total: int, used: int, free: int):
            self.total = total
            self.used = used
            self.free = free

    return Usage(total, used, free)
