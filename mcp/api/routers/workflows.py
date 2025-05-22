from fastapi import APIRouter, HTTPException, Depends, Body, Path as FastApiPath, Response
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path

from sqlalchemy.orm import Session
from mcp.db.session import get_db # DB session dependency
from mcp.db.models import WorkflowDefinition, WorkflowRun, MCP as MCPModel # Workflow models and MCP for checking existence

from mcp.schemas.workflow import (
    Workflow as WorkflowSchema, # Rename to avoid clash with model
    WorkflowCreate as WorkflowCreateSchema,
    WorkflowExecutionResult as WorkflowExecutionResultSchema,
    WorkflowStep # For validating steps
)
from mcp.core.types import MCPType # For type checking in MCP if needed

# Assuming API key dependency and mcp_server_registry will be passed or imported
# from ..main import get_api_key, mcp_server_registry # OLD IMPORT - REMOVE/COMMENT
from ..dependencies import get_current_subject # Changed from get_api_key to get_current_subject
# from ...core.registry import mcp_server_registry # NEW IMPORT for registry
from ...core import registry as mcp_registry_service # For MCP DB functions
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

def load_workflows_from_storage() -> Dict[str, WorkflowSchema]:
    if not WORKFLOW_STORAGE_FILE.exists():
        return {}
    try:
        with open(WORKFLOW_STORAGE_FILE, 'r') as f:
            raw_data = json.load(f)
            deserialized_workflows = {}
            for wf_id, data in raw_data.items():
                try:
                    deserialized_workflows[wf_id] = WorkflowSchema(**data)
                except Exception as e:
                    print(f"Error deserializing workflow {wf_id}: {e}. Skipping.")
            return deserialized_workflows
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {WORKFLOW_STORAGE_FILE}. Returning empty workflow list.")
        return {}
    except Exception as e:
        print(f"Failed to load workflows from storage: {e}")
        return {}

def save_workflows_to_storage(workflows: Dict[str, WorkflowSchema]):
    serializable_workflows = {
        wf_id: wf.model_dump(mode='json') for wf_id, wf in workflows.items()
    }
    try:
        STORAGE_DIR.mkdir(exist_ok=True)
        with open(WORKFLOW_STORAGE_FILE, 'w') as f:
            json.dump(serializable_workflows, f, indent=2)
    except Exception as e:
        print(f"Failed to save workflows to storage: {e}")

workflow_registry: Dict[str, WorkflowSchema] = load_workflows_from_storage()
# --- End Temporary Storage ---

router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
    dependencies=[Depends(get_current_subject)] # Changed to get_current_subject
)

# Helper function to get MCP instance (placeholder, needs proper implementation)
# This is a critical piece for execution. For now, routes will focus on definition CRUD.
# The actual instantiation of MCPs from DB for execution engine is complex.
# The WorkflowEngine will need to be adapted to take MCP definitions from DB.
async def get_mcp_instance_for_execution(mcp_id: str, db: Session):
    mcp_definition = mcp_registry_service.load_mcp_definition_from_db(db, mcp_id)
    if not mcp_definition:
        return None
    # This is where you would instantiate the correct BaseMCPServer subclass
    # using mcp_definition.type and the config from its latest version.
    # For now, this part is a simplification / placeholder.
    # The mcp_server_registry used by WorkflowEngine needs to be rethought.
    # It might become a dynamic loader or the engine needs to fetch & instantiate.
    # For CRUD, we don't need instances, but for execution we do.
    
    # Placeholder: this would be the part of mcp_server_registry
    # that WorkflowEngine currently expects. This part needs to be fully designed.
    # This is NOT a complete solution for execution.
    if mcp_definition.type == MCPType.LLM_PROMPT.value:
        # Need to load config from latest version of mcp_definition
        # from mcp.core.llm_prompt import LLMPromptMCP, LLMPromptConfig
        # latest_version = mcp_definition.versions[-1] if mcp_definition.versions else None
        # if latest_version:
        #     config = LLMPromptConfig(**latest_version.config_snapshot, id=str(mcp_definition.id), name=mcp_definition.name, type=mcp_definition.type)
        #     return LLMPromptMCP(config)
        pass # This is a placeholder
    # Add other MCP types here
    return None # Placeholder

