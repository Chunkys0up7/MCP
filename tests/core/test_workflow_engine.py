import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from mcp.core.base import BaseMCPServer
from mcp.core.types import MCPType
# Assuming your project structure allows this import
from mcp.core.workflow_engine import WorkflowEngine, WorkflowStepInput
from mcp.db.models import \
    MCP as \
    MCPModel  # Renaming to avoid clash if MCP schema is also imported directly
from mcp.schemas.mcd_constraints import ArchitecturalConstraints
from mcp.schemas.workflow import (ErrorHandlingConfig, InputSourceType,
                                  Workflow, WorkflowStep)


# Minimal config for testing
class MockMCPConfig(BaseModel):
    setting: str
    name: str
    type: MCPType


class MockMCPServer(BaseMCPServer):
    def __init__(self, config: MockMCPConfig):
        super().__init__(config)
        self.config = config

    async def execute(self, inputs: dict) -> dict:
        # Simple execution for testing
        if inputs.get("fail"):
            return {
                "success": False,
                "error": "Test MCP failed as requested",
                "result": None,
            }
        return {
            "success": True,
            "result": {"output": f"Processed: {inputs.get('input_data', '')}"},
            "error": None,
        }

    @classmethod
    def get_config_schema(cls) -> type[BaseModel]:
        return MockMCPConfig

    @classmethod
    def get_description(cls) -> str:
        return "A mock MCP for testing."

    @classmethod
    def get_type(cls) -> MCPType:
        return (
            MCPType.PYTHON_SCRIPT
        )  # Or any other, doesn't strictly matter for this mock


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def allow_all_constraints() -> ArchitecturalConstraints:
    return ArchitecturalConstraints()


@pytest.fixture
def restrictive_constraints_max_steps() -> ArchitecturalConstraints:
    return ArchitecturalConstraints(max_workflow_steps=1)


@pytest.fixture
def restrictive_constraints_allowed_types() -> ArchitecturalConstraints:
    return ArchitecturalConstraints(allowed_mcp_types=[MCPType.PYTHON_SCRIPT])


@pytest.fixture
def restrictive_constraints_prohibited_types() -> ArchitecturalConstraints:
    return ArchitecturalConstraints(prohibited_mcp_types=[MCPType.LLM_PROMPT])


@pytest.fixture
def restrictive_constraints_required_tags() -> ArchitecturalConstraints:
    return ArchitecturalConstraints(required_tags_all_steps=["prod"])


@pytest.fixture
def restrictive_constraints_prohibited_tags() -> ArchitecturalConstraints:
    return ArchitecturalConstraints(prohibited_tags_any_step=["experimental"])


def create_mock_mcp_model(
    mcp_id: str, mcp_type: MCPType, tags: list[str] | None = None
) -> MCPModel:
    mock_model = MagicMock(spec=MCPModel)
    try:
        mock_model.id = uuid.UUID(mcp_id)
    except ValueError:
        print(
            f"Warning: Invalid mcp_id '{mcp_id}' passed to create_mock_mcp_model. Generating a new UUID."
        )
        mock_model.id = uuid.uuid4()

    mock_model.type = mcp_type.value  # MCPModel stores type as string value
    mock_model.tags = tags if tags else []
    return mock_model


@pytest.fixture
def mock_mcp_id_1() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def mock_mcp_id_2() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def basic_workflow_definition(mock_mcp_id_1: str) -> Workflow:
    return Workflow(
        workflow_id="wf-test-001",
        name="Test Workflow",
        description="A basic test workflow",
        steps=[
            WorkflowStep(
                step_id="step-1",
                mcp_id=mock_mcp_id_1,
                mcp_version_id="1.0.0",
                name="Mock Step 1",
                inputs={
                    "input_data": WorkflowStepInput(
                        source_type=InputSourceType.WORKFLOW_INPUT,
                        workflow_input_key="initial_param",
                    )
                },
            )
        ],
        error_handling=ErrorHandlingConfig(strategy="Stop on Error"),
    )


@pytest.mark.asyncio
async def test_workflow_engine_instantiation(mock_db_session, allow_all_constraints):
    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=allow_all_constraints
    )
    assert engine.db_session == mock_db_session
    assert engine.constraints == allow_all_constraints


