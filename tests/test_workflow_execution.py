# tests/test_workflow_execution.py
"""
End-to-end tests for workflow creation and execution.

Prerequisites:
- FastAPI application must be running.
- `requests` library must be installed (`pip install requests`).
- `pytest` library must be installed (`pip install pytest`).

Environment Variables or Configuration:
- API_BASE_URL: The base URL of the running MCP API (e.g., http://localhost:8000)
- MCP_API_KEY: A valid API key for authentication.
"""

import os
import time
import uuid

import pytest
import requests

from tests.workflow_mcp_scripts import CONCAT_MCP_SCRIPT, ECHO_MCP_SCRIPT

# --- Test Configuration ---
# Load from environment variables or set defaults
API_BASE_URL = os.getenv(
    "API_BASE_URL", "http://127.0.0.1:8000"
)  # Default for local dev
API_KEY = os.getenv(
    "MCP_API_KEY", "test_api_key_placeholder"
)  # NEW: Using MCP_API_KEY from server

if API_KEY == "test_api_key_placeholder":
    print(
        "WARNING: Using placeholder API key for tests. Please set MCP_API_KEY environment variable."
    )

HEADERS = {
    "X-API-Key": API_KEY,  # Use the new variable
    "Content-Type": "application/json",
}


# Helper function to create or get an MCP
def create_or_get_mcp(name: str, script_content: str, description: str) -> str:
    """
    Creates a PythonScriptMCP if it doesn't exist by name, or returns the ID of the existing one.

    Args:
        name (str): The desired name of the MCP.
        script_content (str): The Python script for the MCP.
        description (str): Description of the MCP.

    Returns:
        str: The ID of the MCP.

    Raises:
        Exception: If MCP creation or retrieval fails.
    """
    # Check if MCP exists
    try:
        response = requests.get(f"{API_BASE_URL}/context", headers=HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        mcps = response.json()
        for mcp in mcps:
            if mcp.get("name") == name and mcp.get("type") == "PYTHON_SCRIPT":
                print(f"Found existing MCP '{name}' with ID: {mcp['id']}")
                return mcp["id"]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to list existing MCPs: {e}")

    # If not found, create it
    mcp_payload = {
        "name": name,
        "type": "python_script",
        "description": description,
        "config": {
            "script_content": script_content,
            "script_path": f"./mcp_scripts/generated/{name.replace(' ', '_').lower()}.py",  # Dummy path
        },
    }
    print(f"Creating MCP '{name}' with payload: {mcp_payload}")
    try:
        response = requests.post(
            f"{API_BASE_URL}/context", json=mcp_payload, headers=HEADERS
        )
        response.raise_for_status()
        created_mcp = response.json()
        mcp_id = created_mcp.get("id")
        if not mcp_id:
            pytest.fail(
                f"MCP '{name}' created but ID is missing in response: {created_mcp}"
            )
        print(f"MCP '{name}' created successfully with ID: {mcp_id}")
        return mcp_id
    except requests.exceptions.RequestException as e:
        pytest.fail(
            f"Failed to create MCP '{name}': {e.response.text if e.response else e}"
        )
    return ""  # Should not be reached if pytest.fail works


@pytest.fixture(scope="module")
def setup_test_mcps():
    """Pytest fixture to set up (create or get) MCPs needed for workflow tests."""
    print("\nSetting up test MCPs...")
    try:
        echo_mcp_id = create_or_get_mcp(
            name="Test Echo String MCP",
            script_content=ECHO_MCP_SCRIPT,
            description="Test MCP that echoes its input string.",
        )
        concat_mcp_id = create_or_get_mcp(
            name="Test Concatenate Strings MCP",
            script_content=CONCAT_MCP_SCRIPT,
            description="Test MCP that concatenates two input strings.",
        )
        return {"echo_mcp_id": echo_mcp_id, "concat_mcp_id": concat_mcp_id}
    except Exception as e:
        pytest.fail(f"Failed during MCP setup: {e}")
    return {}  # Should not reach here


def test_workflow_creation_and_execution(setup_test_mcps):
    """
    Tests creating a workflow with multiple steps (static, workflow input, step output)
    and then executes it, validating the final output.
    """
    mcp_ids = setup_test_mcps
    echo_mcp_id = mcp_ids["echo_mcp_id"]
    concat_mcp_id = mcp_ids["concat_mcp_id"]

    workflow_name = f"Test String Manipulation Workflow - {uuid.uuid4()}"
    workflow_payload = {
        "name": workflow_name,
        "description": "A test workflow for string manipulation using echo and concat MCPs.",
        "steps": [
            {
                "name": "Step 1: Get Initial String (from Workflow Input)",
                "mcp_id": echo_mcp_id,
                "inputs": {
                    "input_string": {  # This key must match the expected input name in ECHO_MCP_SCRIPT
                        "source_type": "workflow_input",
                        "workflow_input_key": "initial_message",
                    }
                },
            },
            {
                "name": "Step 2: Define Suffix (Static Value)",
                "mcp_id": echo_mcp_id,
                "inputs": {
                    "input_string": {
                        "source_type": "static_value",
                        "value": "-suffix-from-static",
                    }
                },
            },
            {
                "name": "Step 3: Combine Initial and Suffix",
                "mcp_id": concat_mcp_id,
                "inputs": {
                    "string1": {  # Key must match CONCAT_MCP_SCRIPT's expected input
                        "source_type": "step_output",
                        # This step_id needs to be the *actual* ID of Step 1 once created.
                        # For now, we assume the workflow definition implicitly knows step order for sequential.
                        # The WorkflowEngine resolves based on the order in the `steps` list.
                        # However, WorkflowStepInput schema requires source_step_id for STEP_OUTPUT.
                        # The API/Engine must handle this. Our Workflow Pydantic model auto-generates step_id.
                        # This implies we MUST create the workflow first, get its step_ids, then potentially update it,
                        # or the backend must resolve this by order/name if IDs are not known at definition time.
                        # For this test, we will define the workflow in one go and assume engine can resolve.
                        # Ideally, client would make placeholder step_ids and server would fill them.
                        # For now, let's assume this test structure will work with how the engine is built.
                        # This is a tricky part for workflow definitions.
                        # The current WorkflowEngine doesn't look up steps by name, but uses stored step_id in workflow_context.
                        # This test needs to be robust to how WorkflowStep.step_id is generated and used.
                        # Let's assume we can't know the step_id beforehand when defining the payload.
                        # The `_resolve_step_inputs` in WorkflowEngine expects actual step_id in `workflow_context`.
                        # This means the current test structure for Step 3's inputs is problematic for source_step_id.
                        # We'll simplify for now, and acknowledge this is an area for refinement in the workflow system.
                        # For the test, we'll have to create the workflow, then GET it to find the assigned step_ids,
                        # then formulate the execute call with correct references IF the workflow execution logic
                        # doesn't handle symbolic references or ordering implicitly.
                        # The current WorkflowEngine.run_workflow seems to populate workflow_context using the step.step_id
                        # from the Workflow object. So, the Workflow object passed to run_workflow should have these.
                        # The WorkflowStepInput.source_step_id MUST match one of these.
                        # This test will POST the workflow, then GET it to retrieve step_ids.
                        # Then, it will have to re-construct step 3 inputs for the execution payload if needed,
                        # OR, more simply, ensure the Workflow definition itself contains correct source_step_ids.
                        # The Pydantic model for WorkflowStep *auto-generates* step_id. So, the client doesn't send it.
                        # This is good. The server will have them. The client can build the `inputs` part dynamically.
                        # Let's try defining the step_ids manually in the payload to match the generated ones. This is not ideal for real use.
                        # A better way: workflow creation returns the full workflow object with generated step_ids.
                        "source_step_id": "placeholder_step1_id",  # This will be replaced after workflow creation
                        "source_output_name": "output_string",  # Output name from ECHO_MCP_SCRIPT
                    },
                    "string2": {
                        "source_type": "step_output",
                        "source_step_id": "placeholder_step2_id",  # This will be replaced
                        "source_output_name": "output_string",
                    },
                },
            },
        ],
    }

    # 1. Create Workflow
    print(f"Creating workflow: {workflow_name}")
    workflow_id = None
    try:
        response = requests.post(
            f"{API_BASE_URL}/workflows/", json=workflow_payload, headers=HEADERS
        )
        response.raise_for_status()
        created_workflow = response.json()
        workflow_id = created_workflow.get("workflow_id")
        assert workflow_id, "Workflow ID missing in creation response"
        print(f"Workflow '{workflow_name}' created successfully with ID: {workflow_id}")

        # Extract generated step_ids to update the payload for Step 3 for correctness
        # This is crucial because WorkflowStepInput.source_step_id must reference an actual step_id
        # generated by the server during workflow creation (as per WorkflowStep Pydantic model).
        created_workflow["steps"][0]["step_id"]
        created_workflow["steps"][1]["step_id"]

        # Update Step 3 in the *original* workflow_payload (or the created_workflow object to re-PUT)
        # For simplicity in this test, we'll assume the execution takes the workflow_id and initial_inputs,
        # and the workflow stored on the server already has these correct step_ids internally.
        # The _resolve_step_inputs uses the Workflow object passed to it, which should be the one fetched or created.
        # If we re-construct payload for execution, it's more complex.
        # Let's test if the Workflow object stored by the POST is complete.
        # The crucial part is that the `Workflow` object inside the `WorkflowEngine` during `run_workflow`
        # must have these step_ids correctly linked in the `inputs` of subsequent steps.
        # The current API for POST /workflows takes WorkflowCreate, which contains WorkflowSteps.
        # The WorkflowStep *does not* take source_step_id as part of its `inputs` definition in the *schema* for `WorkflowCreate`.
        # This is a design flaw in the test or the schemas previously defined.
        # WorkflowStepInput.source_step_id is part of WorkflowStepInput, which is inside WorkflowStep.inputs.
        # This means the client *must* provide the source_step_id when creating the workflow.
        # This is only possible if client pre-generates step_ids or uses symbolic names that backend resolves.
        # Our Pydantic models (WorkflowStep.step_id) auto-generate them. This creates a cycle for the client.

        # RESOLUTION for the test: Modify the payload *before* creating the workflow, assuming we can
        # deterministically assign temporary IDs that the backend will honor OR (more realistically)
        # create steps that don't have inter-dependencies first, then add/update.
        # For this test, let's make temporary IDs and hope the server-side uses them if provided, or updates them.
        # This is a common challenge in defining graph-like structures via JSON.

        # Re-creating the payload with known temporary IDs for steps, then confirming server uses them or replaces.
        # Pydantic `default_factory` for step_id means if we provide one, it should be used.
        temp_step1_id = f"temp_step_{uuid.uuid4()}"
        temp_step2_id = f"temp_step_{uuid.uuid4()}"
        temp_step3_id = f"temp_step_{uuid.uuid4()}"

        revised_workflow_payload = {
            "name": f"Test String Workflow Revised - {uuid.uuid4()}",
            "description": "Revised test workflow with explicit step_ids for input mapping.",
            "steps": [
                {
                    "step_id": temp_step1_id,
                    "name": "Step 1: Get Initial String",
                    "mcp_id": echo_mcp_id,
                    "inputs": {
                        "input_string": {
                            "source_type": "workflow_input",
                            "workflow_input_key": "initial_message",
                        }
                    },
                },
                {
                    "step_id": temp_step2_id,
                    "name": "Step 2: Define Suffix",
                    "mcp_id": echo_mcp_id,
                    "inputs": {
                        "input_string": {
                            "source_type": "static_value",
                            "value": "-suffix-from-static",
                        }
                    },
                },
                {
                    "step_id": temp_step3_id,
                    "name": "Step 3: Combine",
                    "mcp_id": concat_mcp_id,
                    "inputs": {
                        "string1": {
                            "source_type": "step_output",
                            "source_step_id": temp_step1_id,
                            "source_output_name": "output_string",
                        },
                        "string2": {
                            "source_type": "step_output",
                            "source_step_id": temp_step2_id,
                            "source_output_name": "output_string",
                        },
                    },
                },
            ],
        }
        response = requests.post(
            f"{API_BASE_URL}/workflows/", json=revised_workflow_payload, headers=HEADERS
        )
        response.raise_for_status()
        created_workflow = response.json()
        workflow_id = created_workflow.get("workflow_id")
        assert workflow_id, "Revised Workflow ID missing"
        print(f"Revised workflow created successfully with ID: {workflow_id}")

        # Verify if the server used our step_ids or generated new ones (important for `source_step_id` in engine)
        # The `WorkflowEngine` will use the `Workflow` object fetched from `workflow_registry`,
        # which is populated by the `created_workflow` response. So, these step_ids should be consistent.
        server_step1_id = created_workflow["steps"][0]["step_id"]
        server_step2_id = created_workflow["steps"][1]["step_id"]
        assert (
            server_step1_id == temp_step1_id
        ), f"Server step 1 ID {server_step1_id} != client {temp_step1_id}"
        assert (
            server_step2_id == temp_step2_id
        ), f"Server step 2 ID {server_step2_id} != client {temp_step2_id}"

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Workflow creation failed: {e.response.text if e.response else e}")
    except AssertionError as e:
        pytest.fail(f"Assertion failed during workflow creation: {e}")

    # 2. Execute Workflow
    if not workflow_id:  # Should have failed earlier if no ID
        pytest.fail("Cannot execute workflow, ID not obtained.")

    execution_payload = {"initial_inputs": {"initial_message": "HelloFromTest"}}
    print(f"Executing workflow ID: {workflow_id} with payload: {execution_payload}")
    try:
        # Add a small delay if server needs time to fully process/save workflow
        time.sleep(0.5)
        response = requests.post(
            f"{API_BASE_URL}/workflows/{workflow_id}/execute",
            json=execution_payload,
            headers=HEADERS,
        )
        response.raise_for_status()
        execution_result = response.json()
        print(f"Execution result: {execution_result}")

        assert (
            execution_result.get("status") == "SUCCESS"
        ), f"Workflow execution failed. Status: {execution_result.get('status')}. Error: {execution_result.get('error_message')}"

        final_outputs = execution_result.get("final_outputs")
        assert (
            final_outputs is not None
        ), "Final outputs missing from successful execution result."

        # Expected output from Step 3 (Concat MCP)
        # Step 1 output: {"output_string": "HelloFromTest"}
        # Step 2 output: {"output_string": "-suffix-from-static"}
        # Step 3 input: string1="HelloFromTest", string2="-suffix-from-static"
        # Step 3 output: {"concatenated_string": "HelloFromTest-suffix-from-static"}
        # This is also the final_output of the workflow (as per current engine logic)
        expected_final_concat = "HelloFromTest-suffix-from-static"
        assert (
            final_outputs.get("concatenated_string") == expected_final_concat
        ), f"Final output mismatch. Expected: '{expected_final_concat}', Got: '{final_outputs.get("concatenated_string")}'"

        print(
            f"Workflow '{workflow_name}' (actual: {created_workflow.get('name')}) executed successfully with correct output."
        )

    except requests.exceptions.RequestException as e:
        pytest.fail(
            f"Workflow execution request failed: {e.response.text if e.response else e}"
        )
    except AssertionError as e:
        pytest.fail(f"Assertion failed during workflow execution: {e}")
    finally:
        # 3. Cleanup: Delete the workflow
        if workflow_id:
            print(f"Cleaning up: Deleting workflow ID {workflow_id}")
            try:
                del_response = requests.delete(
                    f"{API_BASE_URL}/workflows/{workflow_id}", headers=HEADERS
                )
                del_response.raise_for_status()
                print(f"Workflow {workflow_id} deleted successfully.")
            except requests.exceptions.RequestException as e:
                print(
                    f"WARN: Failed to delete workflow {workflow_id}: {e.response.text if e.response else e}"
                )


# To run this test:
# 1. Ensure your FastAPI server is running.
# 2. Set API_BASE_URL and MCP_API_KEY environment variables if not using defaults.
# 3. Run `pytest tests/test_workflow_execution.py` from the project root.