@router.post("/", response_model=WorkflowSchema, status_code=201)
async def create_workflow_definition(
    workflow_in: WorkflowCreateSchema, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    # Validate that MCPs in steps exist
    for step_data in workflow_in.steps:
        mcp_def = mcp_registry_service.load_mcp_definition_from_db(db=db, mcp_id_str=step_data.mcp_id)
        if not mcp_def:
            raise HTTPException(status_code=404, detail=f"MCP with ID {step_data.mcp_id} for step '{step_data.name}' not found.")

    db_workflow = WorkflowDefinition(
        name=workflow_in.name,
        description=workflow_in.description,
        steps=[step.model_dump() for step in workflow_in.steps], # Store steps as JSON
        execution_mode=workflow_in.execution_mode,
        error_handling=workflow_in.error_handling.model_dump() # Store error handling as JSON
    )
    db.add(db_workflow)
    try:
        db.commit()
        db.refresh(db_workflow)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create workflow definition: {str(e)}")
    return db_workflow # Pydantic will convert from ORM model due to Config.from_attributes=True

@router.get("/", response_model=List[WorkflowSchema])
async def list_workflow_definitions(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100, 
    current_user_sub: str = Depends(get_current_subject)
):
    workflows = db.query(WorkflowDefinition).offset(skip).limit(limit).all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowSchema)
