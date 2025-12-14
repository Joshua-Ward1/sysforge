from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from sysforge import utils


class FakeDiskUsage:
    def __init__(self, total: int, used: int, free: int) -> None:
        self.total = total
        self.used = used
        self.free = free


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


def shutil_fake_usage(total: int, used: int, free: int) -> FakeDiskUsage:
    return FakeDiskUsage(total, used, free)


def test_json_dump_pretty_and_default_serializer() -> None:
    class Custom:
        def __str__(self) -> str:
            return "custom"

    compact = utils.json_dump({"a": Custom()}, pretty=False)
    pretty = utils.json_dump({"a": Custom()}, pretty=True)

    assert compact == '{"a": "custom"}'
    assert pretty == '{\n  "a": "custom"\n}'


def test_write_json_file_creates_parents(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "file.json"
    utils.write_json_file({"hello": "world"}, target, pretty=True)

    assert target.exists()
    assert target.read_text() == '{\n  "hello": "world"\n}'


def test_memory_bytes_windows_path(monkeypatch: pytest.MonkeyPatch) -> None:
    import types

    # Force non-windows branch to fail so we hit windows path.
    def _raise_sysconf(*_args, **_kwargs):
        raise AttributeError()

    monkeypatch.setattr(utils.os, "sysconf", _raise_sysconf)
    monkeypatch.setattr(utils.sys, "platform", "win32")

    fake_ctypes = types.ModuleType("ctypes")
    fake_ctypes.c_uint32 = int
    fake_ctypes.c_uint64 = int

    class FakeStructure:
        pass

    def fake_sizeof(_cls: object) -> int:
        return 0

    def fake_byref(obj: object) -> object:
        return obj

    class FakeKernel32:
        def GlobalMemoryStatusEx(self, status: object) -> None:
            status.total_physical = 1234

    fake_ctypes.Structure = FakeStructure
    fake_ctypes.sizeof = fake_sizeof
    fake_ctypes.byref = fake_byref
    fake_ctypes.windll = types.SimpleNamespace(kernel32=FakeKernel32())

    monkeypatch.setitem(sys.modules, "ctypes", fake_ctypes)

    result = utils.memory_bytes()
    assert result == 1234
