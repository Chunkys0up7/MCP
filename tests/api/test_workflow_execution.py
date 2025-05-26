from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from mcp.core.types import MCPType
from mcp.db.models import MCP


@pytest.fixture
def multi_step_workflow(
    test_app_client: TestClient, jwt_headers: Dict[str, str], test_db_session: Session
):
    """Creates a workflow with multiple steps for testing complex execution scenarios."""
    # Create test MCPs first
    mcp1 = MCP(
        name="Test MCP 1",
        type=MCPType.PYTHON_SCRIPT,
        description="Test MCP for workflow execution",
        tags=["test"],
    )
    mcp2 = MCP(
        name="Test MCP 2",
        type=MCPType.PYTHON_SCRIPT,
        description="Test MCP for workflow execution",
        tags=["test"],
    )
    test_db_session.add_all([mcp1, mcp2])
    test_db_session.commit()

    # Create workflow with multiple steps
    workflow_data = {
        "name": "Multi-Step Test Workflow",
        "description": "A workflow with multiple steps for testing execution scenarios",
        "steps": [
            {
                "name": "Step 1: Process Input",
                "mcp_id": str(mcp1.id),
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "workflow_input",
                        "workflow_input_key": "initial_data",
                    }
                },
            },
            {
                "name": "Step 2: Transform Data",
                "mcp_id": str(mcp2.id),
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "step_output",
                        "source_step_id": "step-1",
                        "source_output_name": "processed_data",
                    }
                },
            },
        ],
    }

    response = test_app_client.post(
        "/workflows/", json=workflow_data, headers=jwt_headers
    )
    assert response.status_code == 201
    return response.json()


def test_execute_workflow_with_empty_inputs(
    test_app_client: TestClient,
    multi_step_workflow: Dict,
    jwt_headers: Dict[str, str],
    test_db_session: Session,
):
    """Test workflow execution with empty inputs."""
    workflow_id = multi_step_workflow["workflow_id"]
    response = test_app_client.post(
        f"/workflows/{workflow_id}/execute", json={}, headers=jwt_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert "Missing required input" in data["error_message"]


def test_execute_workflow_with_invalid_step_reference(
    test_app_client: TestClient,
    multi_step_workflow: Dict,
    jwt_headers: Dict[str, str],
    test_db_session: Session,
):
    """Test workflow execution with invalid step reference in input mapping."""
    workflow_id = multi_step_workflow["workflow_id"]

    # Update the workflow to have an invalid step reference
    update_data = {
        "name": "Invalid Step Reference Workflow",
        "steps": [
            {
                "name": "Step 1",
                "mcp_id": multi_step_workflow["steps"][0]["mcp_id"],
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "workflow_input",
                        "workflow_input_key": "initial_data",
                    }
                },
            },
            {
                "name": "Step 2",
                "mcp_id": multi_step_workflow["steps"][1]["mcp_id"],
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "step_output",
                        "source_step_id": "non-existent-step",
                        "source_output_name": "processed_data",
                    }
                },
            },
        ],
    }

    response = test_app_client.put(
        f"/workflows/{workflow_id}", json=update_data, headers=jwt_headers
    )
    assert response.status_code == 200

    # Try to execute the workflow
    response = test_app_client.post(
        f"/workflows/{workflow_id}/execute",
        json={"initial_data": "test"},
        headers=jwt_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert "Invalid step reference" in data["error_message"]


def test_execute_workflow_with_missing_output(
    test_app_client: TestClient,
    multi_step_workflow: Dict,
    jwt_headers: Dict[str, str],
    test_db_session: Session,
):
    """Test workflow execution when a step's output is missing."""
    workflow_id = multi_step_workflow["workflow_id"]

    # Update the workflow to reference a non-existent output
    update_data = {
        "name": "Missing Output Workflow",
        "steps": [
            {
                "name": "Step 1",
                "mcp_id": multi_step_workflow["steps"][0]["mcp_id"],
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "workflow_input",
                        "workflow_input_key": "initial_data",
                    }
                },
            },
            {
                "name": "Step 2",
                "mcp_id": multi_step_workflow["steps"][1]["mcp_id"],
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "step_output",
                        "source_step_id": "step-1",
                        "source_output_name": "non-existent-output",
                    }
                },
            },
        ],
    }

    response = test_app_client.put(
        f"/workflows/{workflow_id}", json=update_data, headers=jwt_headers
    )
    assert response.status_code == 200

    # Try to execute the workflow
    response = test_app_client.post(
        f"/workflows/{workflow_id}/execute",
        json={"initial_data": "test"},
        headers=jwt_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert "Missing output" in data["error_message"]


def test_execute_workflow_with_concurrent_steps(
    test_app_client: TestClient,
    multi_step_workflow: Dict,
    jwt_headers: Dict[str, str],
    test_db_session: Session,
):
    """Test workflow execution with concurrent steps."""
    workflow_id = multi_step_workflow["workflow_id"]

    # Update the workflow to have concurrent steps
    update_data = {
        "name": "Concurrent Steps Workflow",
        "execution_mode": "concurrent",
        "steps": [
            {
                "name": "Step 1",
                "mcp_id": multi_step_workflow["steps"][0]["mcp_id"],
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "workflow_input",
                        "workflow_input_key": "initial_data",
                    }
                },
            },
            {
                "name": "Step 2",
                "mcp_id": multi_step_workflow["steps"][1]["mcp_id"],
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "workflow_input",
                        "workflow_input_key": "initial_data",
                    }
                },
            },
        ],
    }

    response = test_app_client.put(
        f"/workflows/{workflow_id}", json=update_data, headers=jwt_headers
    )
    assert response.status_code == 200

    # Execute the workflow
    response = test_app_client.post(
        f"/workflows/{workflow_id}/execute",
        json={"initial_data": "test"},
        headers=jwt_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["step_results"]) == 2
    # Verify that both steps were executed
    step_ids = {result["step_id"] for result in data["step_results"]}
    assert len(step_ids) == 2


