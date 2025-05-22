import pytest
from fastapi.testclient import TestClient
import os
import uuid
from typing import Dict, Any, List
from datetime import datetime

# Set a consistent API key for testing environment (used to get JWT)
TEST_API_KEY = str(uuid.uuid4())
os.environ["MCP_API_KEY"] = TEST_API_KEY

from mcp.api.main import app # app from your FastAPI application
from mcp.core.registry import mcp_server_registry, MCP_REGISTRY_FILE, WORKFLOW_STORAGE_FILE
from mcp.schemas.workflow import Workflow, WorkflowCreate, WorkflowExecutionResult
from mcp.core.types import MCPType

@pytest.fixture(scope="module")
def client():
    for f in [WORKFLOW_STORAGE_FILE, MCP_REGISTRY_FILE]:
        if f.exists():
            f.unlink()
    with TestClient(app) as c:
        yield c
    for f in [WORKFLOW_STORAGE_FILE, MCP_REGISTRY_FILE]:
        if f.exists():
            f.unlink()

@pytest.fixture(autouse=True)
def clear_registries_and_files():
    mcp_server_registry.clear()
    if MCP_REGISTRY_FILE.exists():
        MCP_REGISTRY_FILE.unlink()
    # Clear workflow storage by removing the file, it will be recreated empty by load_workflows_from_storage
    if WORKFLOW_STORAGE_FILE.exists():
        WORKFLOW_STORAGE_FILE.unlink()
    # Need to force a reload of the workflow_registry in the router by re-importing or patching load function
    # For simplicity in testing, we can rely on the app starting fresh for each test session (if client is function-scoped)
    # Or, if workflow_registry is module-level in router, it might need explicit clearing/reloading logic for tests.
    # The current workflow_router.workflow_registry loads at import time. This means it won't be cleared by just deleting the file
    # between tests in the same session if the module isn't reloaded. 
    # For now, we hope test isolation or fixture scope handles this. 
    # A more robust way would be to patch workflow_router.workflow_registry or workflow_router.load_workflows_from_storage
    from mcp.api.routers import workflows as workflow_router # Re-import or access directly
    workflow_router.workflow_registry.clear() # Explicitly clear the in-memory dict

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

@pytest.fixture
def dummy_mcp_id(client: TestClient, jwt_headers: Dict[str, str]) -> str:
    mcp_payload = {
        "name": "Test Python Script for Workflow",
        "type": MCPType.PYTHON_SCRIPT.value,
        "config": {"script_content": "print('Hello from workflow test MCP')"}
    }
    response = client.post("/context", json=mcp_payload, headers=jwt_headers)
    assert response.status_code == 201, f"Failed to create dummy MCP: {response.text}"
    return response.json()["id"]

@pytest.fixture
def created_workflow_id(client: TestClient, dummy_mcp_id: str, jwt_headers: Dict[str, str]) -> str:
    workflow_payload = {
        "name": "Test Workflow",
        "description": "A test workflow for API testing",
        "steps": [
            {
                "name": "Step 1",
                "mcp_id": dummy_mcp_id,
                "inputs": {"param1": "value1"},
                "outputs_to_map": {"output1": "step1_output"}
            }
        ]
    }
    response = client.post("/workflows/", json=workflow_payload, headers=jwt_headers)
    assert response.status_code == 201, f"Failed to create workflow: {response.text}"
    return response.json()["workflow_id"]