@pytest.mark.asyncio
@patch("mcp.core.registry.get_mcp_instance_from_db")
async def test_run_workflow_successful_sequential_execution(
    mock_get_mcp_instance,
    mock_db_session,
    basic_workflow_definition: Workflow,
    allow_all_constraints,
):
    with patch("mcp.core.registry.load_mcp_definition_from_db") as mock_load_mcp_def:
        mock_mcp_model_for_validation = create_mock_mcp_model(
            mcp_id=basic_workflow_definition.steps[0].mcp_id,
            mcp_type=MCPType.PYTHON_SCRIPT,
        )
        mock_load_mcp_def.return_value = mock_mcp_model_for_validation

        engine = WorkflowEngine(
            db_session=mock_db_session, constraints=allow_all_constraints
        )

        mock_mcp_instance = MockMCPServer(
            config=MockMCPConfig(
                setting="test", name="TestMCP1", type=MCPType.PYTHON_SCRIPT
            )
        )
        mock_mcp_instance.execute = AsyncMock(
            return_value={
                "success": True,
                "result": {"output": "Step 1 output"},
                "error": None,
            }
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
            mcp_id_str=basic_workflow_definition.steps[0].mcp_id,
            mcp_version_str="1.0.0",
        )
        mock_mcp_instance.execute.assert_called_once_with(
            {"input_data": "Hello Workflow"}
        )


@pytest.mark.asyncio
@patch("mcp.core.registry.get_mcp_instance_from_db")
async def test_run_workflow_step_failure_stop_on_error(
    mock_get_mcp_instance,
    mock_db_session,
    basic_workflow_definition: Workflow,
    allow_all_constraints,
):
    with patch("mcp.core.registry.load_mcp_definition_from_db") as mock_load_mcp_def:
        mock_mcp_model_for_validation = create_mock_mcp_model(
            mcp_id=basic_workflow_definition.steps[0].mcp_id,
            mcp_type=MCPType.PYTHON_SCRIPT,
        )
        mock_load_mcp_def.return_value = mock_mcp_model_for_validation

        engine = WorkflowEngine(
            db_session=mock_db_session, constraints=allow_all_constraints
        )

        mock_mcp_instance = MockMCPServer(
            config=MockMCPConfig(
                setting="test", name="TestMCPFail", type=MCPType.PYTHON_SCRIPT
            )
        )
        mock_mcp_instance.execute = AsyncMock(
            return_value={
                "success": False,
                "error": "MCP simulated failure",
                "result": None,
            }
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
@patch("mcp.core.registry.get_mcp_instance_from_db")
async def test_run_workflow_mcp_instantiation_failure(
    mock_get_mcp_instance,
    mock_db_session,
    basic_workflow_definition: Workflow,
    allow_all_constraints,
):
    with patch("mcp.core.registry.load_mcp_definition_from_db") as mock_load_mcp_def:
        mock_mcp_model_for_validation = create_mock_mcp_model(
            mcp_id=basic_workflow_definition.steps[0].mcp_id,
            mcp_type=MCPType.PYTHON_SCRIPT,
        )
        mock_load_mcp_def.return_value = mock_mcp_model_for_validation

        engine = WorkflowEngine(
            db_session=mock_db_session, constraints=allow_all_constraints
        )
        mock_get_mcp_instance.return_value = (
            None  # Simulate MCP not found or failed to instantiate
        )

        initial_inputs = {"initial_param": "Test input"}
        result = await engine.run_workflow(basic_workflow_definition, initial_inputs)

        assert result.status == "FAILED"
        assert result.error_message is not None
        assert (
            "MCP instance for ID '{}' (Version: 1.0.0) not found or failed to instantiate.".format(
                basic_workflow_definition.steps[0].mcp_id
            )
            in result.error_message
        )
        assert len(result.step_results) == 1
        assert result.step_results[0]["status"] == "FAILED"
        assert (
            basic_workflow_definition.steps[0].mcp_id in result.step_results[0]["error"]
        )
        assert result.final_outputs is None


def test_resolve_step_inputs_static_value(mock_db_session, allow_all_constraints):
    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=allow_all_constraints
    )
    step = WorkflowStep(
        step_id="s1",
        mcp_id="m1",
        name="Static Test",
        inputs={
            "static_param": WorkflowStepInput(
                source_type=InputSourceType.STATIC_VALUE, value=123
            )
        },
    )
    resolved = engine._resolve_step_inputs(step, {})
    assert resolved == {"static_param": 123}


