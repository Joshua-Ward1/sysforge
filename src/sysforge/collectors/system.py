from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any

from ..utils import disk_usage_summary, iso_timestamp, memory_bytes, safe_env_summary
from .base import BaseCollector


class SystemCollector(BaseCollector):
    name = "system"

    def collect(self) -> dict[str, Any]:
        os_info = {
            "name": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        }
        python_info = {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": os.fsdecode(sys.executable) if sys.executable is not None else None,
        }
        hardware: dict[str, Any] = {"cpu_count": os.cpu_count()}
        mem_bytes = memory_bytes()
        if mem_bytes is not None:
            hardware["memory_bytes"] = mem_bytes

        disk_info = disk_usage_summary(Path.home())
        env_info = safe_env_summary(
            ["PATH", "SHELL", "TERM", "LANG", "HOME", "USER", "USERNAME", "LOGNAME"]
        )

        return {
            "timestamp": iso_timestamp(),
            "os": os_info,
            "python": python_info,
            "hardware": hardware,
            "disk": disk_info,
            "environment": env_info,
        }
