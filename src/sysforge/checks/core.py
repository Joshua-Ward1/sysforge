from __future__ import annotations

import shutil
import sys
from pathlib import Path

from ..utils import disk_usage_summary
from .base import BaseCheck, CheckResult

WARN_THRESHOLD_MARGIN = 0.05


class DiskSpaceCheck(BaseCheck):
    name = "disk_space"

    def run(self, *, disk_threshold: float = 0.10) -> CheckResult:
        usage = disk_usage_summary(Path.home())
        percent_free = usage["percent_free"]

        if percent_free <= disk_threshold:
            status = "fail"
            message = f"Low disk space: {percent_free:.2%} free (<= {disk_threshold:.0%})"
        elif percent_free <= disk_threshold + WARN_THRESHOLD_MARGIN:
            status = "warn"
            message = f"Disk space is getting low: {percent_free:.2%} free"
        else:
            status = "pass"
            message = f"Disk space healthy: {percent_free:.2%} free"

        return CheckResult(name=self.name, status=status, message=message, data=usage)


class GitInstalledCheck(BaseCheck):
    name = "git_installed"

    def run(self, *, disk_threshold: float = 0.10) -> CheckResult:  # disk_threshold unused
        found = shutil.which("git") is not None
        if found:
            return CheckResult(
                name=self.name,
                status="pass",
                message="git is available in PATH.",
            )
        return CheckResult(
            name=self.name,
            status="fail",
            message="git is not available in PATH.",
        )


class PythonVersionCheck(BaseCheck):
    name = "python_version"

    def run(self, *, disk_threshold: float = 0.10) -> CheckResult:  # disk_threshold unused
        version_info = sys.version_info
        meets_requirement = version_info.major > 3 or (
            version_info.major == 3 and version_info.minor >= 11
        )
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        if meets_requirement:
            return CheckResult(
                name=self.name,
                status="pass",
                message=f"Python {version_str} meets requirement (>=3.11).",
            )
        return CheckResult(
            name=self.name,
            status="fail",
            message=f"Python {version_str} is below required 3.11.",
        )