def test_execute_workflow_with_retry_on_failure(
    test_app_client: TestClient,
    multi_step_workflow: Dict,
    jwt_headers: Dict[str, str],
    test_db_session: Session,
):
    """Test workflow execution with retry on failure."""
    workflow_id = multi_step_workflow["workflow_id"]

    # Update the workflow to include retry configuration
    update_data = {
        "name": "Retry on Failure Workflow",
        "error_handling": {
            "strategy": "retry",
            "max_retries": 3,
            "backoff_factor": 1.5,
        },
        "steps": multi_step_workflow["steps"],
    }

    response = test_app_client.put(
        f"/workflows/{workflow_id}", json=update_data, headers=jwt_headers
    )
    assert response.status_code == 200

    # Execute the workflow
    response = test_app_client.post(
        f"/workflows/{workflow_id}/execute",
        json={"initial_data": "test"},
        headers=jwt_headers,
    )

    assert response.status_code == 200
    data = response.json()
    # Check if retry information is included in the response
    assert "retry_attempts" in data
    assert data["retry_attempts"] <= 3  # Should not exceed max_retries


def test_execute_workflow_with_fallback_workflow(
    test_app_client: TestClient,
    multi_step_workflow: Dict,
    jwt_headers: Dict[str, str],
    test_db_session: Session,
):
    """Test workflow execution with fallback workflow on failure."""
    # Create a fallback workflow
    fallback_data = {
        "name": "Fallback Workflow",
        "description": "A simple fallback workflow",
        "steps": [
            {
                "name": "Fallback Step",
                "mcp_id": multi_step_workflow["steps"][0]["mcp_id"],
                "mcp_version_id": "1.0.0",
                "inputs": {
                    "input_data": {
                        "source_type": "workflow_input",
                        "workflow_input_key": "initial_data",
                    }
                },
            }
        ],
    }

    response = test_app_client.post(
        "/workflows/", json=fallback_data, headers=jwt_headers
    )
    assert response.status_code == 201
    fallback_workflow_id = response.json()["workflow_id"]

    # Update the main workflow to use the fallback
    update_data = {
        "name": "Workflow with Fallback",
        "error_handling": {
            "strategy": "fallback",
            "fallback_workflow_id": fallback_workflow_id,
        },
        "steps": multi_step_workflow["steps"],
    }

    response = test_app_client.put(
        f"/workflows/{multi_step_workflow['workflow_id']}",
        json=update_data,
        headers=jwt_headers,
    )
    assert response.status_code == 200

    # Execute the workflow
    response = test_app_client.post(
        f"/workflows/{multi_step_workflow['workflow_id']}/execute",
        json={"initial_data": "test"},
        headers=jwt_headers,
    )

    assert response.status_code == 200
    data = response.json()
    # Check if fallback information is included in the response
    assert "fallback_executed" in data
    if data["status"] == "FAILED":
        assert data["fallback_executed"] is True