def test_resolve_step_inputs_workflow_input(mock_db_session, allow_all_constraints):
    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=allow_all_constraints
    )
    step = WorkflowStep(
        step_id="s1",
        mcp_id="m1",
        name="Workflow Input Test",
        inputs={
            "wf_param": WorkflowStepInput(
                source_type=InputSourceType.WORKFLOW_INPUT,
                workflow_input_key="global_input",
            )
        },
    )
    workflow_context = {"workflow_initial_inputs": {"global_input": "hello"}}
    resolved = engine._resolve_step_inputs(step, workflow_context)
    assert resolved == {"wf_param": "hello"}


def test_resolve_step_inputs_step_output(mock_db_session, allow_all_constraints):
    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=allow_all_constraints
    )
    step = WorkflowStep(
        step_id="s2",
        mcp_id="m2",
        name="Step Output Test",
        inputs={
            "prev_output": WorkflowStepInput(
                source_type=InputSourceType.STEP_OUTPUT,
                source_step_id="s1",
                source_output_name="data",
            )
        },
    )
    workflow_context = {"s1": {"outputs": {"data": "output_from_s1"}}}
    resolved = engine._resolve_step_inputs(step, workflow_context)
    assert resolved == {"prev_output": "output_from_s1"}


@pytest.mark.asyncio
@patch("mcp.core.registry.get_mcp_instance_from_db")
async def test_run_workflow_two_steps_data_passing(
    mock_get_mcp_instance,
    mock_db_session,
    allow_all_constraints,
    mock_mcp_id_1: str,
    mock_mcp_id_2: str,
):
    with patch("mcp.core.registry.load_mcp_definition_from_db") as mock_load_mcp_def:

        engine = WorkflowEngine(
            db_session=mock_db_session, constraints=allow_all_constraints
        )

        mock_mcp_instance_1 = MockMCPServer(
            config=MockMCPConfig(
                setting="test1", name="MCP1", type=MCPType.PYTHON_SCRIPT
            )
        )
        mock_mcp_instance_1.execute = AsyncMock(
            return_value={
                "success": True,
                "result": {"inter_output": "Data from step 1"},
                "error": None,
            }
        )

        mock_mcp_instance_2 = MockMCPServer(
            config=MockMCPConfig(
                setting="test2", name="MCP2", type=MCPType.PYTHON_SCRIPT
            )
        )
        mock_mcp_instance_2.execute = AsyncMock(
            return_value={
                "success": True,
                "result": {"final_output": "Processed by step 2"},
                "error": None,
            }
        )

        def side_effect_get_mcp(db, mcp_id_str, mcp_version_str):
            if mcp_id_str == mock_mcp_id_1:
                return mock_mcp_instance_1
            elif mcp_id_str == mock_mcp_id_2:
                return mock_mcp_instance_2
            return None

        mock_get_mcp_instance.side_effect = side_effect_get_mcp

        def side_effect_load_def(db, mcp_id_str):
            if mcp_id_str == mock_mcp_id_1:
                return create_mock_mcp_model(
                    mcp_id=mock_mcp_id_1, mcp_type=MCPType.PYTHON_SCRIPT
                )
            elif mcp_id_str == mock_mcp_id_2:
                return create_mock_mcp_model(
                    mcp_id=mock_mcp_id_2, mcp_type=MCPType.PYTHON_SCRIPT
                )
            return None

        mock_load_mcp_def.side_effect = side_effect_load_def

        two_step_workflow = Workflow(
            workflow_id="wf-two-step-001",
            name="Two Step Workflow",
            steps=[
                WorkflowStep(
                    step_id="step-a",
                    mcp_id=mock_mcp_id_1,
                    mcp_version_id="1.0",
                    name="First MCP",
                    inputs={
                        "input_data": WorkflowStepInput(
                            source_type=InputSourceType.WORKFLOW_INPUT,
                            workflow_input_key="start_data",
                        )
                    },
                ),
                WorkflowStep(
                    step_id="step-b",
                    mcp_id=mock_mcp_id_2,
                    mcp_version_id="1.0",
                    name="Second MCP",
                    inputs={
                        "input_from_step_a": WorkflowStepInput(
                            source_type=InputSourceType.STEP_OUTPUT,
                            source_step_id="step-a",
                            source_output_name="inter_output",
                        )
                    },
                ),
            ],
        )

        initial_inputs = {"start_data": "Initial Value"}
        result = await engine.run_workflow(two_step_workflow, initial_inputs)

        assert result.status == "SUCCESS"
        assert len(result.step_results) == 2

        assert result.step_results[0]["status"] == "SUCCESS"
        assert result.step_results[0]["outputs_generated"] == {
            "inter_output": "Data from step 1"
        }

        assert result.step_results[1]["status"] == "SUCCESS"
        assert result.step_results[1]["outputs_generated"] == {
            "final_output": "Processed by step 2"
        }
        assert result.step_results[1]["inputs_used"] == {
            "input_from_step_a": "Data from step 1"
        }

        assert result.final_outputs == {"final_output": "Processed by step 2"}

        mock_mcp_instance_1.execute.assert_called_once_with(
            {"input_data": "Initial Value"}
        )
        mock_mcp_instance_2.execute.assert_called_once_with(
            {"input_from_step_a": "Data from step 1"}
        )

        assert mock_get_mcp_instance.call_count == 2
        mock_get_mcp_instance.assert_any_call(
            db=mock_db_session, mcp_id_str=mock_mcp_id_1, mcp_version_str="1.0"
        )
        mock_get_mcp_instance.assert_any_call(
            db=mock_db_session, mcp_id_str=mock_mcp_id_2, mcp_version_str="1.0"
        )

        assert mock_load_mcp_def.call_count == 2
        mock_load_mcp_def.assert_any_call(db=mock_db_session, mcp_id_str=mock_mcp_id_1)
        mock_load_mcp_def.assert_any_call(db=mock_db_session, mcp_id_str=mock_mcp_id_2)


