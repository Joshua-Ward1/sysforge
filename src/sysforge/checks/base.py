from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

CheckStatus = Literal["pass", "warn", "fail"]


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }
        if self.data is not None:
            payload["data"] = self.data
        return payload


class BaseCheck(ABC):
    name: str

    @abstractmethod
    def run(self, *, disk_threshold: float) -> CheckResult:
        raise NotImplementedError
