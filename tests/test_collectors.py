from __future__ import annotations

from pathlib import Path

import pytest

from sysforge.collectors import get_collectors, register_collector
from sysforge.collectors.base import BaseCollector
from sysforge.collectors.system import SystemCollector


def test_system_collector_collects_expected_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    disk_call: dict[str, Path] = {}
    env_call: dict[str, list[str]] = {}
    expected_disk = {"path": "/home/test", "percent_free": 0.5}
    expected_env = {"allowed": {"PATH": "/bin"}, "total_count": 2}
    expected_env_keys = ["PATH", "SHELL", "TERM", "LANG", "HOME", "USER", "USERNAME", "LOGNAME"]

    monkeypatch.setattr("sysforge.collectors.system.iso_timestamp", lambda: "2024-01-01T00:00:00Z")
    monkeypatch.setattr("sysforge.collectors.system.platform.system", lambda: "TestOS")
    monkeypatch.setattr("sysforge.collectors.system.platform.release", lambda: "1.0")
    monkeypatch.setattr("sysforge.collectors.system.platform.version", lambda: "build-xyz")
    monkeypatch.setattr("sysforge.collectors.system.platform.platform", lambda: "TestOS-1.0")
    monkeypatch.setattr("sysforge.collectors.system.platform.machine", lambda: "x86_64")
    monkeypatch.setattr("sysforge.collectors.system.platform.python_version", lambda: "3.11.5")
    monkeypatch.setattr("sysforge.collectors.system.platform.python_implementation", lambda: "CPython")
    monkeypatch.setattr("sysforge.collectors.system.sys.executable", "/usr/bin/python")
    monkeypatch.setattr("sysforge.collectors.system.os.cpu_count", lambda: 8)
    monkeypatch.setattr("sysforge.collectors.system.memory_bytes", lambda: 1024)

    def fake_disk_usage(path: Path) -> dict[str, object]:
        disk_call["path"] = path
        return expected_disk

    def fake_env_summary(keys: list[str]) -> dict[str, object]:
        env_call["keys"] = keys
        return expected_env

    monkeypatch.setattr("sysforge.collectors.system.disk_usage_summary", fake_disk_usage)
    monkeypatch.setattr("sysforge.collectors.system.safe_env_summary", fake_env_summary)

    payload = SystemCollector().collect()

    assert set(payload.keys()) == {"timestamp", "os", "python", "hardware", "disk", "environment"}
    assert payload["timestamp"] == "2024-01-01T00:00:00Z"
    assert payload["os"] == {
        "name": "TestOS",
        "release": "1.0",
        "version": "build-xyz",
        "platform": "TestOS-1.0",
        "machine": "x86_64",
    }
    assert payload["python"] == {
        "version": "3.11.5",
        "implementation": "CPython",
        "executable": "/usr/bin/python",
    }
    assert payload["hardware"] == {"cpu_count": 8, "memory_bytes": 1024}
    assert payload["disk"] == expected_disk
    assert payload["environment"] == expected_env
    assert env_call["keys"] == expected_env_keys
    assert disk_call["path"] == Path.home()


def test_system_collector_omits_memory_when_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sysforge.collectors.system.iso_timestamp", lambda: "ts")
    monkeypatch.setattr("sysforge.collectors.system.platform.system", lambda: "TestOS")
    monkeypatch.setattr("sysforge.collectors.system.platform.release", lambda: "1.0")
    monkeypatch.setattr("sysforge.collectors.system.platform.version", lambda: "build")
    monkeypatch.setattr("sysforge.collectors.system.platform.platform", lambda: "TestOS-1.0")
    monkeypatch.setattr("sysforge.collectors.system.platform.machine", lambda: "arm64")
    monkeypatch.setattr("sysforge.collectors.system.platform.python_version", lambda: "3.11.5")
    monkeypatch.setattr("sysforge.collectors.system.platform.python_implementation", lambda: "CPython")
    monkeypatch.setattr("sysforge.collectors.system.sys.executable", "/usr/bin/python")
    monkeypatch.setattr("sysforge.collectors.system.os.cpu_count", lambda: 4)
    monkeypatch.setattr("sysforge.collectors.system.memory_bytes", lambda: None)
    monkeypatch.setattr(
        "sysforge.collectors.system.disk_usage_summary",
        lambda path: {"path": str(path), "percent_free": 0.9},
    )
    monkeypatch.setattr(
        "sysforge.collectors.system.safe_env_summary",
        lambda keys: {"allowed": {}, "total_count": len(keys)},
    )

    payload = SystemCollector().collect()

    assert payload["hardware"] == {"cpu_count": 4}
    assert "memory_bytes" not in payload["hardware"]


class DummyCollector(BaseCollector):
    name = "dummy"

    def collect(self) -> dict[str, object]:
        return {"dummy": True}


def test_register_collector_warns_on_duplicate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sysforge.collectors._collector_registry", [])
    collector = DummyCollector()

    register_collector(collector)
    with pytest.warns(UserWarning, match="already registered"):
        register_collector(collector)

    assert get_collectors() == [collector]
