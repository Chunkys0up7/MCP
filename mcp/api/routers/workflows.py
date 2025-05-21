from fastapi import APIRouter, HTTPException, Depends, Body, Path as FastApiPath
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path

from mcp.schemas.workflow import (
    Workflow, WorkflowCreate, WorkflowExecutionResult
)
# Assuming API key dependency and mcp_server_registry will be passed or imported
# from ..main import get_api_key, mcp_server_registry # OLD IMPORT - REMOVE/COMMENT
from ..dependencies import get_api_key # Assuming get_api_key is here
from ...core.registry import mcp_server_registry # NEW IMPORT for registry
from ...core.workflow_engine import WorkflowEngine # Added import

# Placeholder for get_api_key and mcp_server_registry for standalone router testing
# In real integration, these would come from the main app
# API_KEY_NAME = "X-API-Key-Placeholder"
# async def get_api_key():
# pass # Replace with actual dependency from ..main

# mcp_server_registry: Dict[str, Any] = {} # Replace with actual dependency from ..main

# --- Temporary In-Memory Storage (Replace with DB/JSON file persistence) ---
STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / ".mcp_data"
WORKFLOW_STORAGE_FILE = STORAGE_DIR / "chain_storage.json"

def load_workflows_from_storage() -> Dict[str, Workflow]:
    if not WORKFLOW_STORAGE_FILE.exists():
        return {}
    try:
        with open(WORKFLOW_STORAGE_FILE, 'r') as f:
            raw_data = json.load(f)
            deserialized_workflows = {}
            for wf_id, data in raw_data.items():
                try:
                    deserialized_workflows[wf_id] = Workflow(**data)
                except Exception as e:
                    print(f"Error deserializing workflow {wf_id}: {e}. Skipping.")
            return deserialized_workflows
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {WORKFLOW_STORAGE_FILE}. Returning empty workflow list.")
        return {}
    except Exception as e:
        print(f"Failed to load workflows from storage: {e}")
        return {}

def save_workflows_to_storage(workflows: Dict[str, Workflow]):
    serializable_workflows = {
        wf_id: wf.model_dump(mode='json') for wf_id, wf in workflows.items()
    }
    try:
        STORAGE_DIR.mkdir(exist_ok=True)
        with open(WORKFLOW_STORAGE_FILE, 'w') as f:
            json.dump(serializable_workflows, f, indent=2)
    except Exception as e:
        print(f"Failed to save workflows to storage: {e}")

workflow_registry: Dict[str, Workflow] = load_workflows_from_storage()
# --- End Temporary Storage ---

router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
    dependencies=[Depends(get_api_key)]
)

@router.post("/", response_model=Workflow, status_code=201)
async def create_workflow(workflow_in: WorkflowCreate):
    new_workflow_id = str(uuid.uuid4())
    # Ensure created_at and updated_at are set, and workflow_id is part of the Workflow model
    workflow_data = workflow_in.model_dump()
    new_workflow = Workflow(
        **workflow_data,
        workflow_id=new_workflow_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    for step in new_workflow.steps:
        if step.mcp_id not in mcp_server_registry:
            raise HTTPException(status_code=400, detail=f"MCP with ID {step.mcp_id} not found for step '{step.name}'.")

    workflow_registry[new_workflow.workflow_id] = new_workflow
    save_workflows_to_storage(workflow_registry)
    return new_workflow

@router.get("/", response_model=List[Workflow])
async def list_workflows():
    return list(workflow_registry.values())

@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str = FastApiPath(..., description="The ID of the workflow to retrieve")):
    if workflow_id not in workflow_registry:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow_registry[workflow_id]

@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_in: WorkflowCreate, workflow_id: str = FastApiPath(..., description="The ID of the workflow to update")):
    if workflow_id not in workflow_registry:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    existing_workflow = workflow_registry[workflow_id]
    updated_workflow_data = workflow_in.model_dump(exclude_unset=True)
    
    updated_workflow = existing_workflow.model_copy(update=updated_workflow_data)
    updated_workflow.updated_at = datetime.utcnow()
    
    for step in updated_workflow.steps:
        if step.mcp_id not in mcp_server_registry:
            raise HTTPException(status_code=400, detail=f"MCP with ID {step.mcp_id} not found for step '{step.name}'.")
            
    workflow_registry[workflow_id] = updated_workflow
    save_workflows_to_storage(workflow_registry)
    return updated_workflow

