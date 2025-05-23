import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import BaseModel

# Assuming your project structure allows this import
from mcp.core.workflow_engine import WorkflowEngine, WorkflowStepInput
from mcp.schemas.workflow import Workflow, WorkflowStep, ErrorHandlingConfig
from mcp.core.base import BaseMCPServer
from mcp.core.types import MCPType

# Minimal config for testing
class MockMCPConfig(BaseModel):
    setting: str

class MockMCPServer(BaseMCPServer):
    def __init__(self, config: MockMCPConfig):
        super().__init__(config)
        self.config = config

    async def execute(self, inputs: dict) -> dict:
        # Simple execution for testing
        if inputs.get("fail"):
            return {"success": False, "error": "Test MCP failed as requested", "result": None}
        return {"success": True, "result": {"output": f"Processed: {inputs.get('input_data', '')}"}, "error": None}

    @classmethod
    def get_config_schema(cls) -> type[BaseModel]:
        return MockMCPConfig

    @classmethod
    def get_description(cls) -> str:
        return "A mock MCP for testing."

    @classmethod
    def get_type(cls) -> MCPType:
        return MCPType.PYTHON_SCRIPT # Or any other, doesn't strictly matter for this mock

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def basic_workflow_definition() -> Workflow:
    return Workflow(
        workflow_id="wf-test-001",
        name="Test Workflow",
        description="A basic test workflow",
        steps=[
            WorkflowStep(
                step_id="step-1",
                mcp_id="mcp-mock-001",
                mcp_version_id="1.0.0",
                name="Mock Step 1",
                inputs={
                    "input_data": WorkflowStepInput(
                        source_type=InputSourceType.WORKFLOW_INPUT,
                        workflow_input_key="initial_param"
                    )
                }
            )
        ],
        error_handling=ErrorHandlingConfig(strategy="Stop on Error")
    )


@pytest.mark.asyncio
async def test_workflow_engine_instantiation(mock_db_session):
    engine = WorkflowEngine(db_session=mock_db_session)
    assert engine.db_session == mock_db_session

@pytest.mark.asyncio
@patch('mcp.core.registry.get_mcp_instance_from_db')
async def test_run_workflow_successful_sequential_execution(
    mock_get_mcp_instance,
    mock_db_session,
    basic_workflow_definition: Workflow
):
    engine = WorkflowEngine(db_session=mock_db_session)

    # Configure the mock MCP instance
    mock_mcp_instance = MockMCPServer(config=MockMCPConfig(setting="test"))
    mock_mcp_instance.execute = AsyncMock(
        return_value={"success": True, "result": {"output": "Step 1 output"}, "error": None}
    )
    mock_get_mcp_instance.return_value = mock_mcp_instance

    initial_inputs = {"initial_param": "Hello Workflow"}
    result = await engine.run_workflow(basic_workflow_definition, initial_inputs)

    assert result.status == "SUCCESS"
    assert result.workflow_id == basic_workflow_definition.workflow_id
    assert result.error_message is None
    assert len(result.step_results) == 1
    
    step_result = result.step_results[0]
    assert step_result["step_id"] == "step-1"
    assert step_result["status"] == "SUCCESS"
    assert step_result["outputs_generated"] == {"output": "Step 1 output"}
    assert result.final_outputs == {"output": "Step 1 output"}

    mock_get_mcp_instance.assert_called_once_with(
        db=mock_db_session,
        mcp_id_str="mcp-mock-001",
        mcp_version_str="1.0.0"
    )
    mock_mcp_instance.execute.assert_called_once_with({"input_data": "Hello Workflow"})


@pytest.mark.asyncio
@patch('mcp.core.registry.get_mcp_instance_from_db')
async def test_run_workflow_step_failure_stop_on_error(
    mock_get_mcp_instance,
    mock_db_session,
    basic_workflow_definition: Workflow
):
    engine = WorkflowEngine(db_session=mock_db_session)

    mock_mcp_instance = MockMCPServer(config=MockMCPConfig(setting="test"))
    mock_mcp_instance.execute = AsyncMock(
        return_value={"success": False, "error": "MCP simulated failure", "result": None}
    )
    mock_get_mcp_instance.return_value = mock_mcp_instance

    initial_inputs = {"initial_param": "Test input"}
    result = await engine.run_workflow(basic_workflow_definition, initial_inputs)

    assert result.status == "FAILED"
    assert result.error_message is not None
    assert "MCP simulated failure" in result.error_message
    assert len(result.step_results) == 1
    step_result = result.step_results[0]
    assert step_result["status"] == "FAILED"
    assert step_result["error"] == "MCP simulated failure"
    assert result.final_outputs is None

@pytest.mark.asyncio
@patch('mcp.core.registry.get_mcp_instance_from_db')
async def test_run_workflow_mcp_instantiation_failure(
    mock_get_mcp_instance,
    mock_db_session,
    basic_workflow_definition: Workflow
):
    engine = WorkflowEngine(db_session=mock_db_session)
    mock_get_mcp_instance.return_value = None # Simulate MCP not found or failed to instantiate

    initial_inputs = {"initial_param": "Test input"}
    result = await engine.run_workflow(basic_workflow_definition, initial_inputs)

    assert result.status == "FAILED"
    assert result.error_message is not None
    assert "MCP instance for ID 'mcp-mock-001' (Version: 1.0.0) not found or failed to instantiate." in result.error_message
    assert len(result.step_results) == 0 # No step result if instantiation fails before execution
    assert result.final_outputs is None


