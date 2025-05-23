from fastapi.testclient import TestClient
from mcp.api.main import app

client = TestClient(app)

def test_create_and_execute_python_script():
    # Create a new Python script MCP
    mcp_config = {
        "name": "Test Script",
        "type": "python_script",
        "config": {
            "script_path": "mcp/scripts/hello_world.py",
            "requirements": [],
            "input_variables": ["name", "language"],
            "virtual_env": False,
            "timeout": 60
        }
    }
    create_resp = client.post("/context", json=mcp_config)
    assert create_resp.status_code == 200
    mcp = create_resp.json()
    server_id = mcp["id"]

    # Execute the MCP
    exec_resp = client.post(f"/context/{server_id}/execute", json={"name": "Alice", "language": "en"})
    assert exec_resp.status_code == 200
    data = exec_resp.json()
    assert data["success"] is True
    assert "result" in data

    # Delete the MCP
    del_resp = client.delete(f"/context/{server_id}", headers={"X-API-Key": "your-api-key-here"})
    assert del_resp.status_code == 200


def test_execute_nonexistent_mcp():
    resp = client.post("/context/nonexistent-id/execute", json={})
    assert resp.status_code == 404


def test_create_invalid_type():
    mcp_config = {
        "name": "Invalid MCP",
        "type": "unknown_type",
        "config": {}
    }
    resp = client.post("/context", json=mcp_config)
    assert resp.status_code == 400 