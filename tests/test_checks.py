from __future__ import annotations

from types import SimpleNamespace

import pytest

from sysforge.checks.core import DiskSpaceCheck, GitInstalledCheck, PythonVersionCheck


def test_python_version_check_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sysforge.checks.core.sys.version_info",
        SimpleNamespace(major=3, minor=11, micro=0),
    )
    result = PythonVersionCheck().run(disk_threshold=0.1)
    assert result.status == "pass"


def test_python_version_check_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sysforge.checks.core.sys.version_info",
        SimpleNamespace(major=3, minor=10, micro=9),
    )
    result = PythonVersionCheck().run(disk_threshold=0.1)
    assert result.status == "fail"


def test_git_installed_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sysforge.checks.core.shutil.which", lambda _: "/usr/bin/git")
    result = GitInstalledCheck().run(disk_threshold=0.1)
    assert result.status == "pass"


def test_disk_space_check_statuses(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_usage(percent_free: float) -> dict[str, float]:
        return {
            "path": "/tmp",
            "total_bytes": 100,
            "used_bytes": 50,
            "free_bytes": 50,
            "percent_free": percent_free,
        }

    monkeypatch.setattr(
        "sysforge.checks.core.disk_usage_summary",
        lambda _: fake_usage(0.02),
    )
    assert DiskSpaceCheck().run(disk_threshold=0.1).status == "fail"

    monkeypatch.setattr(
        "sysforge.checks.core.disk_usage_summary",
        lambda _: fake_usage(0.12),
    )
    assert DiskSpaceCheck().run(disk_threshold=0.1).status == "warn"

    monkeypatch.setattr(
        "sysforge.checks.core.disk_usage_summary",
        lambda _: fake_usage(0.5),
    )
    assert DiskSpaceCheck().run(disk_threshold=0.1).status == "pass"