@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str = FastApiPath(..., description="The ID of the workflow to delete")):
    if workflow_id not in workflow_registry:
        raise HTTPException(status_code=404, detail="Workflow not found")
    del workflow_registry[workflow_id]
    save_workflows_to_storage(workflow_registry)
    return None

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResult)
async def execute_workflow(workflow_id: str = FastApiPath(..., description="The ID of the workflow to execute"),
                           initial_inputs: Optional[Dict[str, Any]] = Body(None, description="Initial inputs for the workflow")):
    if workflow_id not in workflow_registry:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_to_execute = workflow_registry[workflow_id]
    
    # Extract the actual inputs from the request body
    actual_initial_inputs: Optional[Dict[str, Any]] = None
    if initial_inputs and "initial_inputs" in initial_inputs:
        actual_initial_inputs = initial_inputs.get("initial_inputs")
        # Basic type check, could be more robust if specific structure expected
        if not isinstance(actual_initial_inputs, dict):
            # Log a warning or raise an error if the structure is not as expected
            print(f"WARNING: 'initial_inputs' key found in request body, but its value is not a dictionary. Received: {actual_initial_inputs}")
            # Decide on behavior: pass it as is, or treat as no inputs, or error.
            # For now, let's try to be lenient and pass it if it's not dict, or None if it caused issues.
            # Or, more strictly, assume it's an error if initial_inputs.initial_inputs isn't a dict.
            # For this fix, we'll assume if 'initial_inputs' key exists, its value should be the dict we want.
            # If initial_inputs = {"initial_inputs": "not_a_dict"}, this will pass "not_a_dict" to engine.
            # This might need further refinement based on how strictly the API contract is defined.
            pass # actual_initial_inputs is already set
    elif initial_inputs: # If initial_inputs is not None but doesn't have the 'initial_inputs' key, use it directly
        actual_initial_inputs = initial_inputs

    # Instantiate and use the WorkflowEngine
    engine = WorkflowEngine(mcp_server_registry=mcp_server_registry)
    try:
        # Pass the potentially unwrapped inputs to the engine
        execution_result = await engine.run_workflow(workflow_to_execute, actual_initial_inputs)
        return execution_result
    except Exception as e:
        # This is a fallback for unexpected errors within the engine run itself,
        # though the engine should ideally catch and format its own operational errors.
        # The WorkflowExecutionResult from the engine should already contain error details if the workflow failed gracefully.
        import traceback
        print(f"Critical error during engine.run_workflow: {str(e)}\n{traceback.format_exc()}")
        # Return a generic server error if the engine itself crashed badly
        # However, the engine is designed to return a WorkflowExecutionResult even on failure.
        # This path might be hit if engine instantiation fails or a non-handled exception occurs before engine.run_workflow starts its try/finally.
        # Consider if a specific error response model is better here or if this indicates a bug in the engine's error handling.
        # For now, we'll assume the engine.run_workflow will always return a valid WorkflowExecutionResult.
        # If the engine itself has an unhandled exception, FastAPI will return a 500 error.
        # So, a specific catch here might be for logging or shaping a very specific error response if needed.
        # Let's rely on the engine to produce a WorkflowExecutionResult indicating failure.
        raise HTTPException(status_code=500, detail=f"Workflow execution engine failed: {str(e)}")

    # ---- Old placeholder logic (removed) ----
    # start_time = datetime.utcnow()
    # print(f"Executing workflow: {workflow_to_execute.name} with initial inputs: {initial_inputs}")
    # return WorkflowExecutionResult(
    #     workflow_id=workflow_id,
    #     status="SIMULATED_SUCCESS",
    #     started_at=start_time,
    #     finished_at=datetime.utcnow(),
    #     step_results=[{
    #         "step_id": step.step_id, 
    #         "mcp_id": step.mcp_id, 
    #         "status": "simulated_complete", 
    #         "output": "dummy_data"
    #     } for step in workflow_to_execute.steps],
    #     final_outputs={"message": "Workflow execution simulated."}
    # ) 