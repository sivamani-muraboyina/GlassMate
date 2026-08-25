from app.agents.base import AgentContext
from app.orchestrator.base import Orchestrator, WorkflowRequest


def test_orchestrator_is_deterministic_stub() -> None:
    result = Orchestrator().execute(
        WorkflowRequest(workflow_name="phase_0_check", inputs={})
    )

    assert result.status == "NOT_IMPLEMENTED"
    assert result.workflow_name == "phase_0_check"


def test_agent_context_is_typed_data() -> None:
    context = AgentContext(workflow_id="workflow-1", inputs={"value": 1})

    assert context.workflow_id == "workflow-1"
    assert context.inputs["value"] == 1
