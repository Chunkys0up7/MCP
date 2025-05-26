import os
import uuid
from datetime import datetime
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

# Set a consistent API key for testing environment
TEST_API_KEY = str(uuid.uuid4())
os.environ["MCP_API_KEY"] = TEST_API_KEY

# Now import the app after setting the env var
from mcp.api.main import app  # app from your FastAPI application
from mcp.api.routers.workflows import (  # For cleanup and direct inspection
    WORKFLOW_STORAGE_FILE, save_workflows_to_storage, workflow_registry)
from mcp.core.registry import (MCP_REGISTRY_FILE,  # Added MCP_REGISTRY_FILE
                               WORKFLOW_STORAGE_FILE, mcp_server_registry)
from mcp.core.types import MCPType  # Import MCPType
from mcp.schemas.workflow import InputSourceType, Workflow


@pytest.fixture(scope="module")
def client():
    # Clean up storage files before and after tests
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
    workflow_registry.clear()
    save_workflows_to_storage(workflow_registry)
    mcp_server_registry.clear()  # Clear MCP registry as well
    # Save empty MCP registry (optional, as it might be reloaded by app, but good for clean slate)
    if MCP_REGISTRY_FILE.exists():
        MCP_REGISTRY_FILE.unlink()
    # Re-initialize mcp_server_registry by calling the function that loads it in main.py if necessary, or ensure test client reloads app
    # For now, clearing the global should be mostly fine if app import re-evaluates its globals or loads fresh.
    # However, the app instance for TestClient is created once.
    # A better way might be to manage the mcp_registry.json file directly for mcp_server_registry state.


# --- Helper Data ---
def get_headers() -> Dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}


SAMPLE_MCP_ID_VALID = "mcp_passthrough_string_v1"  # Assume this MCP is registered in mcp_server_registry for some tests
SAMPLE_MCP_ID_INVALID = "non_existent_mcp_v1"


@pytest.fixture(
    scope="function"
)  # Changed to function scope for cleaner state if tests modify it
def ensure_passthrough_mcp_exists(client: TestClient):
    """Ensures the SAMPLE_MCP_ID_VALID (mcp_passthrough_string_v1) exists via API call."""
    # Check if it already exists to avoid re-creation if not necessary for some test setups
    # However, given clear_registries_and_files, it should be created each time this fixture is used.

    mcp_payload = {
        "name": "Passthrough String MCP for Tests",
        "type": MCPType.PYTHON_SCRIPT.value,  # Assuming PythonScriptMCP can act as a passthrough
        "description": "A simple passthrough MCP.",
        "config": {
            "script_path": "",  # Placeholder, actual passthrough logic would be in PythonScriptMCP
            "script_content": "def execute(inputs: dict):\\n    return inputs.get('input_string', 'default_passthrough_output')",
            "requirements": [],
            # Add id, name, description, type to config as per PythonScriptConfig model if they are part of it
            # Based on PythonScriptConfig, these top-level fields are not part of 'config' dict but are set from MCPCreationRequest
        },
    }
    # Override the ID for predictable testing if POST /context allows specifying ID or if we retrieve it
    # The current POST /context generates its own ID. We need to use that generated ID.
    # Let's assume SAMPLE_MCP_ID_VALID is the *name* we will give it, and then find its ID.
    # For simplicity, let's assume the mcp_server_registry is populated correctly by the app for basic types like PythonScript.
    # If mcp_passthrough_string_v1 is a *specific implementation* that needs to be loaded, this fixture must ensure that.

    # For now, let's assume a PythonScriptMCP with a specific name can fulfill this.
    # The test_create_workflow_success relies on this MCP_ID being valid.
    # The workflow router directly checks mcp_id in mcp_server_registry.

    # The easiest way to ensure it for tests, without complex file manipulation, is to add it directly to the registry for the test session.
    # This bypasses the API for this specific setup, making tests more direct for workflow logic.
    if SAMPLE_MCP_ID_VALID not in mcp_server_registry:
        # Mock a simple PythonScriptMCP instance for testing purposes
        from mcp.core.python_script import PythonScriptConfig, PythonScriptMCP

        mock_config_data = {
            "id": SAMPLE_MCP_ID_VALID,  # Use the known ID
            "name": "Test Passthrough MCP",
            "type": MCPType.PYTHON_SCRIPT,
            "description": "A mock passthrough script for testing workflows.",
            "script_content": 'def execute(inputs: dict):\n    return {"success": True, "result": inputs.get(\'input_string\', \'default_passthrough_output\'), "error": None}',
        }
        mock_config = PythonScriptConfig(**mock_config_data)
        mock_mcp_instance = PythonScriptMCP(config=mock_config)
        mcp_server_registry[SAMPLE_MCP_ID_VALID] = {
            "id": SAMPLE_MCP_ID_VALID,
            "name": mock_config.name,
            "description": mock_config.description,
            "type": mock_config.type.value,
            "config": mock_config.model_dump(),
            "instance": mock_mcp_instance,
        }
    return SAMPLE_MCP_ID_VALID