def test_resolve_step_inputs_static_value(mock_db_session):
    engine = WorkflowEngine(db_session=mock_db_session)
    step = WorkflowStep(
        step_id="s1", mcp_id="m1", name="Static Test",
        inputs={
            "static_param": WorkflowStepInput(source_type=InputSourceType.STATIC_VALUE, value=123)
        }
    )
    resolved = engine._resolve_step_inputs(step, {})
    assert resolved == {"static_param": 123}

def test_resolve_step_inputs_workflow_input(mock_db_session):
    engine = WorkflowEngine(db_session=mock_db_session)
    step = WorkflowStep(
        step_id="s1", mcp_id="m1", name="Workflow Input Test",
        inputs={
            "wf_param": WorkflowStepInput(source_type=InputSourceType.WORKFLOW_INPUT, workflow_input_key="global_input")
        }
    )
    workflow_context = {"workflow_initial_inputs": {"global_input": "hello"}}
    resolved = engine._resolve_step_inputs(step, workflow_context)
    assert resolved == {"wf_param": "hello"}

def test_resolve_step_inputs_step_output(mock_db_session):
    engine = WorkflowEngine(db_session=mock_db_session)
    step = WorkflowStep(
        step_id="s2", mcp_id="m2", name="Step Output Test",
        inputs={
            "prev_output": WorkflowStepInput(source_type=InputSourceType.STEP_OUTPUT, source_step_id="s1", source_output_name="data")
        }
    )
    workflow_context = {"s1": {"outputs": {"data": "output_from_s1"}}}
    resolved = engine._resolve_step_inputs(step, workflow_context)
    assert resolved == {"prev_output": "output_from_s1"}


@pytest.mark.asyncio
@patch('mcp.core.registry.get_mcp_instance_from_db')
async def test_run_workflow_two_steps_data_passing(
    mock_get_mcp_instance,
    mock_db_session,
):
    engine = WorkflowEngine(db_session=mock_db_session)

    # Configure mock MCP instances
    mock_mcp_instance_1 = MockMCPServer(config=MockMCPConfig(setting="test1"))
    mock_mcp_instance_1.execute = AsyncMock(
        return_value={"success": True, "result": {"inter_output": "Data from step 1"}, "error": None}
    )
    
    mock_mcp_instance_2 = MockMCPServer(config=MockMCPConfig(setting="test2"))
    mock_mcp_instance_2.execute = AsyncMock(
        return_value={"success": True, "result": {"final_output": "Processed by step 2"}, "error": None}
    )

    # Setup mock to return different instances based on mcp_id
    def side_effect_get_mcp(db, mcp_id_str, mcp_version_str):
        if mcp_id_str == "mcp-1":
            return mock_mcp_instance_1
        elif mcp_id_str == "mcp-2":
            return mock_mcp_instance_2
        return None
    mock_get_mcp_instance.side_effect = side_effect_get_mcp

    two_step_workflow = Workflow(
        workflow_id="wf-two-step-001",
        name="Two Step Workflow",
        steps=[
            WorkflowStep(
                step_id="step-a",
                mcp_id="mcp-1",
                mcp_version_id="1.0",
                name="First MCP",
                inputs={
                    "input_data": WorkflowStepInput(
                        source_type=InputSourceType.WORKFLOW_INPUT,
                        workflow_input_key="start_data"
                    )
                }
            ),
            WorkflowStep(
                step_id="step-b",
                mcp_id="mcp-2",
                mcp_version_id="1.0",
                name="Second MCP",
                inputs={
                    "input_from_step_a": WorkflowStepInput(
                        source_type=InputSourceType.STEP_OUTPUT,
                        source_step_id="step-a",
                        source_output_name="inter_output"
                    )
                }
            )
        ]
    )

    initial_inputs = {"start_data": "Initial Value"}
    result = await engine.run_workflow(two_step_workflow, initial_inputs)

    assert result.status == "SUCCESS"
    assert len(result.step_results) == 2
    
    assert result.step_results[0]["status"] == "SUCCESS"
    assert result.step_results[0]["outputs_generated"] == {"inter_output": "Data from step 1"}
    
    assert result.step_results[1]["status"] == "SUCCESS"
    assert result.step_results[1]["outputs_generated"] == {"final_output": "Processed by step 2"}
    assert result.step_results[1]["inputs_used"] == {"input_from_step_a": "Data from step 1"}
    
    assert result.final_outputs == {"final_output": "Processed by step 2"}

    mock_mcp_instance_1.execute.assert_called_once_with({"input_data": "Initial Value"})
    mock_mcp_instance_2.execute.assert_called_once_with({"input_from_step_a": "Data from step 1"})

# Need to import BaseModel for MockMCPConfig