# Need to import BaseModel for MockMCPConfig

# --- Tests for _validate_workflow_against_constraints ---


@patch("mcp.core.registry.load_mcp_definition_from_db")
def test_validate_constraints_max_steps_violation(
    mock_load_mcp_def,
    mock_db_session,
    basic_workflow_definition,  # Has 1 step
    restrictive_constraints_max_steps,  # Allows 1 step
    mock_mcp_id_2: str,  # ADDED: To provide a valid ID for the second step
):
    # Make workflow have 2 steps to violate constraint of 1 step
    two_step_workflow = basic_workflow_definition.model_copy(deep=True)
    two_step_workflow.steps.append(
        WorkflowStep(
            step_id="step-2",
            mcp_id=mock_mcp_id_2,
            name="Mock Step 2",
            inputs={},  # MODIFIED: use mock_mcp_id_2
            mcp_version_id="1.0.0",
        )
    )

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=restrictive_constraints_max_steps
    )

    with pytest.raises(ValueError) as excinfo:
        engine._validate_workflow_against_constraints(two_step_workflow)
    assert "exceeds maximum allowed (1)" in str(excinfo.value)
    assert "Number of steps (2)" in str(excinfo.value)
    mock_load_mcp_def.assert_not_called()  # Should fail before checking step details