@pytest.fixture
def sample_workflow_payload(ensure_passthrough_mcp_exists: str) -> Dict[str, Any]:
    # Now SAMPLE_MCP_ID_VALID is guaranteed to be in the registry for this test
    mcp_id_to_use = ensure_passthrough_mcp_exists
    return {
        "name": "Test Workflow - Minimal",
        "description": "A basic workflow for API testing.",
        "execution_mode": "sequential",
        "error_handling": {
            "strategy": "Stop on Error",
        },
        "steps": [
            {
                "mcp_id": mcp_id_to_use,
                "name": "Step 1 - Echo Input",
                "inputs": {
                    "input_string": {
                        "source_type": InputSourceType.WORKFLOW_INPUT.value,
                        "workflow_input_key": "main_input",
                    }
                },
            }
        ],
    }


@pytest.fixture
def create_sample_workflow(
    client: TestClient, sample_workflow_payload: Dict[str, Any]
) -> Workflow:
    """Helper fixture to pre-populate a workflow for tests that need one."""
    response = client.post(
        "/workflows/", json=sample_workflow_payload, headers=get_headers()
    )
    assert response.status_code == 201
    return Workflow(**response.json())


# --- Test Cases ---


# === Authentication Tests ===
def test_create_workflow_no_api_key(
    client: TestClient, sample_workflow_payload: Dict[str, Any]
):
    response = client.post("/workflows/", json=sample_workflow_payload)
    assert (
        response.status_code == 403
    )  # Expecting 403 due to auto_error=True in APIKeyHeader
    assert (
        "Not authenticated" in response.json().get("detail", "").lower()
        or "api key" in response.json().get("detail", "").lower()
    )  # More flexible check for auth error messages


def test_create_workflow_invalid_api_key(
    client: TestClient, sample_workflow_payload: Dict[str, Any]
):
    response = client.post(
        "/workflows/", json=sample_workflow_payload, headers={"X-API-Key": "invalidkey"}
    )
    assert response.status_code == 403
    assert "invalid api key" in response.json().get("detail", "").lower()


