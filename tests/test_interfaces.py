from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.agents.base import AgentContext
from app.db.base import Base
from app.models import AgentRun, AgentRunStatus
from app.orchestrator.base import Orchestrator, WorkflowRequest
from app.tools.base import ScopedToolRegistry, Tool, ToolRegistry
import app.models.entities  # noqa: F401


def test_orchestrator_is_deterministic_stub() -> None:
    result = Orchestrator().execute(
        WorkflowRequest(workflow_name="phase_0_check", inputs={})
    )

    assert result.status == "NOT_IMPLEMENTED"
    assert result.workflow_name == "phase_0_check"


def test_orchestrator_executes_registered_workflow_and_records_run() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    orchestrator = Orchestrator(
        {"prepare": lambda request: {"candidate_id": request.inputs["candidate_id"]}}
    )

    with Session(engine) as session:
        result = orchestrator.execute(
            WorkflowRequest(workflow_name="prepare", inputs={"candidate_id": 7}),
            session,
        )

        run = session.scalar(select(AgentRun))
        assert result.status == "SUCCEEDED"
        assert result.output == {"candidate_id": 7}
        assert run is not None
        assert run.status == AgentRunStatus.SUCCEEDED
        assert run.input_data == {"candidate_id": 7}
        assert run.output_data == {"candidate_id": 7}


def test_orchestrator_returns_failed_result_and_records_error() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    orchestrator = Orchestrator({"broken": lambda _: 1})

    with Session(engine) as session:
        result = orchestrator.execute(WorkflowRequest("broken", {}), session)

        run = session.scalar(select(AgentRun))
        assert result.status == "FAILED"
        assert result.output == {"error": "Workflow handlers must return a dictionary"}
        assert run is not None
        assert run.status == AgentRunStatus.FAILED
        assert run.error_message == "Workflow handlers must return a dictionary"


def test_orchestrator_rejects_empty_and_duplicate_workflows() -> None:
    orchestrator = Orchestrator()
    handler = lambda _: {}

    try:
        orchestrator.register("", handler)
    except ValueError as error:
        assert str(error) == "Workflow name must not be empty"
    else:
        raise AssertionError("Expected empty workflow names to be rejected")

    orchestrator.register("prepare", handler)
    try:
        orchestrator.register("prepare", handler)
    except ValueError as error:
        assert str(error) == "Workflow 'prepare' is already registered"
    else:
        raise AssertionError("Expected duplicate workflow names to be rejected")


def test_agent_context_is_typed_data() -> None:
    context = AgentContext(workflow_id="workflow-1", inputs={"value": 1})

    assert context.workflow_id == "workflow-1"
    assert context.inputs["value"] == 1


class EchoTool(Tool):
    name = "echo"

    def execute(self, arguments: dict[str, object]) -> dict[str, object]:
        return arguments


class PrivateTool(Tool):
    name = "private"

    def execute(self, arguments: dict[str, object]) -> dict[str, object]:
        return arguments


def test_tool_registry_scopes_agent_access() -> None:
    registry = ToolRegistry([EchoTool(), PrivateTool()])
    scoped = registry.scope(["echo"])

    assert isinstance(scoped, ScopedToolRegistry)
    assert registry.names() == ("echo", "private")
    assert scoped.names() == ("echo",)
    assert scoped.execute("echo", {"value": 1}) == {"value": 1}

    try:
        scoped.execute("private", {})
    except PermissionError as error:
        assert str(error) == "Tool 'private' is not available in this scope"
    else:
        raise AssertionError("Expected scoped access to reject unavailable tools")