@patch("mcp.core.registry.load_mcp_definition_from_db")
def test_validate_constraints_allowed_type_violation(
    mock_load_mcp_def,
    mock_db_session,
    basic_workflow_definition,  # Uses mcp-mock-001
    restrictive_constraints_allowed_types,  # Allows only PYTHON_SCRIPT
):
    # Simulate mcp-mock-001 is of type LLM_PROMPT, which is not allowed
    mock_mcp_model = create_mock_mcp_model(
        mcp_id=basic_workflow_definition.steps[0].mcp_id, mcp_type=MCPType.LLM_PROMPT
    )
    mock_load_mcp_def.return_value = mock_mcp_model

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=restrictive_constraints_allowed_types
    )

    with pytest.raises(ValueError) as excinfo:
        engine._validate_workflow_against_constraints(basic_workflow_definition)
    assert "not in the list of allowed types" in str(excinfo.value)
    assert f"type '{MCPType.LLM_PROMPT.value}'" in str(excinfo.value)
    expected_allowed_str = str(
        [m.value for m in restrictive_constraints_allowed_types.allowed_mcp_types]
    )
    assert expected_allowed_str in str(excinfo.value)
    mock_load_mcp_def.assert_called_once_with(
        db=mock_db_session, mcp_id_str=basic_workflow_definition.steps[0].mcp_id
    )


@patch("mcp.core.registry.load_mcp_definition_from_db")
def test_validate_constraints_prohibited_type_violation(
    mock_load_mcp_def,
    mock_db_session,
    basic_workflow_definition,  # Uses mcp-mock-001
    restrictive_constraints_prohibited_types,  # Prohibits LLM_PROMPT
):
    # Simulate mcp-mock-001 is of type LLM_PROMPT, which is prohibited
    mock_mcp_model = create_mock_mcp_model(
        mcp_id=basic_workflow_definition.steps[0].mcp_id, mcp_type=MCPType.LLM_PROMPT
    )
    mock_load_mcp_def.return_value = mock_mcp_model

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=restrictive_constraints_prohibited_types
    )

    with pytest.raises(ValueError) as excinfo:
        engine._validate_workflow_against_constraints(basic_workflow_definition)
    assert "is in the list of prohibited types" in str(excinfo.value)
    assert f"type '{MCPType.LLM_PROMPT.value}'" in str(excinfo.value)
    expected_prohibited_str = str(
        [m.value for m in restrictive_constraints_prohibited_types.prohibited_mcp_types]
    )
    assert expected_prohibited_str in str(excinfo.value)
    mock_load_mcp_def.assert_called_once_with(
        db=mock_db_session, mcp_id_str=basic_workflow_definition.steps[0].mcp_id
    )


@patch("mcp.core.registry.load_mcp_definition_from_db")
def test_validate_constraints_required_tag_missing(
    mock_load_mcp_def,
    mock_db_session,
    basic_workflow_definition,  # Uses mcp-mock-001
    restrictive_constraints_required_tags,  # Requires "prod" tag
):
    # Simulate mcp-mock-001 has type PYTHON_SCRIPT and tag "dev", but not "prod"
    mock_mcp_model = create_mock_mcp_model(
        mcp_id=basic_workflow_definition.steps[0].mcp_id,
        mcp_type=MCPType.PYTHON_SCRIPT,
        tags=["dev"],
    )
    mock_load_mcp_def.return_value = mock_mcp_model

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=restrictive_constraints_required_tags
    )

    with pytest.raises(ValueError) as excinfo:
        engine._validate_workflow_against_constraints(basic_workflow_definition)
    assert "is missing required tag 'prod'" in str(excinfo.value)
    mock_load_mcp_def.assert_called_once_with(
        db=mock_db_session, mcp_id_str=basic_workflow_definition.steps[0].mcp_id
    )


@patch("mcp.core.registry.load_mcp_definition_from_db")
def test_validate_constraints_prohibited_tag_present(
    mock_load_mcp_def,
    mock_db_session,
    basic_workflow_definition,  # Uses mcp-mock-001
    restrictive_constraints_prohibited_tags,  # Prohibits "experimental"
):
    # Simulate mcp-mock-001 has type PYTHON_SCRIPT and tag "experimental"
    mock_mcp_model = create_mock_mcp_model(
        mcp_id=basic_workflow_definition.steps[0].mcp_id,
        mcp_type=MCPType.PYTHON_SCRIPT,
        tags=["experimental", "dev"],
    )
    mock_load_mcp_def.return_value = mock_mcp_model

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=restrictive_constraints_prohibited_tags
    )

    with pytest.raises(ValueError) as excinfo:
        engine._validate_workflow_against_constraints(basic_workflow_definition)
    assert "has prohibited tag 'experimental'" in str(excinfo.value)
    mock_load_mcp_def.assert_called_once_with(
        db=mock_db_session, mcp_id_str=basic_workflow_definition.steps[0].mcp_id
    )