async def get_workflow_definition(
    workflow_id: str, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    try:
        wf_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow ID format.")
    
    db_workflow = db.query(WorkflowDefinition).filter(WorkflowDefinition.workflow_id == wf_uuid).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow definition not found")
    return db_workflow

@router.put("/{workflow_id}", response_model=WorkflowSchema)
async def update_workflow_definition(
    workflow_id: str, 
    workflow_in: WorkflowCreateSchema, # Using Create schema for full update
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    try:
        wf_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow ID format.")

    db_workflow = db.query(WorkflowDefinition).filter(WorkflowDefinition.workflow_id == wf_uuid).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow definition not found for update.")

    # Validate MCPs in updated steps
    for step_data in workflow_in.steps:
        mcp_def = mcp_registry_service.load_mcp_definition_from_db(db=db, mcp_id_str=step_data.mcp_id)
        if not mcp_def:
            raise HTTPException(status_code=404, detail=f"MCP with ID {step_data.mcp_id} for step '{step_data.name}' not found.")

    update_data = workflow_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "steps" or key == "error_handling": # These are JSON fields
            setattr(db_workflow, key, value) # value is already a dict from model_dump()
        else:
            setattr(db_workflow, key, value)
    
    try:
        db.commit()
        db.refresh(db_workflow)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update workflow definition: {str(e)}")
    return db_workflow

@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow_definition(
    workflow_id: str, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    try:
        wf_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow ID format.")

    db_workflow = db.query(WorkflowDefinition).filter(WorkflowDefinition.workflow_id == wf_uuid).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow definition not found for deletion.")
    
    # Consider related WorkflowRuns: should they be deleted, orphaned, or prevent deletion?
    # For now, assuming they might be orphaned or handled by DB cascade if set up.
    db.delete(db_workflow)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow definition: {str(e)}")
    return Response(status_code=204)

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResultSchema)
async def execute_workflow(
    workflow_id: str, 
    initial_inputs: Optional[Dict[str, Any]] = Body(None, description="Initial inputs for the workflow"), 
    db: Session = Depends(get_db),
    current_user_sub: str = Depends(get_current_subject)
):
    try:
        wf_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow ID format.")

    db_workflow_definition = db.query(WorkflowDefinition).filter(WorkflowDefinition.workflow_id == wf_uuid).first()
    if not db_workflow_definition:
        raise HTTPException(status_code=404, detail="Workflow definition not found for execution.")

    # Convert DB model to Pydantic schema for the engine
    # The WorkflowEngine expects a Pydantic Workflow schema
    workflow_schema_for_engine = WorkflowSchema.model_validate(db_workflow_definition)

    # Create a WorkflowRun entry to track this execution
    db_workflow_run = WorkflowRun(
        workflow_id=db_workflow_definition.workflow_id,
        status="PENDING", # Initial status
        inputs=initial_inputs
    )
    db.add(db_workflow_run)
    try:
        db.commit()
        db.refresh(db_workflow_run)
    except Exception as e:
        db.rollback()
        # Log error and potentially return a specific error response
        raise HTTPException(status_code=500, detail=f"Failed to initiate workflow run record: {str(e)}")

    actual_initial_inputs: Optional[Dict[str, Any]] = None
    if initial_inputs and "initial_inputs" in initial_inputs:
        actual_initial_inputs = initial_inputs.get("initial_inputs")
    elif initial_inputs:
        actual_initial_inputs = initial_inputs
        
    # The WorkflowEngine needs to be adapted to not rely on the global mcp_server_registry
    # but rather fetch MCP definitions from the DB as needed, or be provided with them.
    # This is a MAJOR REFACTORING POINT for the WorkflowEngine itself.
    # For now, this will likely fail if WorkflowEngine has not been updated.
    # I am proceeding assuming WorkflowEngine will be adapted or this part will be fixed later.
    
    # Placeholder: The mcp_server_registry for the engine needs to be built dynamically based on MCPs in workflow steps
    # This is a simplified placeholder and likely won't work without engine refactor.
    # It would need to load MCPs from DB and instantiate them.
    current_mcp_registry_for_engine = {}
    # for step in workflow_schema_for_engine.steps:
        # mcp_instance = await get_mcp_instance_for_execution(step.mcp_id, db)
        # if mcp_instance:
            # current_mcp_registry_for_engine[step.mcp_id] = { "instance": mcp_instance, "config": "..."} # Needs full structure
        # else:
            # db_workflow_run.status = "FAILED"
            # db_workflow_run.error_message = f"Could not load MCP instance for ID {step.mcp_id}"
            # db.commit()
            # raise HTTPException(status_code=500, detail=db_workflow_run.error_message)

    engine = WorkflowEngine(mcp_server_registry=current_mcp_registry_for_engine) # This registry is problematic
    
    try:
        db_workflow_run.status = "RUNNING"
        db.commit()
        db.refresh(db_workflow_run)

        execution_result: WorkflowExecutionResultSchema = await engine.run_workflow(
            workflow_schema_for_engine, 
            actual_initial_inputs
        )
        
        # Update WorkflowRun with results
        db_workflow_run.status = execution_result.status
        db_workflow_run.finished_at = execution_result.finished_at # Should be set by engine
        db_workflow_run.outputs = execution_result.final_outputs
        db_workflow_run.step_results = execution_result.step_results
        db_workflow_run.error_message = execution_result.error_message
        db.commit()
        db.refresh(db_workflow_run)
        
        # Augment execution_result with the database run_id (which is execution_id in schema)
        # execution_result.execution_id = str(db_workflow_run.run_id)
        # The schema already generates one, so ensure they align or decide which one is canonical.
        # For now, returning the engine's result. The DB has its own run_id.
        return execution_result

    except Exception as e:
        db.rollback() # Rollback any status changes if engine crashes before returning
        db_workflow_run.status = "FAILED"
        db_workflow_run.error_message = f"Critical error during workflow execution: {str(e)}"
        if not db_workflow_run.finished_at:
             db_workflow_run.finished_at = datetime.utcnow()
        db.commit()
        # Log critical error e
        raise HTTPException(status_code=500, detail=db_workflow_run.error_message)

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