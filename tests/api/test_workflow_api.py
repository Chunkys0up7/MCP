import pytest
from fastapi.testclient import TestClient
import os
import uuid
from typing import Dict, Any, List
from datetime import datetime

# Import the test_app_client and test_db_session from conftest
from ..conftest import test_app_client, test_db_session # Relative import for conftest

# Set a consistent API key for testing environment (used to get JWT)
TEST_API_KEY = str(uuid.uuid4())
os.environ["MCP_API_KEY"] = TEST_API_KEY

from mcp.api.main import app # app from your FastAPI application
# from mcp.core.registry import mcp_server_registry, MCP_REGISTRY_FILE, WORKFLOW_STORAGE_FILE # Old file-based
from mcp.db.models import MCP as MCPModel, MCPVersion as MCPVersionModel, WorkflowDefinition as WorkflowDefinitionModel # DB Models
from mcp.db.session import Session # For type hinting db session
from mcp.schemas.workflow import Workflow as WorkflowSchema, WorkflowCreate as WorkflowCreateSchema, WorkflowExecutionResult, WorkflowStep, InputSourceType, ErrorHandlingConfig
from mcp.schemas.mcp import MCPCreate as MCPCreateSchema # For creating MCPs
from mcp.core.types import MCPType

# Use the test_app_client from conftest.py, which handles DB override
@pytest.fixture(scope="module")
def client(test_app_client: TestClient): # Renamed client parameter to avoid clash, inject test_app_client
    # The old client fixture managed file cleanup. That's not needed for DB backed tests in the same way.
    # test_app_client fixture from conftest already provides the TestClient instance with overridden DB.
    yield test_app_client 

@pytest.fixture(autouse=True)
def clear_db_records(test_db_session: Session): # Uses the SQLite session from conftest
    # This fixture will run for every test. test_db_session already handles table creation/dropping.
    # We might want to ensure no data leaks if tests don't clean up perfectly, 
    # but create_all/drop_all per function in test_db_session should handle isolation.
    pass

@pytest.fixture(scope="module")
def api_key_headers() -> Dict[str, str]:
    """Headers for endpoints still protected by X-API-Key (e.g., /auth/issue-dev-token)."""
    return {"X-API-Key": TEST_API_KEY}

@pytest.fixture(scope="module")
def jwt_headers(client: TestClient, api_key_headers: Dict[str, str]) -> Dict[str, str]:
    """Gets a JWT and returns headers for JWT-protected endpoints."""
    response = client.post("/auth/issue-dev-token", headers=api_key_headers)
    assert response.status_code == 200, f"Failed to get JWT: {response.text}"
    token_data = response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

# MODIFIED: dummy_mcp_id to create MCP in the test DB
@pytest.fixture
def dummy_mcp_def(test_db_session: Session) -> MCPModel:
    mcp_create = MCPCreateSchema(
        name="Test Python Script for Workflow",
        type=MCPType.PYTHON_SCRIPT,
        description="A test python script MCP.",
        tags=["test", "python"],
        initial_version_str="1.0.0",
        initial_version_description="Initial version",
        initial_config={"script_content": "print('Hello from DB-backed workflow test MCP')"}
    )
    
    # Use a direct service call if available, or construct and save manually
    # Assuming a service function like mcp_registry_service.save_mcp_definition_to_db exists and works with Session
    from mcp.core import registry as mcp_registry_service # Ensure this import is correct
    db_mcp = mcp_registry_service.save_mcp_definition_to_db(db=test_db_session, mcp_data=mcp_create)
    return db_mcp

@pytest.fixture
def dummy_mcp_id(dummy_mcp_def: MCPModel) -> str:
    return str(dummy_mcp_def.id)