@patch("mcp.core.registry.load_mcp_definition_from_db")
def test_validate_constraints_mcp_def_not_found(
    mock_load_mcp_def,
    mock_db_session,
    basic_workflow_definition,  # Uses mcp-mock-001
    allow_all_constraints,
):
    mock_load_mcp_def.return_value = None  # Simulate MCP definition not found

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=allow_all_constraints
    )

    with pytest.raises(ValueError) as excinfo:
        engine._validate_workflow_against_constraints(basic_workflow_definition)
    assert "MCP definition for ID '{}' in step 'Mock Step 1' not found.".format(
        basic_workflow_definition.steps[0].mcp_id
    ) in str(excinfo.value)
    assert "not found" in str(excinfo.value)
    mock_load_mcp_def.assert_called_once_with(
        db=mock_db_session, mcp_id_str=basic_workflow_definition.steps[0].mcp_id
    )


@patch("mcp.core.registry.load_mcp_definition_from_db")
def test_validate_constraints_successful_with_constraints(
    mock_load_mcp_def,
    mock_db_session,
    basic_workflow_definition,  # Uses mcp-mock-001, one step
    restrictive_constraints_allowed_types,  # Allows PYTHON_SCRIPT
):
    # Simulate mcp-mock-001 is type PYTHON_SCRIPT, tags=[]
    mock_mcp_model = create_mock_mcp_model(
        mcp_id=basic_workflow_definition.steps[0].mcp_id,
        mcp_type=MCPType.PYTHON_SCRIPT,
        tags=[],
    )
    mock_load_mcp_def.return_value = mock_mcp_model

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=restrictive_constraints_allowed_types
    )

    try:
        engine._validate_workflow_against_constraints(basic_workflow_definition)
    except ValueError:
        pytest.fail(
            "_validate_workflow_against_constraints raised ValueError unexpectedly"
        )

    mock_load_mcp_def.assert_called_once_with(
        db=mock_db_session, mcp_id_str=basic_workflow_definition.steps[0].mcp_id
    )


# --- Tests for run_workflow with Constraint Violations ---


@pytest.mark.asyncio
@patch("mcp.core.registry.load_mcp_definition_from_db")
@patch(
    "mcp.core.registry.get_mcp_instance_from_db"
)  # Also mock this, though it shouldn't be called if validation fails
async def test_run_workflow_fails_on_constraint_violation(
    mock_get_mcp_instance,  # For execution phase (should not be reached)
    mock_load_mcp_def,  # For validation phase
    mock_db_session,
    basic_workflow_definition,  # Uses mcp-mock-001
    restrictive_constraints_prohibited_types,  # Prohibits LLM_PROMPT
):
    # Simulate mcp-mock-001 is of type LLM_PROMPT, which is prohibited
    mock_mcp_model_for_validation = create_mock_mcp_model(
        mcp_id=basic_workflow_definition.steps[0].mcp_id, mcp_type=MCPType.LLM_PROMPT
    )
    mock_load_mcp_def.return_value = mock_mcp_model_for_validation

    engine = WorkflowEngine(
        db_session=mock_db_session, constraints=restrictive_constraints_prohibited_types
    )

    initial_inputs = {"initial_param": "Test input"}
    result = await engine.run_workflow(basic_workflow_definition, initial_inputs)

    assert result.status == "FAILED"
    assert result.error_message is not None
    assert (
        "is in the list of prohibited types" in result.error_message
    )  # Error from validation
    assert len(result.step_results) == 0  # No steps executed

    mock_load_mcp_def.assert_called_once_with(
        db=mock_db_session, mcp_id_str=basic_workflow_definition.steps[0].mcp_id
    )
    mock_get_mcp_instance.assert_not_called()  # Should not attempt to get instance if validation fails
