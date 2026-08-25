from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowRequest:
    workflow_name: str
    inputs: dict[str, Any]


@dataclass(frozen=True)
class WorkflowResult:
    workflow_name: str
    status: str
    output: dict[str, Any]


class Orchestrator:
    def execute(self, request: WorkflowRequest) -> WorkflowResult:
        return WorkflowResult(
            workflow_name=request.workflow_name,
            status="NOT_IMPLEMENTED",
            output={},
        )