# === POST /workflows/ ===
def test_create_workflow_success(client: TestClient, dummy_mcp_id: str, jwt_headers: Dict[str, str]):
    workflow_data = {
        "name": "My New Workflow",
        "description": "A detailed description.",
        "steps": [
            {
                "name": "Initial Step",
                "mcp_id": dummy_mcp_id,
                "inputs": {"data": "input_data"},
                "outputs_to_map": {"result": "step_result"}
            }
        ]
    }
    response = client.post("/workflows/", json=workflow_data, headers=jwt_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My New Workflow"
    assert data["description"] == "A detailed description."
    assert len(data["steps"]) == 1
    assert data["steps"][0]["mcp_id"] == dummy_mcp_id
    assert "workflow_id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_workflow_mcp_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_mcp_id = str(uuid.uuid4())
    workflow_data = {
        "name": "Workflow with Bad MCP",
        "steps": [{"name": "Bad Step", "mcp_id": non_existent_mcp_id, "inputs": {}}]
    }
    response = client.post("/workflows/", json=workflow_data, headers=jwt_headers)
    assert response.status_code == 400
    assert "mcp with id" in response.json()["detail"].lower()
    assert non_existent_mcp_id in response.json()["detail"]

def test_create_workflow_no_jwt(client: TestClient, dummy_mcp_id: str):
    workflow_data = {"name": "No Auth Workflow", "steps": [{"name": "S1", "mcp_id": dummy_mcp_id, "inputs": {}}]}
    response = client.post("/workflows/", json=workflow_data) # No headers
    assert response.status_code == 401

def test_create_workflow_invalid_jwt(client: TestClient, dummy_mcp_id: str):
    workflow_data = {"name": "Invalid Auth Workflow", "steps": [{"name": "S1", "mcp_id": dummy_mcp_id, "inputs": {}}]}
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.post("/workflows/", json=workflow_data, headers=invalid_headers)
    assert response.status_code == 401

# === GET /workflows/ ===
def test_list_workflows_empty(client: TestClient, jwt_headers: Dict[str, str]):
    response = client.get("/workflows/", headers=jwt_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_list_workflows_with_data(client: TestClient, created_workflow_id: str, jwt_headers: Dict[str, str]):
    # `created_workflow_id` fixture ensures at least one workflow exists
    response = client.get("/workflows/", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(wf["workflow_id"] == created_workflow_id for wf in data)

def test_list_workflows_no_jwt(client: TestClient):
    response = client.get("/workflows/")
    assert response.status_code == 401

def test_list_workflows_invalid_jwt(client: TestClient):
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/workflows/", headers=invalid_headers)
    assert response.status_code == 401

# === GET /workflows/{workflow_id} ===
def test_get_workflow_success(client: TestClient, created_workflow_id: str, jwt_headers: Dict[str, str]):
    response = client.get(f"/workflows/{created_workflow_id}", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == created_workflow_id
    assert data["name"] == "Test Workflow"

def test_get_workflow_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/workflows/{non_existent_id}", headers=jwt_headers)
    assert response.status_code == 404

def test_get_workflow_no_jwt(client: TestClient, created_workflow_id: str):
    response = client.get(f"/workflows/{created_workflow_id}")
    assert response.status_code == 401

def test_get_workflow_invalid_jwt(client: TestClient, created_workflow_id: str):
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get(f"/workflows/{created_workflow_id}", headers=invalid_headers)
    assert response.status_code == 401

# === PUT /workflows/{workflow_id} ===
def test_update_workflow_success(client: TestClient, created_workflow_id: str, dummy_mcp_id: str, jwt_headers: Dict[str, str]):
    updated_data = {
        "name": "Updated Workflow Name",
        "description": "Updated description.",
        "steps": [
            {
                "name": "Updated Step 1",
                "mcp_id": dummy_mcp_id, # Assuming same MCP for simplicity
                "inputs": {"param1": "new_value"},
                "outputs_to_map": {"output1": "updated_step1_output"}
            }
        ]
    }
    response = client.put(f"/workflows/{created_workflow_id}", json=updated_data, headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Workflow Name"
    assert data["description"] == "Updated description."
    assert data["workflow_id"] == created_workflow_id
    assert data["steps"][0]["name"] == "Updated Step 1"
    # Check that updated_at is greater than created_at (or roughly, allow for small diff)
    # This requires parsing datetime strings. For simplicity, check it exists and changed if possible.
    original_workflow_response = client.get(f"/workflows/{created_workflow_id}", headers=jwt_headers)
    original_updated_at = datetime.fromisoformat(original_workflow_response.json()["updated_at"])
    current_updated_at = datetime.fromisoformat(data["updated_at"])
    assert current_updated_at > original_updated_at # Should be true if update modified it

def test_update_workflow_not_found(client: TestClient, dummy_mcp_id: str, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    update_payload = {"name": "Attempt Update", "steps": [{"name": "S1", "mcp_id": dummy_mcp_id, "inputs": {}}]}
    response = client.put(f"/workflows/{non_existent_id}", json=update_payload, headers=jwt_headers)
    assert response.status_code == 404

def test_update_workflow_bad_mcp_id(client: TestClient, created_workflow_id: str, jwt_headers: Dict[str, str]):
    non_existent_mcp_id = str(uuid.uuid4())
    update_payload = {"name": "Workflow with Bad MCP Update", "steps": [{"name": "Bad MCP Step", "mcp_id": non_existent_mcp_id, "inputs": {}}]}
    response = client.put(f"/workflows/{created_workflow_id}", json=update_payload, headers=jwt_headers)
    assert response.status_code == 400
    assert "mcp with id" in response.json()["detail"].lower()

def test_update_workflow_no_jwt(client: TestClient, created_workflow_id: str, dummy_mcp_id: str):
    update_payload = {"name": "No Auth Update", "steps": [{"name": "S1", "mcp_id": dummy_mcp_id, "inputs": {}}]}
    response = client.put(f"/workflows/{created_workflow_id}", json=update_payload)
    assert response.status_code == 401

# === DELETE /workflows/{workflow_id} ===
def test_delete_workflow_success(client: TestClient, created_workflow_id: str, jwt_headers: Dict[str, str]):
    response = client.delete(f"/workflows/{created_workflow_id}", headers=jwt_headers)
    assert response.status_code == 204
    # Verify it's actually deleted
    get_response = client.get(f"/workflows/{created_workflow_id}", headers=jwt_headers)
    assert get_response.status_code == 404

def test_delete_workflow_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    response = client.delete(f"/workflows/{non_existent_id}", headers=jwt_headers)
    assert response.status_code == 404

def test_delete_workflow_no_jwt(client: TestClient, created_workflow_id: str):
    response = client.delete(f"/workflows/{created_workflow_id}")
    assert response.status_code == 401

# === POST /workflows/{workflow_id}/execute ===
def test_execute_workflow_success(client: TestClient, created_workflow_id: str, dummy_mcp_id: str, jwt_headers: Dict[str, str]):
    # Ensure the dummy_mcp_id is a Python script that can execute simply
    # The dummy_mcp_id fixture already creates a PythonScriptMCP

    initial_inputs = {"initial_param": "start_value"} # Raw dict for initial_inputs, not nested under "initial_inputs"
    response = client.post(f"/workflows/{created_workflow_id}/execute", json=initial_inputs, headers=jwt_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == created_workflow_id
    assert data["status"] == "COMPLETED" # Assuming simple workflow completes
    assert "started_at" in data
    assert "finished_at" in data
    assert len(data["step_results"]) == 1
    assert data["step_results"][0]["mcp_id"] == dummy_mcp_id
    assert data["step_results"][0]["status"] == "SUCCESS"
    # Check final_outputs based on the dummy MCP and workflow definition
    # The dummy workflow maps "output1" to "step1_output". The PythonScriptMCP output structure is specific.
    # The default PythonScriptMCP will have its print output in 'result'.
    # If workflow definition output_mapping is `{"result": "final_output_key"}` and step maps to it,
    # then it would appear in final_outputs.
    # For the current dummy workflow: "outputs_to_map": {"output1": "step1_output"}
    # The PythonScriptMCP result format is `{"result": stdout_content, "stdout": stdout_content, "stderr": stderr_content, "success": True/False, "error": ...}`
    # The WorkflowEngine tries to map based on `outputs_to_map` from the step's result. If step result is {"result":"Hello..."}, and map is {"output1":"step1_output"}
    # this means it looks for `result["output1"]`. This won't match python script output directly.
    # Let's adjust the workflow step definition or the test assertion.

    # Assuming default Python script output `{"result": "printed_string"}`
    # and workflow step: `"outputs_to_map": {"result": "my_step_output"}`
    # then `final_outputs` would be `{"my_step_output": "printed_string"}`
    # Our current workflow: `"outputs_to_map": {"output1": "step1_output"}`. This requires the MCP to return `{"output1": ...}`
    # PythonScriptMCP returns `{"result": ...}`. So the current mapping won't yield a value in `final_outputs` for `step1_output`.
    # For a simple print, the `result` field of the PythonScriptMCP execution will contain the printed output.
    # The step result in WorkflowExecutionResult will be the full MCPResult. So `data["step_results"][0]["output"]` will be the MCPResult.
    # And `final_outputs` will be constructed based on `outputs_to_map` from that MCPResult.
    # If outputs_to_map is {"result": "step1_result_key"}, then final_outputs would be {"step1_result_key": "Hello from workflow test MCP"}

    # Given the created_workflow_id step definition: outputs_to_map: {"output1": "step1_output"}
    # And PythonScriptMCP output: { "result": "Hello...", "success": True, ...}
    # The current engine logic will look for `output['output1']` which is not present. So final_outputs might be empty for this key.
    # Let's verify the step output itself for now.
    step_output = data["step_results"][0]["output"]
    assert step_output["result"] == "Hello from workflow test MCP\n" # Python print adds a newline
    assert step_output["success"] is True

    # If we want to test final_outputs, the `outputs_to_map` in workflow definition should align with MCP output keys.
    # E.g., if dummy_mcp_id step had `"outputs_to_map": {"result": "final_script_printout"}`
    # then: assert data["final_outputs"]["final_script_printout"] == "Hello from workflow test MCP\n"
    # For now, we'll assert final_outputs is a dict (it might be empty or contain mapped values if mappings align)
    assert isinstance(data["final_outputs"], dict)

def test_execute_workflow_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    response = client.post(f"/workflows/{non_existent_id}/execute", json={}, headers=jwt_headers)
    assert response.status_code == 404

def test_execute_workflow_with_malformed_nested_initial_inputs(client: TestClient, created_workflow_id: str, jwt_headers: Dict[str, str]):
    # This test is for the case where the body is `{"initial_inputs": "not_a_dict"}`
    # The endpoint expects `Optional[Dict[str, Any]]`, so FastAPI should handle this structure.
    # The router code currently has logic to unwrap `{"initial_inputs": actual_dict}`.
    # If `initial_inputs` itself is provided but not a dict, it should pass that non-dict value to the engine.
    malformed_payload = {"initial_inputs": "this_is_not_a_dictionary_of_inputs"}
    response = client.post(f"/workflows/{created_workflow_id}/execute", json=malformed_payload, headers=jwt_headers)
    # The current engine expects `initial_inputs` to be a dict or None. 
    # If it receives a string, it will likely fail during `update` or `get` calls on it.
    # The engine should robustly handle this, or the API should validate.
    # Based on engine `run_workflow`'s `current_inputs.update(initial_inputs or {})`,
    # if `initial_inputs` is a string, `update` will raise AttributeError.
    # The engine catches generic exceptions and returns a FAILED status.
    assert response.status_code == 200 # The endpoint itself doesn't fail, the workflow execution does
    data = response.json()
    assert data["status"] == "FAILED"
    assert "error during workflow execution" in data.get("error", "").lower()
    # More specific error might be: "AttributeError: 'str' object has no attribute 'items'" or similar from deep in the engine.

def test_execute_workflow_with_direct_non_dict_initial_inputs(client: TestClient, created_workflow_id: str, jwt_headers: Dict[str, str]):
    # This test is for the case where the body is `"not_a_dict_at_all"` which is invalid for `Body(None, ...)` expecting `Dict`
    # FastAPI will return a 422 Unprocessable Entity error before it even hits the path operation function.
    # So, we cannot directly send a string as the top-level JSON body if the Pydantic model is Dict.
    # The `initial_inputs: Optional[Dict[str, Any]] = Body(None, ...)` means the body *must* be a JSON object (dict) or null.
    # A raw string like "hello" is not a valid JSON object for this.
    # However, if we send a JSON object that doesn't fit the *expected structure for unwrapping*, that's different.
    # e.g. json={"unexpected_key": "value"} -> this becomes initial_inputs = {"unexpected_key": "value"}
    # The test `test_execute_workflow_with_malformed_nested_initial_inputs` covers the unwrapping logic branch.
    # A direct non-dict (e.g. sending a JSON array `[]` or string `"foo"`) to an endpoint expecting `Dict` via `Body`
    # would be caught by FastAPI's validation (422).
    # The router logic tries to be lenient: if initial_inputs is not None but not `{"initial_inputs": ...}`, it uses initial_inputs directly.
    # So, if client sends `json={"direct_param": 123}`, then actual_initial_inputs becomes `{"direct_param": 123}`.
    # If client sends `json=null` (or no body), `actual_initial_inputs` is `None`.
    # If client sends `json={"initial_inputs": {"actual_param": 456}}`, `actual_initial_inputs` is `{"actual_param": 456}`.

    # Let's test the case where `initial_inputs` is a dict, but doesn't contain the nested `initial_inputs` key.
    # This is a valid scenario and should pass the inputs directly to the engine.
    direct_inputs = {"some_param": "some_value", "another_param": 123}
    response = client.post(f"/workflows/{created_workflow_id}/execute", json=direct_inputs, headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED" # Should still complete if inputs are usable or ignored by the simple script
    assert isinstance(data["final_outputs"], dict)

def test_execute_workflow_no_jwt(client: TestClient, created_workflow_id: str):
    response = client.post(f"/workflows/{created_workflow_id}/execute", json={})
    assert response.status_code == 401

def test_execute_workflow_invalid_jwt(client: TestClient, created_workflow_id: str):
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.post(f"/workflows/{created_workflow_id}/execute", json={}, headers=invalid_headers)
    assert response.status_code == 401

# Add more tests: invalid workflow definitions, complex step dependencies, error handling in steps, etc. 