# === POST /workflows/ ===
def test_create_workflow_success(
    client: TestClient, sample_workflow_payload: Dict[str, Any]
):
    response = client.post(
        "/workflows/", json=sample_workflow_payload, headers=get_headers()
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_workflow_payload["name"]
    assert "workflow_id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert len(data["steps"]) == 1
    assert data["steps"][0]["mcp_id"] == SAMPLE_MCP_ID_VALID
    # Check if it's in the in-memory registry (and thus saved to file by extension)
    assert data["workflow_id"] in workflow_registry


def test_create_workflow_invalid_mcp_id(
    client: TestClient, sample_workflow_payload: Dict[str, Any]
):
    payload_invalid_mcp = sample_workflow_payload.copy()
    payload_invalid_mcp["steps"][0]["mcp_id"] = SAMPLE_MCP_ID_INVALID
    response = client.post(
        "/workflows/", json=payload_invalid_mcp, headers=get_headers()
    )
    assert response.status_code == 400
    assert (
        f"mcp with id {SAMPLE_MCP_ID_INVALID} not found"
        in response.json()["detail"].lower()
    )


def test_create_workflow_bad_input_source_config(
    client: TestClient, sample_workflow_payload: Dict[str, Any]
):
    payload = sample_workflow_payload.copy()
    # Malform the input config, e.g., WORKFLOW_INPUT without workflow_input_key
    payload["steps"][0]["inputs"]["input_string"] = {
        "source_type": InputSourceType.WORKFLOW_INPUT.value,
        # Missing "workflow_input_key"
    }
    response = client.post("/workflows/", json=payload, headers=get_headers())
    assert response.status_code == 422  # Pydantic validation error
    # Check for detail indicating the validation error for workflow_input_key
    details = response.json().get("detail", [])
    assert any(
        "workflow_input_key' must be provided" in err.get("msg", "")
        for err in details
        if isinstance(err, dict)
    )


# === GET /workflows/ ===
def test_list_workflows_empty(client: TestClient):
    response = client.get("/workflows/", headers=get_headers())
    assert response.status_code == 200
    assert response.json() == []


def test_list_workflows_with_data(client: TestClient, create_sample_workflow: Workflow):
    # One workflow created by the fixture
    response = client.get("/workflows/", headers=get_headers())
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["workflow_id"] == create_sample_workflow.workflow_id


# === GET /workflows/{workflow_id} ===
def test_get_workflow_success(client: TestClient, create_sample_workflow: Workflow):
    workflow_id = create_sample_workflow.workflow_id
    response = client.get(f"/workflows/{workflow_id}", headers=get_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert data["name"] == create_sample_workflow.name


def test_get_workflow_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/workflows/{non_existent_id}", headers=get_headers())
    assert response.status_code == 404
    assert "workflow not found" in response.json()["detail"].lower()


# === PUT /workflows/{workflow_id} ===
def test_update_workflow_success(
    client: TestClient,
    create_sample_workflow: Workflow,
    sample_workflow_payload: Dict[str, Any],
):
    workflow_id = create_sample_workflow.workflow_id
    update_payload = sample_workflow_payload.copy()
    update_payload["name"] = "Updated Workflow Name"
    update_payload["description"] = "Updated description."
    # Ensure steps are part of the update payload for WorkflowCreate model if it's used directly
    # or adjust if a specific WorkflowUpdate schema is introduced without steps.
    # The current endpoint uses WorkflowCreate as input for PUT.

    original_updated_at = create_sample_workflow.updated_at

    response = client.put(
        f"/workflows/{workflow_id}", json=update_payload, headers=get_headers()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert data["name"] == "Updated Workflow Name"
    assert data["description"] == "Updated description."
    assert data["created_at"] == create_sample_workflow.created_at.isoformat().replace(
        "+00:00", "Z"
    )  # Ensure ISO format matches
    # Pydantic v2 datetime to json might not add Z, FastAPI might. Ensure comparison is robust.
    # For simplicity, we can parse both and compare datetime objects if precision issues arise.
    parsed_updated_at = datetime.fromisoformat(
        data["updated_at"].replace("Z", "+00:00")
    )
    assert parsed_updated_at > original_updated_at


def test_update_workflow_not_found(
    client: TestClient, sample_workflow_payload: Dict[str, Any]
):
    non_existent_id = str(uuid.uuid4())
    response = client.put(
        f"/workflows/{non_existent_id}",
        json=sample_workflow_payload,
        headers=get_headers(),
    )
    assert response.status_code == 404


def test_update_workflow_invalid_mcp_id(
    client: TestClient,
    create_sample_workflow: Workflow,
    sample_workflow_payload: Dict[str, Any],
):
    workflow_id = create_sample_workflow.workflow_id
    update_payload = sample_workflow_payload.copy()
    update_payload["name"] = "Attempt Update Invalid MCP"
    update_payload["steps"][0]["mcp_id"] = SAMPLE_MCP_ID_INVALID

    response = client.put(
        f"/workflows/{workflow_id}", json=update_payload, headers=get_headers()
    )
    assert response.status_code == 400
    assert (
        f"mcp with id {SAMPLE_MCP_ID_INVALID} not found"
        in response.json()["detail"].lower()
    )


# === DELETE /workflows/{workflow_id} ===
def test_delete_workflow_success(client: TestClient, create_sample_workflow: Workflow):
    workflow_id = create_sample_workflow.workflow_id
    response = client.delete(f"/workflows/{workflow_id}", headers=get_headers())
    assert response.status_code == 204
    # Verify it's gone
    assert workflow_id not in workflow_registry
    get_response = client.get(f"/workflows/{workflow_id}", headers=get_headers())
    assert get_response.status_code == 404


def test_delete_workflow_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    response = client.delete(f"/workflows/{non_existent_id}", headers=get_headers())
    assert response.status_code == 404
