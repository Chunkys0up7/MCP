import pytest
from fastapi.testclient import TestClient
import os
import uuid
from typing import Dict
from unittest.mock import patch # Added for mocking
from datetime import datetime

# Import the test_app_client and test_db_session from conftest

# Set a consistent API key for testing environment (used to get JWT)
TEST_API_KEY = str(uuid.uuid4())
os.environ["MCP_API_KEY"] = TEST_API_KEY

from mcp.api.main import app # app from your FastAPI application
# from mcp.core.registry import mcp_server_registry, MCP_REGISTRY_FILE, WORKFLOW_STORAGE_FILE # REMOVE: Old file-based
from mcp.core.types import MCPType
from mcp.schemas.mcp import MCPDetail, MCPListItem # Added MCPListItem, MCPRead
from mcp.db.models import MCP as MCPModel, MCPVersion as MCPVersionModel, EMBEDDING_DIM # DB Models and EMBEDDING_DIM
from mcp.db.session import Session # For type hinting db session
from mcp.schemas.mcp import MCPCreate as MCPCreateSchema # For creating MCPs


# Use the test_app_client from conftest.py, which handles DB override
@pytest.fixture(scope="function") # Changed scope to function to align with test_db_session
def client(test_app_client: TestClient): # Inject test_app_client
    yield test_app_client

@pytest.fixture(autouse=True)
def clear_db_records(test_db_session: Session): # Uses the SQLite session from conftest
    # This fixture will run for every test. test_db_session from conftest
    # already handles table creation/dropping per function.
    # No explicit cleanup here is needed if test_db_session correctly isolates.
    pass

@pytest.fixture(scope="module") # JWT token can be module-scoped if API key is module-scoped
def api_key_headers() -> Dict[str, str]:
    """Headers for endpoints still protected by X-API-Key (e.g., /auth/issue-dev-token)."""
    return {"X-API-Key": TEST_API_KEY}

@pytest.fixture(scope="module")
def jwt_headers(client: TestClient, api_key_headers: Dict[str, str]) -> Dict[str, str]:
    """Gets a JWT and returns headers for JWT-protected endpoints."""
    # Need a client that persists for the module scope for this fixture.
    # This is tricky if the main 'client' fixture is function-scoped.
    # For now, let's try to get a one-off client for token generation.
    # This assumes the app's dependency_overrides are not critical for /auth/issue-dev-token
    # If /auth/issue-dev-token required the DB, this would need a rethink or make jwt_headers function-scoped.
    
    # Create a temporary client instance for fetching the JWT token.
    # This is a common pattern if the TestClient used for tests is function-scoped due to DB setup/teardown,
    # but the JWT itself can be longer-lived (module or session).
    # However, the 'client' parameter for jwt_headers is typically the test client.
    # Let's make jwt_headers function-scoped for now to ensure it uses the correct client.
    
    # Re-evaluating: The client fixture from conftest is function-scoped.
    # If jwt_headers is module-scoped, it will get a TestClient instance but the DB setup
    # (via override_get_db triggered by test_app_client) might not be active or might be stale.
    # Safest is to make jwt_headers function-scoped as well.
    pass # Will redefine this as function-scoped later if needed, or adjust client for module.
    # For now, will copy from test_workflow_api.py which has module-scoped jwt_headers
    # by creating a one-off client just for token issuance.
    
    # Reverting to a simpler approach: make jwt_headers also function scoped if client is function scoped.
    # For now, keeping it module-scoped as in test_workflow_api.py and assuming the /auth endpoint
    # doesn't need the overridden DB for this specific call.
    
    # Let's get a fresh client for token generation that doesn't rely on function-scoped DB overrides.
    # This assumes /auth/issue-dev-token is independent of the main DB state for tests.
    with TestClient(app) as token_client:
        response = token_client.post("/auth/issue-dev-token", headers=api_key_headers)
    assert response.status_code == 200, f"Failed to get JWT: {response.text}"
    token_data = response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