# MODIFIED: created_workflow_id to create WorkflowDefinition in the test DB
@pytest.fixture
def created_workflow_definition(test_db_session: Session, dummy_mcp_id: str) -> WorkflowDefinitionModel:
    workflow_payload = WorkflowCreateSchema(
        name="Test DB Workflow",
        description="A test workflow for API testing, DB backed.",
        steps=[
            WorkflowStep(
                name="Step 1 DB",
                mcp_id=dummy_mcp_id,
                mcp_version_id="1.0.0", # Assuming the dummy MCP created version "1.0.0"
                inputs={
                    "param1": WorkflowStepInput(source_type=InputSourceType.STATIC_VALUE, value="value1_from_db_wf")
                }
                # Removed "outputs_to_map" as it's not in the current WorkflowStep schema
            )
        ],
        error_handling=ErrorHandlingConfig(strategy="Stop on Error")
        # Add execution_mode if it's mandatory or for specific tests
    )
    
    db_workflow = WorkflowDefinitionModel(
        name=workflow_payload.name,
        description=workflow_payload.description,
        steps=[step.model_dump() for step in workflow_payload.steps],
        execution_mode=workflow_payload.execution_mode,
        error_handling=workflow_payload.error_handling.model_dump()
    )
    test_db_session.add(db_workflow)
    test_db_session.commit()
    test_db_session.refresh(db_workflow)
    return db_workflow

@pytest.fixture
def created_workflow_id(created_workflow_definition: WorkflowDefinitionModel) -> str:
    return str(created_workflow_definition.workflow_id)

