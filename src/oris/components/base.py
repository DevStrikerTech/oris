"""Base component contract for pipeline execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from oris.runtime.context import ExecutionContext


@dataclass(slots=True)
class Component(ABC):
    """Abstract base class for all Oris components (stateless per run)."""

    name: str
    config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validate_config(self.config)

    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate ``config`` before ``run``; raise ``ConfigurationError`` when invalid."""
        return

    @abstractmethod
    def run(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute this component and return a transformed payload."""