# --- Helper to create an MCP via API for testing GET/PUT/DELETE endpoints ---
@pytest.fixture
def created_db_mcp(client: TestClient, jwt_headers: Dict[str, str], test_db_session: Session) -> MCPModel:
    mcp_payload = MCPCreateSchema(
        name="Test Python Script MCP for DB Context API",
        type=MCPType.PYTHON_SCRIPT,
        description="A Python script MCP for DB context API tests",
        tags=["db_test", "python_script"],
        initial_version_str="0.1.0",
        initial_version_description="First version for DB test",
        initial_config={
            "script_content": "print('Hello from DB test MCP for context API')",
            "requirements": ["pandas"]
        }
    )
    response = client.post("/context", json=mcp_payload.model_dump(mode='json'), headers=jwt_headers)
    assert response.status_code == 201, f"Failed to create MCP for testing: {response.text}"
    mcp_data = response.json()
    
    # Fetch the created MCP from DB to return as an ORM object for easier access in tests
    db_mcp = test_db_session.query(MCPModel).filter(MCPModel.id == uuid.UUID(mcp_data["id"])).first()
    assert db_mcp is not None
    return db_mcp

# === GET /context/{mcp_id} Tests ===

def test_get_mcp_details_success(client: TestClient, created_db_mcp: MCPModel, jwt_headers: Dict[str, str]):
    mcp_id = created_db_mcp.id
    response = client.get(f"/context/{mcp_id}", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(mcp_id)
    assert data["name"] == "Test Python Script MCP for DB Context API"
    assert data["type"] == MCPType.PYTHON_SCRIPT.value
    assert data["description"] == "A Python script MCP for DB context API tests"
    assert "script_content" in data["latest_version_config"]
    assert data["latest_version_str"] == "0.1.0"
    assert data["tags"] == ["db_test", "python_script"]
    MCPDetail(**data) # Validate against MCPDetail schema

def test_get_mcp_details_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/context/{non_existent_id}", headers=jwt_headers)
    assert response.status_code == 404
    assert "mcp definition not found" in response.json()["detail"].lower()

def test_get_mcp_details_no_jwt(client: TestClient, created_db_mcp: MCPModel):
    mcp_id = created_db_mcp.id
    response = client.get(f"/context/{mcp_id}") # No Authorization header
    assert response.status_code == 401 # Changed from 403, as OAuth2PasswordBearer typically returns 401
    assert "not authenticated" in response.json().get("detail", "").lower() # FastAPI's default for missing OAuth2 token

def test_get_mcp_details_invalid_jwt(client: TestClient, created_db_mcp: MCPModel):
    mcp_id = created_db_mcp.id
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get(f"/context/{mcp_id}", headers=invalid_headers)
    assert response.status_code == 401 # Changed from 403
    assert "could not validate credentials" in response.json().get("detail", "").lower()

# === GET /context (List All) Tests ===

def test_get_all_mcp_servers_empty(client: TestClient, jwt_headers: Dict[str, str]):
    response = client.get("/context", headers=jwt_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_all_mcp_servers_with_data(client: TestClient, created_db_mcp: MCPModel, jwt_headers: Dict[str, str]):
    # `created_db_mcp` fixture already creates one MCP
    response = client.get("/context", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(created_db_mcp.id)
    assert data[0]["name"] == "Test Python Script MCP for DB Context API"
    assert data[0]["type"] == MCPType.PYTHON_SCRIPT.value
    assert data[0]["description"] == "A Python script MCP for DB context API tests"
    assert data[0]["tags"] == ["db_test", "python_script"]
    assert data[0]["latest_version_str"] == "0.1.0"
    MCPListItem(**data[0]) # Validate schema for items in list (MCPListItem)

def test_get_all_mcp_servers_no_jwt(client: TestClient):
    response = client.get("/context") # No Authorization header
    assert response.status_code == 401 # Changed from 403

def test_get_all_mcp_servers_invalid_jwt(client: TestClient):
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/context", headers=invalid_headers)
    assert response.status_code == 401 # Changed from 403

# === POST /context Tests ===
def test_create_mcp_success(client: TestClient, jwt_headers: Dict[str, str], test_db_session: Session):
    mcp_payload = {
        "name": "New Python MCP via POST",
        "type": MCPType.PYTHON_SCRIPT.value,
        "description": "A brand new Python script MCP created via POST.",
        "tags": ["post_test", "python"],
        "initial_version_str": "1.0.0",
        "initial_version_description": "First version from POST.",
        "initial_config": {
            "script_content": "print('Hello from POST test MCP')",
            "requirements": ["numpy"]
        }
    }
    response = client.post("/context", json=mcp_payload, headers=jwt_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == mcp_payload["name"]
    assert data["type"] == mcp_payload["type"]
    assert data["description"] == mcp_payload["description"]
    assert data["tags"] == mcp_payload["tags"]
    # MCPRead schema doesn't directly return version details, it returns the MCP parent object details
    # To verify version creation, we would typically check the DB or the GET {mcp_id} endpoint

    # Verify in DB
    db_mcp = test_db_session.query(MCPModel).filter(MCPModel.id == uuid.UUID(data["id"])).first()
    assert db_mcp is not None
    assert db_mcp.name == mcp_payload["name"]
    assert len(db_mcp.versions) == 1
    assert db_mcp.versions[0].version_str == "1.0.0"
    assert db_mcp.versions[0].config_snapshot["script_content"] == "print('Hello from POST test MCP')"
    assert db_mcp.embedding is not None # Check embedding is populated
    assert len(db_mcp.embedding) == EMBEDDING_DIM # Check embedding dimension

def test_create_mcp_missing_required_fields(client: TestClient, jwt_headers: Dict[str, str]):
    # Missing 'name'
    mcp_payload_no_name = {
        # "name": "Missing Name MCP",
        "type": MCPType.PYTHON_SCRIPT.value,
        "initial_version_str": "1.0.0",
        "initial_config": {"script_content": "print('test')"}
    }
    response = client.post("/context", json=mcp_payload_no_name, headers=jwt_headers)
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error
    assert "name" in response.json()["detail"][0]["loc"]

    # Missing 'type'
    mcp_payload_no_type = {
        "name": "Missing Type MCP",
        # "type": MCPType.PYTHON_SCRIPT.value,
        "initial_version_str": "1.0.0",
        "initial_config": {"script_content": "print('test')"}
    }
    response = client.post("/context", json=mcp_payload_no_type, headers=jwt_headers)
    assert response.status_code == 422
    assert "type" in response.json()["detail"][0]["loc"]

    # Missing 'initial_version_str'
    mcp_payload_no_version = {
        "name": "Missing Version MCP",
        "type": MCPType.PYTHON_SCRIPT.value,
        # "initial_version_str": "1.0.0",
        "initial_config": {"script_content": "print('test')"}
    }
    response = client.post("/context", json=mcp_payload_no_version, headers=jwt_headers)
    assert response.status_code == 422
    assert "initial_version_str" in response.json()["detail"][0]["loc"]

    # Missing 'initial_config'
    mcp_payload_no_config = {
        "name": "Missing Config MCP",
        "type": MCPType.PYTHON_SCRIPT.value,
        "initial_version_str": "1.0.0",
        # "initial_config": {"script_content": "print('test')"}
    }
    response = client.post("/context", json=mcp_payload_no_config, headers=jwt_headers)
    assert response.status_code == 422
    assert "initial_config" in response.json()["detail"][0]["loc"]

def test_create_mcp_invalid_type(client: TestClient, jwt_headers: Dict[str, str]):
    mcp_payload = {
        "name": "Invalid Type MCP",
        "type": "INVALID_MCP_TYPE",
        "initial_version_str": "1.0.0",
        "initial_config": {"script_content": "print('test')"}
    }
    response = client.post("/context", json=mcp_payload, headers=jwt_headers)
    assert response.status_code == 422 # Validation error for enum
    assert "type" in response.json()["detail"][0]["loc"]

def test_create_mcp_invalid_initial_config_python_script(client: TestClient, jwt_headers: Dict[str, str]):
    # Test case 1: Missing required 'script_content' or 'script_path' for PythonScriptConfig
    mcp_payload_missing_script = {
        "name": "Python MCP Missing Script",
        "type": MCPType.PYTHON_SCRIPT.value,
        "initial_version_str": "1.0.0",
        "initial_config": {"requirements": []} # Missing script_content/script_path
    }
    response = client.post("/context", json=mcp_payload_missing_script, headers=jwt_headers)
    assert response.status_code == 400 # From ValueError in registry service
    assert "invalid initial_config" in response.json()["detail"].lower()
    assert "either 'script_path' or 'script_content' must be provided" in response.json()["detail"].lower()

    # Test case 2: Extra field in initial_config for PythonScriptConfig (extra='forbid' is active)
    mcp_payload_extra_field = {
        "name": "Python MCP Extra Field",
        "type": MCPType.PYTHON_SCRIPT.value,
        "initial_version_str": "1.0.0",
        "initial_config": {
            "script_content": "print('hello')",
            "unknown_field": "some_value" # This field is not in PythonScriptConfig
        }
    }
    response = client.post("/context", json=mcp_payload_extra_field, headers=jwt_headers)
    assert response.status_code == 400
    assert "invalid initial_config" in response.json()["detail"].lower()
    # Pydantic v2 error message for extra fields is like "Extra inputs are not permitted"
    assert "extra inputs are not permitted" in response.json()["detail"].lower() 
    assert "unknown_field" in response.json()["detail"].lower() # Check that the field name is mentioned

    # Test case 3: Incorrect type for a field in PythonScriptConfig
    mcp_payload_wrong_type = {
        "name": "Python MCP Wrong Type",
        "type": MCPType.PYTHON_SCRIPT.value,
        "initial_version_str": "1.0.0",
        "initial_config": {
            "script_content": "print('hello')",
            "timeout": "not-an-integer" # Timeout should be an int
        }
    }
    response = client.post("/context", json=mcp_payload_wrong_type, headers=jwt_headers)
    assert response.status_code == 400
    assert "invalid initial_config" in response.json()["detail"].lower()
    # Pydantic v2 error message for type error is like "Input should be a valid integer"
    assert "input should be a valid integer" in response.json()["detail"].lower()
    assert "timeout" in response.json()["detail"].lower()

def test_create_mcp_valid_initial_config_llm_prompt(client: TestClient, jwt_headers: Dict[str, str], test_db_session: Session):
    mcp_payload = {
        "name": "Valid LLM Prompt MCP",
        "type": MCPType.LLM_PROMPT.value,
        "description": "A valid LLM prompt.",
        "initial_version_str": "0.1.0",
        "initial_config": {
            "name": "LLM Config Name", # BaseMCPConfig field
            "type": MCPType.LLM_PROMPT.value, # BaseMCPConfig field, must match outer type
            "template": "Hello {{name}}",
            "model_name": "test-model",
            "input_variables": ["name"]
            # Not including temperature, max_tokens, system_prompt to use defaults
        }
    }
    response = client.post("/context", json=mcp_payload, headers=jwt_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == mcp_payload["name"]

    # Verify config stored in DB was processed by LLMPromptConfig (e.g. defaults applied)
    db_mcp = test_db_session.query(MCPModel).filter(MCPModel.id == uuid.UUID(data["id"])).first()
    assert db_mcp is not None
    assert len(db_mcp.versions) == 1
    stored_config = db_mcp.versions[0].config_snapshot
    assert stored_config["template"] == "Hello {{name}}"
    assert stored_config["model_name"] == "test-model"
    assert stored_config["temperature"] == 0.7 # Default value from LLMPromptConfig

def test_create_mcp_invalid_initial_config_llm_prompt(client: TestClient, jwt_headers: Dict[str, str]):
    # Missing required 'template' for LLMPromptConfig
    mcp_payload_missing_template = {
        "name": "LLM MCP Missing Template",
        "type": MCPType.LLM_PROMPT.value,
        "initial_version_str": "1.0.0",
        "initial_config": {
            "name": "LLM Config Name",
            "type": MCPType.LLM_PROMPT.value,
            "model_name": "test-model"
            # Missing 'template'
        }
    }
    response = client.post("/context", json=mcp_payload_missing_template, headers=jwt_headers)
    assert response.status_code == 400
    assert "invalid initial_config" in response.json()["detail"].lower()
    assert "template" in response.json()["detail"].lower() # Field required
    assert "field required" in response.json()["detail"].lower() 

def test_create_mcp_no_jwt(client: TestClient):
    mcp_payload = {
        "name": "Test MCP No JWT",
        "type": MCPType.PYTHON_SCRIPT.value,
        "config": {"script_content": "print('test')"}
    }
    response = client.post("/context", json=mcp_payload) # No Authorization header
    assert response.status_code == 401

def test_create_mcp_invalid_jwt(client: TestClient):
    mcp_payload = {
        "name": "Test MCP Invalid JWT",
        "type": MCPType.PYTHON_SCRIPT.value,
        "config": {"script_content": "print('test')"}
    }
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.post("/context", json=mcp_payload, headers=invalid_headers)
    assert response.status_code == 401

# === PUT /context/{mcp_id} Tests ===
def test_update_mcp_success(client: TestClient, created_db_mcp: MCPModel, jwt_headers: Dict[str, str], test_db_session: Session):
    mcp_id = str(created_db_mcp.id)
    update_payload = {
        "name": "Updated MCP Name via PUT",
        "description": "This MCP has been updated.",
        "tags": ["updated", "put_test"]
    }
    response = client.put(f"/context/{mcp_id}", json=update_payload, headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mcp_id
    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]
    assert data["tags"] == update_payload["tags"]
    assert data["type"] == created_db_mcp.type # Type should not change on update

    # Verify in DB
    test_db_session.refresh(created_db_mcp)
    assert created_db_mcp.name == update_payload["name"]
    assert created_db_mcp.description == update_payload["description"]
    assert created_db_mcp.tags == update_payload["tags"]
    assert created_db_mcp.embedding is not None # Check embedding is populated after update
    assert len(created_db_mcp.embedding) == EMBEDDING_DIM # Check embedding dimension

def test_update_mcp_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    update_payload = {"name": "Attempt to update non-existent MCP"}
    response = client.put(f"/context/{non_existent_id}", json=update_payload, headers=jwt_headers)
    assert response.status_code == 404
    assert "mcp definition not found for update" in response.json()["detail"].lower()

def test_update_mcp_invalid_data(client: TestClient, created_db_mcp: MCPModel, jwt_headers: Dict[str, str]):
    mcp_id = str(created_db_mcp.id)
    # Attempt to send a field that is not in MCPUpdate schema, e.g., 'type'
    # Pydantic should strip this by default if not defined in the model, 
    # or raise error if extra='forbid'. Let's test with an invalid value for an existing field.
    # e.g. tags as a string instead of list
    invalid_payload = {
        "name": "Updated Name with Invalid Tags",
        "tags": "not-a-list"
    }
    response = client.put(f"/context/{mcp_id}", json=invalid_payload, headers=jwt_headers)
    assert response.status_code == 422 # Pydantic validation error
    error_details = response.json()["detail"]
    assert any(d["loc"] == ["body", "tags"] and "list_type" in d["type"] for d in error_details)

def test_update_mcp_no_jwt(client: TestClient, created_db_mcp: MCPModel):
    mcp_id = str(created_db_mcp.id)
    update_payload = {"name": "Update attempt no JWT"}
    response = client.put(f"/context/{mcp_id}", json=update_payload)
    assert response.status_code == 401

def test_update_mcp_invalid_jwt(client: TestClient, created_db_mcp: MCPModel):
    mcp_id = str(created_db_mcp.id)
    update_payload = {"name": "Update attempt invalid JWT"}
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.put(f"/context/{mcp_id}", json=update_payload, headers=invalid_headers)
    assert response.status_code == 401

# === DELETE /context/{mcp_id} Tests ===
def test_delete_mcp_success(client: TestClient, created_db_mcp: MCPModel, jwt_headers: Dict[str, str], test_db_session: Session):
    mcp_id = str(created_db_mcp.id)
    response = client.delete(f"/context/{mcp_id}", headers=jwt_headers)
    assert response.status_code == 204

    # Verify in DB (should be None)
    db_mcp = test_db_session.query(MCPModel).filter(MCPModel.id == uuid.UUID(mcp_id)).first()
    assert db_mcp is None

    # Verify associated versions are also deleted (due to cascade? or service logic?)
    # Assuming cascade delete is set up on the MCPVersionModel foreign key to MCPModel
    # If not, the service logic mcp_registry_service.delete_mcp_definition_from_db should handle it.
    # Let's check this explicitly by trying to get versions. If the MCP is gone, versions should be too or orphaned.
    # A robust test would ensure versions are also gone if cascade is expected.
    # For now, just checking the MCP itself is sufficient based on typical delete patterns.
    
    # Try to GET it, should be 404
    get_response = client.get(f"/context/{mcp_id}", headers=jwt_headers)
    assert get_response.status_code == 404

def test_delete_mcp_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    response = client.delete(f"/context/{non_existent_id}", headers=jwt_headers)
    assert response.status_code == 404
    assert "mcp definition not found for deletion" in response.json()["detail"].lower()

def test_delete_mcp_no_jwt(client: TestClient, created_db_mcp: MCPModel):
    mcp_id = str(created_db_mcp.id)
    response = client.delete(f"/context/{mcp_id}")
    assert response.status_code == 401

def test_delete_mcp_invalid_jwt(client: TestClient, created_db_mcp: MCPModel):
    mcp_id = str(created_db_mcp.id)
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.delete(f"/context/{mcp_id}", headers=invalid_headers)
    assert response.status_code == 401


# === GET /context/search Tests ===
@patch('mcp.api.main.mcp_registry_service.search_mcp_definitions_by_text')
def test_search_mcp_definitions_success(
    mock_search_service,
    client: TestClient, 
    jwt_headers: Dict[str, str], 
    test_db_session: Session # Used to create mock MCPModel instances
):
    # Create a couple of mock MCPModel instances that the service might return
    # These need to have 'versions' relationship populated for the API endpoint to work
    mock_mcp1_id = uuid.uuid4()
    mock_mcp1 = MCPModel(
        id=mock_mcp1_id,
        name="Found MCP 1", 
        type=MCPType.PYTHON_SCRIPT.value, 
        description="First found item by search",
        tags=["search_result", "item1"],
        updated_at=datetime.utcnow()
    )
    mock_mcp1_version = MCPVersionModel(id=uuid.uuid4(), mcp_id=mock_mcp1_id, version_str="1.0", config_snapshot={})
    mock_mcp1.versions = [mock_mcp1_version] # Simulate relationship

    mock_mcp2_id = uuid.uuid4()
    mock_mcp2 = MCPModel(
        id=mock_mcp2_id,
        name="Found MCP 2",
        type=MCPType.LLM_PROMPT.value,
        description="Second found item",
        tags=["search_result", "item2"],
        updated_at=datetime.utcnow()
    )
    mock_mcp2_version = MCPVersionModel(id=uuid.uuid4(), mcp_id=mock_mcp2_id, version_str="0.5", config_snapshot={})
    mock_mcp2.versions = [mock_mcp2_version]

    mock_search_service.return_value = [mock_mcp1, mock_mcp2]

    query_text = "find my mcp"
    response = client.get(f"/context/search?query={query_text}&limit=5", headers=jwt_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    mock_search_service.assert_called_once_with(db=test_db_session, query_text=query_text, limit=5)

    # Check if the data matches MCPListItem structure and content
    assert data[0]["name"] == "Found MCP 1"
    assert data[0]["type"] == MCPType.PYTHON_SCRIPT.value
    assert data[0]["latest_version_str"] == "1.0"
    MCPListItem(**data[0]) # Validate schema

    assert data[1]["name"] == "Found MCP 2"
    assert data[1]["type"] == MCPType.LLM_PROMPT.value
    assert data[1]["latest_version_str"] == "0.5"
    MCPListItem(**data[1])

@patch('mcp.api.main.mcp_registry_service.search_mcp_definitions_by_text')
def test_search_mcp_definitions_empty_result(
    mock_search_service,
    client: TestClient, 
    jwt_headers: Dict[str, str],
    test_db_session: Session
):
    mock_search_service.return_value = []
    query_text = "nothing found here"
    response = client.get(f"/context/search?query={query_text}", headers=jwt_headers)

    assert response.status_code == 200
    assert response.json() == []
    mock_search_service.assert_called_once_with(db=test_db_session, query_text=query_text, limit=10) # Default limit

def test_search_mcp_definitions_empty_query(client: TestClient, jwt_headers: Dict[str, str]):
    response = client.get("/context/search?query=", headers=jwt_headers)
    assert response.status_code == 400
    assert "search query cannot be empty" in response.json()["detail"].lower()

    response = client.get("/context/search?query=   ", headers=jwt_headers) # Query with only spaces
    assert response.status_code == 400
    assert "search query cannot be empty" in response.json()["detail"].lower()

def test_search_mcp_definitions_no_jwt(client: TestClient):
    response = client.get("/context/search?query=anything")
    assert response.status_code == 401

def test_search_mcp_definitions_invalid_jwt(client: TestClient):
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/context/search?query=anything", headers=invalid_headers)
    assert response.status_code == 401

# You can add more tests for POST, DELETE /context if they are not covered elsewhere,
# but for this task, GET /context/{id} is the primary focus. 