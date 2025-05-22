import pytest
from fastapi.testclient import TestClient
import os
import uuid
from typing import Dict, Any, List

# Set a consistent API key for testing environment
TEST_API_KEY = str(uuid.uuid4()) # Ensure this is the same key used by get_api_key in dependencies
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

def get_headers() -> Dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}

# --- Helper to create an MCP via API for testing GET endpoints ---
@pytest.fixture
def created_mcp_id(client: TestClient) -> str:
    mcp_payload = {
        "name": "Test Python Script MCP",
        "type": MCPType.PYTHON_SCRIPT.value,
        "description": "A Python script MCP for testing GET /context/{id}",
        "config": {
            "script_content": "print('Hello from test MCP')",
            "requirements": []
        }
    }
    response = client.post("/context", json=mcp_payload, headers=get_headers())
    assert response.status_code == 201
    return response.json()["id"] # Return the ID of the created MCP

# === GET /context/{server_id} Tests ===

def test_get_mcp_details_success(client: TestClient, created_mcp_id: str):
    server_id = created_mcp_id
    response = client.get(f"/context/{server_id}", headers=get_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == server_id
    assert data["name"] == "Test Python Script MCP"
    assert data["type"] == MCPType.PYTHON_SCRIPT.value
    assert data["description"] == "A Python script MCP for testing GET /context/{id}"
    assert "script_content" in data["config"]
    # Validate against MCPDetail schema implicitly by response_model or explicitly if needed
    MCPDetail(**data) # This will raise ValidationError if an issue

def test_get_mcp_details_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/context/{non_existent_id}", headers=get_headers())
    assert response.status_code == 404
    assert "mcp server not found" in response.json()["detail"].lower()

def test_get_mcp_details_no_api_key(client: TestClient, created_mcp_id: str):
    server_id = created_mcp_id
    response = client.get(f"/context/{server_id}")
    assert response.status_code == 403 # Expecting 403 due to auto_error=True
    assert "not authenticated" in response.json().get("detail", "").lower() or \
           "api key" in response.json().get("detail", "").lower()

def test_get_mcp_details_invalid_api_key(client: TestClient, created_mcp_id: str):
    server_id = created_mcp_id
    response = client.get(f"/context/{server_id}", headers={"X-API-Key": "invalidkey"})
    assert response.status_code == 403
    assert "invalid api key" in response.json().get("detail", "").lower()

# === GET /context (List All) Tests ===

def test_get_all_mcp_servers_empty(client: TestClient):
    response = client.get("/context", headers=get_headers())
    assert response.status_code == 200
    assert response.json() == []

def test_get_all_mcp_servers_with_data(client: TestClient, created_mcp_id: str):
    # `created_mcp_id` fixture already creates one MCP
    response = client.get("/context", headers=get_headers())
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == created_mcp_id
    assert data[0]["name"] == "Test Python Script MCP"
    MCPDetail(**data[0]) # Validate schema for items in list

def test_get_all_mcp_servers_no_api_key(client: TestClient):
    response = client.get("/context")
    assert response.status_code == 403

def test_get_all_mcp_servers_invalid_api_key(client: TestClient):
    response = client.get("/context", headers={"X-API-Key": "invalidkey"})
    assert response.status_code == 403

# You can add more tests for POST, DELETE /context if they are not covered elsewhere,
# but for this task, GET /context/{id} is the primary focus. 