from dataclasses import dataclass
from collections.abc import Callable, Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.models import AgentRun, AgentRunStatus


@dataclass(frozen=True)
class WorkflowRequest:
    workflow_name: str
    inputs: dict[str, Any]


@dataclass(frozen=True)
class WorkflowResult:
    workflow_name: str
    status: str
    output: dict[str, Any]


WorkflowHandler = Callable[[WorkflowRequest], dict[str, Any]]


class Orchestrator:
    def __init__(
        self,
        workflows: Mapping[str, WorkflowHandler] | None = None,
    ) -> None:
        self._workflows: dict[str, WorkflowHandler] = dict(workflows or {})

    def register(self, workflow_name: str, handler: WorkflowHandler) -> None:
        if not workflow_name.strip():
            raise ValueError("Workflow name must not be empty")
        if workflow_name in self._workflows:
            raise ValueError(f"Workflow {workflow_name!r} is already registered")
        self._workflows[workflow_name] = handler

    def execute(
        self,
        request: WorkflowRequest,
        session: Session | None = None,
    ) -> WorkflowResult:
        handler = self._workflows.get(request.workflow_name)
        if handler is None:
            return WorkflowResult(
                workflow_name=request.workflow_name,
                status="NOT_IMPLEMENTED",
                output={},
            )

        run = self._start_run(session, request)
        try:
            output = handler(request)
            if not isinstance(output, dict):
                raise TypeError("Workflow handlers must return a dictionary")
        except Exception as error:
            self._finish_run(session, run, AgentRunStatus.FAILED, error_message=str(error))
            return WorkflowResult(
                workflow_name=request.workflow_name,
                status="FAILED",
                output={"error": str(error)},
            )

        self._finish_run(session, run, AgentRunStatus.SUCCEEDED, output=output)
        return WorkflowResult(
            workflow_name=request.workflow_name,
            status="SUCCEEDED",
            output=output,
        )

    @staticmethod
    def _start_run(session: Session | None, request: WorkflowRequest) -> AgentRun | None:
        if session is None:
            return None
        run = AgentRun(
            agent_name="orchestrator",
            workflow_name=request.workflow_name,
            status=AgentRunStatus.STARTED,
            input_data=request.inputs,
        )
        session.add(run)
        session.commit()
        return run

    @staticmethod
    def _finish_run(
        session: Session | None,
        run: AgentRun | None,
        status: AgentRunStatus,
        output: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        if session is None or run is None:
            return
        run.status = status
        run.output_data = output
        run.error_message = error_message
        session.commit()
