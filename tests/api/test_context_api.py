import pytest
from fastapi.testclient import TestClient
import os
import uuid
from typing import Dict, Any, List

# Set a consistent API key for testing environment (used to get JWT)
TEST_API_KEY = str(uuid.uuid4())
os.environ["MCP_API_KEY"] = TEST_API_KEY

from mcp.api.main import app # app from your FastAPI application
from mcp.core.registry import mcp_server_registry, MCP_REGISTRY_FILE, WORKFLOW_STORAGE_FILE # For cleanup and direct manipulation
from mcp.core.types import MCPType
from mcp.schemas.mcp import MCPDetail

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
def clear_mcp_registry_and_file():
    """Clears the in-memory MCP registry and storage file before each test."""
    mcp_server_registry.clear()
    if MCP_REGISTRY_FILE.exists():
        MCP_REGISTRY_FILE.unlink()
    # Note: To ensure mcp_server_registry is reloaded by the app for each test if it loads from file at startup,
    # more complex test setup might be needed, or ensure app is re-initialized. 
    # For now, direct manipulation of the global mcp_server_registry and its file is assumed sufficient for these tests.

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

# --- Helper to create an MCP via API for testing GET endpoints ---
@pytest.fixture
def created_mcp_id(client: TestClient, jwt_headers: Dict[str, str]) -> str:
    mcp_payload = {
        "name": "Test Python Script MCP for Context API",
        "type": MCPType.PYTHON_SCRIPT.value,
        "description": "A Python script MCP for context API tests",
        "config": {
            "script_content": "print('Hello from test MCP for context API')",
            "requirements": []
        }
    }
    # MCP creation is now JWT protected
    response = client.post("/context", json=mcp_payload, headers=jwt_headers) 
    assert response.status_code == 201, f"Failed to create MCP for testing: {response.text}"
    return response.json()["id"] # Return the ID of the created MCP

# === GET /context/{server_id} Tests ===

def test_get_mcp_details_success(client: TestClient, created_mcp_id: str, jwt_headers: Dict[str, str]):
    server_id = created_mcp_id
    response = client.get(f"/context/{server_id}", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == server_id
    assert data["name"] == "Test Python Script MCP for Context API"
    assert data["type"] == MCPType.PYTHON_SCRIPT.value
    assert data["description"] == "A Python script MCP for context API tests"
    assert "script_content" in data["config"]
    # Validate against MCPDetail schema implicitly by response_model or explicitly if needed
    MCPDetail(**data) # This will raise ValidationError if an issue

def test_get_mcp_details_not_found(client: TestClient, jwt_headers: Dict[str, str]):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/context/{non_existent_id}", headers=jwt_headers)
    assert response.status_code == 404
    assert "mcp server not found" in response.json()["detail"].lower()

def test_get_mcp_details_no_jwt(client: TestClient, created_mcp_id: str):
    server_id = created_mcp_id
    response = client.get(f"/context/{server_id}") # No Authorization header
    assert response.status_code == 401 # Changed from 403, as OAuth2PasswordBearer typically returns 401
    assert "not authenticated" in response.json().get("detail", "").lower() # FastAPI's default for missing OAuth2 token

def test_get_mcp_details_invalid_jwt(client: TestClient, created_mcp_id: str):
    server_id = created_mcp_id
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get(f"/context/{server_id}", headers=invalid_headers)
    assert response.status_code == 401 # Changed from 403
    assert "could not validate credentials" in response.json().get("detail", "").lower()

# === GET /context (List All) Tests ===

def test_get_all_mcp_servers_empty(client: TestClient, jwt_headers: Dict[str, str]):
    response = client.get("/context", headers=jwt_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_all_mcp_servers_with_data(client: TestClient, created_mcp_id: str, jwt_headers: Dict[str, str]):
    # `created_mcp_id` fixture already creates one MCP
    response = client.get("/context", headers=jwt_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == created_mcp_id
    assert data[0]["name"] == "Test Python Script MCP for Context API"
    MCPDetail(**data[0]) # Validate schema for items in list

def test_get_all_mcp_servers_no_jwt(client: TestClient):
    response = client.get("/context") # No Authorization header
    assert response.status_code == 401 # Changed from 403

def test_get_all_mcp_servers_invalid_jwt(client: TestClient):
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/context", headers=invalid_headers)
    assert response.status_code == 401 # Changed from 403

# === POST /context Tests (Example - assuming it's also JWT protected) ===
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

# Similar updates would be needed for DELETE tests if they exist

# You can add more tests for POST, DELETE /context if they are not covered elsewhere,
# but for this task, GET /context/{id} is the primary focus. 