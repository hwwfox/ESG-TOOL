"""Base classes and utilities for ESG workflow agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class AgentContext(Dict[str, Any]):
    """Mutable context dictionary shared across agents in a workflow."""


class Agent(ABC):
    """Abstract base class for all agents participating in the workflow."""

    name: str = "agent"
    description: str = ""

    def __init__(self) -> None:
        self._last_output: Dict[str, Any] | None = None

    @abstractmethod
    def run(self, context: AgentContext) -> Dict[str, Any]:
        """Execute the agent logic and return updates for the shared context."""

    def __call__(self, context: AgentContext) -> Dict[str, Any]:
        output = self.run(context)
        self._last_output = output
        context.update(output)
        return output

    @property
    def last_output(self) -> Dict[str, Any] | None:
        return self._last_output
