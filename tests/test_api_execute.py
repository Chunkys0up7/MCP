import requests
import pytest
import os
from mcp.core.types import MCPType, LLMPromptConfig

API_BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("MCP_API_KEY", "test_api_key")  # Use environment variable or default for testing
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_llm_prompt_execution():
    """Test LLM prompt MCP execution flow."""
    # Create test MCP server
    config = {
        "name": "Test LLM Prompt",
        "description": "Test LLM prompt MCP",
        "type": "llm_prompt",
        "config": {
            "type": "llm_prompt",
            "name": "Test LLM Prompt",
            "template": "Tell me a joke about {topic}",
            "input_variables": ["topic"],
            "model_name": "claude-3-sonnet-20240229",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    # Create server
    create_resp = requests.post(f"{API_BASE_URL}/context", json=config, headers=HEADERS)
    assert create_resp.status_code == 200, f"Failed to create MCP: {create_resp.text}"
    server_data = create_resp.json()
    server_id = server_data["id"]
    
    try:
        # Execute server
        inputs = {"topic": "programming"}
        execute_resp = requests.post(f"{API_BASE_URL}/context/{server_id}/execute", json=inputs, headers=HEADERS)
        assert execute_resp.status_code == 200, f"Failed to execute MCP: {execute_resp.text}"
        result = execute_resp.json()
        
        # Verify result structure
        assert "result" in result, "Missing 'result' in response"
        assert "success" in result, "Missing 'success' in response"
        assert "context" in result, "Missing 'context' in response"
        assert result["success"], f"Execution failed: {result.get('error')}"
        
    finally:
        # Clean up
        delete_resp = requests.delete(f"{API_BASE_URL}/context/{server_id}", headers=HEADERS)
        assert delete_resp.status_code == 200, f"Failed to delete MCP: {delete_resp.text}"

def test_python_script_execution():
    """Test Python script MCP execution flow."""
    # Create test MCP server
    config = {
        "name": "Test Python Script",
        "description": "Test Python script MCP",
        "type": "python_script",
        "config": {
            "type": "python_script",
            "name": "Test Python Script",
            "script_path": "mcp/scripts/hello_world.py",
            "requirements": ["requests==2.31.0"],
            "input_variables": ["name", "language"],
            "virtual_env": True,
            "timeout": 600
        }
    }
    
    # Create server
    create_resp = requests.post(f"{API_BASE_URL}/context", json=config, headers=HEADERS)
    assert create_resp.status_code == 200, f"Failed to create MCP: {create_resp.text}"
    server_data = create_resp.json()
    server_id = server_data["id"]
    
    try:
        # Execute server
        inputs = {"name": "Test User", "language": "Python"}
        execute_resp = requests.post(f"{API_BASE_URL}/context/{server_id}/execute", json=inputs, headers=HEADERS)
        assert execute_resp.status_code == 200, f"Failed to execute MCP: {execute_resp.text}"
        result = execute_resp.json()
        
        # Verify result structure
        assert "result" in result, "Missing 'result' in response"
        assert "success" in result, "Missing 'success' in response"
        assert "context" in result, "Missing 'context' in response"
        assert result["success"], f"Execution failed: {result.get('error')}"
        
    finally:
        # Clean up
        delete_resp = requests.delete(f"{API_BASE_URL}/context/{server_id}", headers=HEADERS)
        assert delete_resp.status_code == 200, f"Failed to delete MCP: {delete_resp.text}"

def test_jupyter_notebook_execution():
    """Test Jupyter notebook MCP execution flow."""
    # Create test MCP server
    config = {
        "name": "Test Notebook",
        "description": "Test Jupyter notebook MCP",
        "type": "jupyter_notebook",
        "config": {
            "type": "jupyter_notebook",
            "name": "Test Notebook",
            "notebook_path": "mcp/notebooks/example.ipynb",
            "execute_all": True,
            "timeout": 600
        }
    }
    
    # Create server
    create_resp = requests.post(f"{API_BASE_URL}/context", json=config, headers=HEADERS)
    assert create_resp.status_code == 200, f"Failed to create MCP: {create_resp.text}"
    server_data = create_resp.json()
    server_id = server_data["id"]
    
    try:
        # Execute server
        inputs = {}  # No inputs required for this example notebook
        execute_resp = requests.post(f"{API_BASE_URL}/context/{server_id}/execute", json=inputs, headers=HEADERS)
        assert execute_resp.status_code == 200, f"Failed to execute MCP: {execute_resp.text}"
        result = execute_resp.json()
        
        # Verify result structure
        assert "result" in result, "Missing 'result' in response"
        assert "success" in result, "Missing 'success' in response"
        assert "context" in result, "Missing 'context' in response"
        assert result["success"], f"Execution failed: {result.get('error')}"
        
    finally:
        # Clean up
        delete_resp = requests.delete(f"{API_BASE_URL}/context/{server_id}", headers=HEADERS)
        assert delete_resp.status_code == 200, f"Failed to delete MCP: {delete_resp.text}" 