# === POST /workflows/ ===
# Test needs to be adapted to use the client with overridden DB
# and verify DB state if necessary.
def test_create_workflow_success(client: TestClient, dummy_mcp_id: str, jwt_headers: Dict[str, str], test_db_session: Session):
    workflow_data = {
        "name": "My New DB Workflow",
        "description": "A detailed description for DB.",
        "steps": [
            {
                "name": "Initial DB Step",
                "mcp_id": dummy_mcp_id,
                "mcp_version_id": "1.0.0", # Ensure this version exists for dummy_mcp_id
                "inputs": {"data": {"source_type": "static_value", "value": "input_data_db"}} # Corrected input format
            }
        ]
        # Add other fields like execution_mode, error_handling if needed by WorkflowCreateSchema
    }
    response = client.post("/workflows/", json=workflow_data, headers=jwt_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My New DB Workflow"
    
    # Verify in DB
    wf_from_db = test_db_session.query(WorkflowDefinitionModel).filter(WorkflowDefinitionModel.workflow_id == uuid.UUID(data["workflow_id"])).first()
    assert wf_from_db is not None
    assert wf_from_db.name == "My New DB Workflow"

def test_create_workflow_mcp_not_found_in_db(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_mcp_id = str(uuid.uuid4())
    workflow_data = {
        "name": "Workflow with Bad MCP DB",
        "steps": [{"name": "Bad Step DB", "mcp_id": non_existent_mcp_id, "mcp_version_id": "1.0.0", "inputs": {}}]
    }
    response = client.post("/workflows/", json=workflow_data, headers=jwt_headers)
    # The API should check MCP existence in DB. 
    # The current error code in the old test is 400, but it might be 404 if explicitly checked and not found.
    # Let's assume the router's create_workflow_definition does this check.
    assert response.status_code == 404 # Expecting 404 if MCP definition not found
    assert "mcp with id" in response.json()["detail"].lower()
    assert non_existent_mcp_id in response.json()["detail"]

# ... (Keep other auth tests like test_create_workflow_no_jwt, test_create_workflow_invalid_jwt as they are JWT focused)

# === GET /workflows/ === (Should now read from test DB)
def test_list_workflows_empty(client: TestClient, jwt_headers: Dict[str, str], test_db_session: Session):
    # Ensure DB is clean for this specific test (test_db_session fixture handles table drop/create)
    response = client.get("/workflows/", headers=jwt_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_list_workflows_with_data(client: TestClient, created_workflow_definition: WorkflowDefinitionModel, jwt_headers: Dict[str, str]):
    response = client.get("/workflows/", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(wf["workflow_id"] == str(created_workflow_definition.workflow_id) for wf in data)

# ... (Keep auth tests for list)

# === GET /workflows/{workflow_id} === (Should now read from test DB)
def test_get_workflow_success(client: TestClient, created_workflow_definition: WorkflowDefinitionModel, jwt_headers: Dict[str, str]):
    response = client.get(f"/workflows/{created_workflow_definition.workflow_id}", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == str(created_workflow_definition.workflow_id)
    assert data["name"] == created_workflow_definition.name # "Test DB Workflow"

# ... (Keep other GET tests like not_found, auth tests)

# === PUT /workflows/{workflow_id} === (Should now update in test DB)
def test_update_workflow_success(client: TestClient, created_workflow_definition: WorkflowDefinitionModel, dummy_mcp_id: str, jwt_headers: Dict[str, str], test_db_session: Session):
    workflow_id = str(created_workflow_definition.workflow_id)
    updated_data = {
        "name": "Updated DB Workflow Name",
        "description": "Updated DB description.",
        "steps": [
            {
                "name": "Updated DB Step 1",
                "mcp_id": dummy_mcp_id, 
                "mcp_version_id": "1.0.0",
                "inputs": {"param1": {"source_type": "static_value", "value":"new_db_value"}} # Corrected input
            }
        ]
    }
    response = client.put(f"/workflows/{workflow_id}", json=updated_data, headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated DB Workflow Name"
    
    # Verify in DB
    # Fetch the original created_at time before update for comparison if needed
    # original_updated_at = created_workflow_definition.updated_at
    test_db_session.refresh(created_workflow_definition) # Refresh to get updated data from DB
    assert created_workflow_definition.name == "Updated DB Workflow Name"
    # assert created_workflow_definition.updated_at > original_updated_at

# ... (Keep other PUT tests: not_found, bad_mcp_id, auth tests, adapt their mcp_id checks for DB)

# === DELETE /workflows/{workflow_id} === (Should delete from test DB)
def test_delete_workflow_success(client: TestClient, created_workflow_definition: WorkflowDefinitionModel, jwt_headers: Dict[str, str], test_db_session: Session):
    workflow_id = str(created_workflow_definition.workflow_id)
    response = client.delete(f"/workflows/{workflow_id}", headers=jwt_headers)
    assert response.status_code == 204
    # Verify it's actually deleted from DB
    get_response = client.get(f"/workflows/{workflow_id}", headers=jwt_headers)
    assert get_response.status_code == 404
    db_workflow = test_db_session.query(WorkflowDefinitionModel).filter(WorkflowDefinitionModel.workflow_id == uuid.UUID(workflow_id)).first()
    assert db_workflow is None

# ... (Keep other DELETE tests)

# === POST /workflows/{workflow_id}/execute ===
# THIS IS THE MAIN SECTION TO UPDATE AND ADD NEW TESTS FOR DB-BACKED EXECUTION

def test_execute_workflow_success_db_backed(
    client: TestClient, 
    created_workflow_definition: WorkflowDefinitionModel, # Uses DB-backed workflow
    dummy_mcp_def: MCPModel, # Uses DB-backed MCP
    jwt_headers: Dict[str, str],
    test_db_session: Session # To inspect WorkflowRun
):
    workflow_id = str(created_workflow_definition.workflow_id)
    initial_inputs = {"initial_param": "start_value_for_db_exec"} # This matches the input key in created_workflow_definition
    
    # Modify the created_workflow_definition to ensure its input sourcing matches the initial_inputs key if necessary
    # The current created_workflow_definition fixture uses: 
    #   inputs={"param1": WorkflowStepInput(source_type=InputSourceType.STATIC_VALUE, value="value1_from_db_wf")}    
    # This needs to be changed to use WORKFLOW_INPUT for this test to be meaningful with initial_inputs.
    
    # Let's create a NEW workflow definition specifically for this execution test
    # that uses WORKFLOW_INPUT and the dummy_mcp_id.
    
    exec_wf_payload = WorkflowCreateSchema(
        name="Test Exec Workflow DB",
        steps=[
            WorkflowStep(
                name="Exec Step 1 DB",
                mcp_id=str(dummy_mcp_def.id),
                mcp_version_id="1.0.0", # Ensure this version exists
                inputs={
                    "input_data": WorkflowStepInput( # This matches the MockMCPServer's expected input
                        source_type=InputSourceType.WORKFLOW_INPUT,
                        workflow_input_key="trigger_input"
                    )
                }
            )
        ]
    )
    response_create = client.post("/workflows/", json=exec_wf_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response_create.status_code == 201
    exec_workflow_id = response_create.json()["workflow_id"]

    execute_payload = {"trigger_input": "Dynamic Value for Execution"}
    response = client.post(f"/workflows/{exec_workflow_id}/execute", json=execute_payload, headers=jwt_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["workflow_id"] == exec_workflow_id
    assert len(data["step_results"]) == 1
    step_result = data["step_results"][0]
    assert step_result["status"] == "SUCCESS"
    # Based on MockMCPServer's behavior in test_workflow_engine.py:
    assert step_result["outputs_generated"] == {"output": "Processed: Dynamic Value for Execution"}
    assert data["final_outputs"] == {"output": "Processed: Dynamic Value for Execution"}

    # Verify WorkflowRun in DB
    from mcp.db.models import WorkflowRun
    run_entry = test_db_session.query(WorkflowRun).filter(WorkflowRun.workflow_id == uuid.UUID(exec_workflow_id)).first()
    assert run_entry is not None
    assert run_entry.status == "SUCCESS"
    assert run_entry.inputs == execute_payload
    assert run_entry.outputs == {"output": "Processed: Dynamic Value for Execution"}

# Add more execute tests here:
def test_execute_workflow_step_mcp_def_not_found_in_db(
    client: TestClient, 
    jwt_headers: Dict[str, str],
    test_db_session: Session # To create workflow run, and check it later
):
    non_existent_mcp_id = str(uuid.uuid4())
    
    # Create a workflow definition that points to a non-existent MCP ID
    wf_payload = WorkflowCreateSchema(
        name="WF MCP Not Found DB",
        steps=[
            WorkflowStep(
                name="Step With Missing MCP",
                mcp_id=non_existent_mcp_id,
                mcp_version_id="1.0.0",
                inputs={}
            )
        ]
    )
    response_create = client.post("/workflows/", json=wf_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response_create.status_code == 201 # Workflow definition creation should succeed
    exec_workflow_id = response_create.json()["workflow_id"]

    execute_payload = {}
    response = client.post(f"/workflows/{exec_workflow_id}/execute", json=execute_payload, headers=jwt_headers)
    
    assert response.status_code == 200 # The API call itself is okay, the workflow execution fails
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["workflow_id"] == exec_workflow_id
    assert "MCP instance for ID" in data["error_message"]
    assert non_existent_mcp_id in data["error_message"]
    assert "not found or failed to instantiate" in data["error_message"]
    assert len(data["step_results"]) == 0 # Should fail before any step execution attempt if MCP can't be loaded

    # Verify WorkflowRun in DB
    from mcp.db.models import WorkflowRun
    run_entry = test_db_session.query(WorkflowRun).filter(WorkflowRun.workflow_id == uuid.UUID(exec_workflow_id)).order_by(WorkflowRun.created_at.desc()).first()
    assert run_entry is not None
    assert run_entry.status == "FAILED"
    assert "MCP instance for ID" in run_entry.error_message
    assert non_existent_mcp_id in run_entry.error_message

# - MCP version not found in DB for a step
# - MCP instantiation fails (e.g., bad config in DB loaded by get_mcp_instance_from_db)

# (Keep original execute tests for not_found, auth, etc., they should still be valid)
# test_execute_workflow_not_found(...)
# test_execute_workflow_no_jwt(...)
# test_execute_workflow_invalid_jwt(...)

# Add more tests: invalid workflow definitions, complex step dependencies, error handling in steps, etc. 

def test_execute_workflow_step_mcp_version_not_found(
    client: TestClient, 
    dummy_mcp_def: MCPModel, # Use an existing MCP definition
    jwt_headers: Dict[str, str],
    test_db_session: Session
):
    existing_mcp_id = str(dummy_mcp_def.id)
    non_existent_mcp_version_id = "9.9.9"
    
    wf_payload = WorkflowCreateSchema(
        name="WF MCP Version Not Found",
        steps=[
            WorkflowStep(
                name="Step With Missing MCP Version",
                mcp_id=existing_mcp_id,
                mcp_version_id=non_existent_mcp_version_id,
                inputs={}
            )
        ]
    )
    response_create = client.post("/workflows/", json=wf_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response_create.status_code == 201
    exec_workflow_id = response_create.json()["workflow_id"]

    execute_payload = {}
    response = client.post(f"/workflows/{exec_workflow_id}/execute", json=execute_payload, headers=jwt_headers)
    
    assert response.status_code == 200 
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["workflow_id"] == exec_workflow_id
    assert f"MCP instance for ID '{existing_mcp_id}' (Version: {non_existent_mcp_version_id}) not found or failed to instantiate." in data["error_message"]
    assert len(data["step_results"]) == 0

    # Verify WorkflowRun in DB
    from mcp.db.models import WorkflowRun
    run_entry = test_db_session.query(WorkflowRun).filter(WorkflowRun.workflow_id == uuid.UUID(exec_workflow_id)).order_by(WorkflowRun.created_at.desc()).first()
    assert run_entry is not None
    assert run_entry.status == "FAILED"
    assert f"MCP instance for ID '{existing_mcp_id}' (Version: {non_existent_mcp_version_id}) not found or failed to instantiate." in run_entry.error_message

# - MCP instantiation fails (e.g., bad config in DB loaded by get_mcp_instance_from_db)
# - Step execution fails, check WorkflowRun status and error 

def test_execute_workflow_mcp_instantiation_failure_bad_config(
    client: TestClient, 
    dummy_mcp_def: MCPModel, # Use an existing MCP definition
    jwt_headers: Dict[str, str],
    test_db_session: Session
):
    mcp_id = str(dummy_mcp_def.id)
    mcp_version_str = "1.0.0" # Matches the version created by dummy_mcp_def

    # Directly tamper with the MCPVersion's config_snapshot in the DB
    # to make it invalid for the Pydantic model used by the MCP type.
    # dummy_mcp_def is PYTHON_SCRIPT, its config is PythonScriptConfig (expects "script_content": str)
    mcp_version_entry = test_db_session.query(MCPVersionModel).filter(
        MCPVersionModel.mcp_id == dummy_mcp_def.id, 
        MCPVersionModel.version_str == mcp_version_str
    ).first()
    assert mcp_version_entry is not None
    
    # Corrupt the config by providing something that PythonScriptConfig cannot parse
    mcp_version_entry.config_snapshot = {"invalid_config_key": 12345} # This is not PythonScriptConfig
    test_db_session.add(mcp_version_entry)
    test_db_session.commit()
    test_db_session.refresh(mcp_version_entry)

    # Create a workflow that uses this MCP and version
    wf_payload = WorkflowCreateSchema(
        name="WF MCP Bad Config",
        steps=[
            WorkflowStep(
                name="Step With Bad MCP Config",
                mcp_id=mcp_id,
                mcp_version_id=mcp_version_str,
                inputs={}
            )
        ]
    )
    response_create = client.post("/workflows/", json=wf_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response_create.status_code == 201
    exec_workflow_id = response_create.json()["workflow_id"]

    execute_payload = {}
    response = client.post(f"/workflows/{exec_workflow_id}/execute", json=execute_payload, headers=jwt_headers)
    
    assert response.status_code == 200 
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["workflow_id"] == exec_workflow_id
    # The error message comes from WorkflowEngine when get_mcp_instance_from_db returns None
    assert f"MCP instance for ID '{mcp_id}' (Version: {mcp_version_str}) not found or failed to instantiate." in data["error_message"]
    assert len(data["step_results"]) == 0

    # Verify WorkflowRun in DB
    from mcp.db.models import WorkflowRun
    run_entry = test_db_session.query(WorkflowRun).filter(WorkflowRun.workflow_id == uuid.UUID(exec_workflow_id)).order_by(WorkflowRun.created_at.desc()).first()
    assert run_entry is not None
    assert run_entry.status == "FAILED"
    assert f"MCP instance for ID '{mcp_id}' (Version: {mcp_version_str}) not found or failed to instantiate." in run_entry.error_message

# - Step execution fails, check WorkflowRun status and error 

def test_execute_workflow_step_execution_failure(
    client: TestClient, 
    dummy_mcp_def: MCPModel,
    jwt_headers: Dict[str, str],
    test_db_session: Session
):
    mcp_id = str(dummy_mcp_def.id)
    mcp_version_str = "1.0.0"

    # The dummy_mcp_def is a PythonScriptMCP. Its script_content is:
    # "print('Hello from DB-backed workflow test MCP')"
    # To make it fail, we can rely on the MockMCPServer logic if we could inject it,
    # but these are integration tests. So, we need an MCP type that can be configured to fail,
    # or we modify the script content of the dummy_mcp_def for this test to cause an error.

    # For this test, let's assume the PythonScriptMCP will fail if its script is bad.
    # We'll create a new MCP version with a failing script.
    failing_script_content = "raise Exception('Simulated script failure')"
    
    mcp_version_entry = test_db_session.query(MCPVersionModel).filter(
        MCPVersionModel.mcp_id == dummy_mcp_def.id, 
        MCPVersionModel.version_str == mcp_version_str
    ).first()
    assert mcp_version_entry is not None
    original_config = mcp_version_entry.config_snapshot

    # Update config to make it fail
    mcp_version_entry.config_snapshot = {"script_content": failing_script_content}
    test_db_session.add(mcp_version_entry)
    test_db_session.commit()
    test_db_session.refresh(mcp_version_entry)

    wf_payload = WorkflowCreateSchema(
        name="WF Step Fail Test",
        steps=[
            WorkflowStep(
                name="Step Designed to Fail",
                mcp_id=mcp_id,
                mcp_version_id=mcp_version_str,
                inputs={}
            )
        ]
    )
    response_create = client.post("/workflows/", json=wf_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response_create.status_code == 201
    exec_workflow_id = response_create.json()["workflow_id"]

    execute_payload = {}
    response = client.post(f"/workflows/{exec_workflow_id}/execute", json=execute_payload, headers=jwt_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["workflow_id"] == exec_workflow_id
    assert len(data["step_results"]) == 1
    step_result = data["step_results"][0]
    assert step_result["status"] == "FAILED"
    assert "Simulated script failure" in step_result["error"] 
    assert "Simulated script failure" in data["error_message"] # Workflow error message should reflect step error

    # Verify WorkflowRun in DB
    from mcp.db.models import WorkflowRun
    run_entry = test_db_session.query(WorkflowRun).filter(WorkflowRun.workflow_id == uuid.UUID(exec_workflow_id)).order_by(WorkflowRun.created_at.desc()).first()
    assert run_entry is not None
    assert run_entry.status == "FAILED"
    assert "Simulated script failure" in run_entry.error_message
    assert run_entry.results_log[0]["error"] is not None
    assert "Simulated script failure" in run_entry.results_log[0]["error"]

    # Clean up: Restore original config if other tests might use dummy_mcp_def
    # However, test_db_session fixture drops and recreates tables, so this might not be strictly necessary
    # on a per-test basis if dummy_mcp_def is function-scoped.
    # If dummy_mcp_def was session-scoped, cleanup would be critical.
    mcp_version_entry.config_snapshot = original_config
    test_db_session.add(mcp_version_entry)
    test_db_session.commit()

# (Keep original execute tests for not_found, auth, etc., they should still be valid)
# test_execute_workflow_not_found(...)
# test_execute_workflow_no_jwt(...)
# test_execute_workflow_invalid_jwt(...)

# Add more tests: invalid workflow definitions, complex step dependencies, error handling in steps, etc. 

def test_execute_workflow_step_mcp_version_not_found(
    client: TestClient, 
    dummy_mcp_def: MCPModel, # Use an existing MCP definition
    jwt_headers: Dict[str, str],
    test_db_session: Session
):
    existing_mcp_id = str(dummy_mcp_def.id)
    non_existent_mcp_version_id = "9.9.9"
    
    wf_payload = WorkflowCreateSchema(
        name="WF MCP Version Not Found",
        steps=[
            WorkflowStep(
                name="Step With Missing MCP Version",
                mcp_id=existing_mcp_id,
                mcp_version_id=non_existent_mcp_version_id,
                inputs={}
            )
        ]
    )
    response_create = client.post("/workflows/", json=wf_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response_create.status_code == 201
    exec_workflow_id = response_create.json()["workflow_id"]

    execute_payload = {}
    response = client.post(f"/workflows/{exec_workflow_id}/execute", json=execute_payload, headers=jwt_headers)
    
    assert response.status_code == 200 
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["workflow_id"] == exec_workflow_id
    assert f"MCP instance for ID '{existing_mcp_id}' (Version: {non_existent_mcp_version_id}) not found or failed to instantiate." in data["error_message"]
    assert len(data["step_results"]) == 0

    # Verify WorkflowRun in DB
    from mcp.db.models import WorkflowRun
    run_entry = test_db_session.query(WorkflowRun).filter(WorkflowRun.workflow_id == uuid.UUID(exec_workflow_id)).order_by(WorkflowRun.created_at.desc()).first()
    assert run_entry is not None
    assert run_entry.status == "FAILED"
    assert f"MCP instance for ID '{existing_mcp_id}' (Version: {non_existent_mcp_version_id}) not found or failed to instantiate." in run_entry.error_message

# - MCP instantiation fails (e.g., bad config in DB loaded by get_mcp_instance_from_db)
# - Step execution fails, check WorkflowRun status and error 

def test_execute_workflow_mcp_instantiation_failure_bad_config(
    client: TestClient, 
    dummy_mcp_def: MCPModel, # Use an existing MCP definition
    jwt_headers: Dict[str, str],
    test_db_session: Session
):
    mcp_id = str(dummy_mcp_def.id)
    mcp_version_str = "1.0.0" # Matches the version created by dummy_mcp_def

    # Directly tamper with the MCPVersion's config_snapshot in the DB
    # to make it invalid for the Pydantic model used by the MCP type.
    # dummy_mcp_def is PYTHON_SCRIPT, its config is PythonScriptConfig (expects "script_content": str)
    mcp_version_entry = test_db_session.query(MCPVersionModel).filter(
        MCPVersionModel.mcp_id == dummy_mcp_def.id, 
        MCPVersionModel.version_str == mcp_version_str
    ).first()
    assert mcp_version_entry is not None
    
    # Corrupt the config by providing something that PythonScriptConfig cannot parse
    mcp_version_entry.config_snapshot = {"invalid_config_key": 12345} # This is not PythonScriptConfig
    test_db_session.add(mcp_version_entry)
    test_db_session.commit()
    test_db_session.refresh(mcp_version_entry)

    # Create a workflow that uses this MCP and version
    wf_payload = WorkflowCreateSchema(
        name="WF MCP Bad Config",
        steps=[
            WorkflowStep(
                name="Step With Bad MCP Config",
                mcp_id=mcp_id,
                mcp_version_id=mcp_version_str,
                inputs={}
            )
        ]
    )
    response_create = client.post("/workflows/", json=wf_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response_create.status_code == 201
    exec_workflow_id = response_create.json()["workflow_id"]

    execute_payload = {}
    response = client.post(f"/workflows/{exec_workflow_id}/execute", json=execute_payload, headers=jwt_headers)
    
    assert response.status_code == 200 
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["workflow_id"] == exec_workflow_id
    # The error message comes from WorkflowEngine when get_mcp_instance_from_db returns None
    assert f"MCP instance for ID '{mcp_id}' (Version: {mcp_version_str}) not found or failed to instantiate." in data["error_message"]
    assert len(data["step_results"]) == 0

    # Verify WorkflowRun in DB
    from mcp.db.models import WorkflowRun
    run_entry = test_db_session.query(WorkflowRun).filter(WorkflowRun.workflow_id == uuid.UUID(exec_workflow_id)).order_by(WorkflowRun.created_at.desc()).first()
    assert run_entry is not None
    assert run_entry.status == "FAILED"
    assert f"MCP instance for ID '{mcp_id}' (Version: {mcp_version_str}) not found or failed to instantiate." in run_entry.error_message

# - Step execution fails, check WorkflowRun status and error 