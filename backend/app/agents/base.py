from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentContext:
    workflow_id: str
    inputs: dict[str, Any]


@dataclass(frozen=True)
class AgentResult:
    agent_name: str
    output: dict[str, Any]


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError
