from fastapi import APIRouter, HTTPException, Depends, Body, Response
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path

from sqlalchemy.orm import Session
from mcp.db.session import get_db # DB session dependency
from mcp.db.models import WorkflowDefinition, WorkflowRun # Workflow models and MCP for checking existence

from mcp.schemas.workflow import (
    Workflow as WorkflowSchema, # Rename to avoid clash with model
    WorkflowCreate as WorkflowCreateSchema,
    WorkflowExecutionResult as WorkflowExecutionResultSchema # For validating steps
)
from mcp.core.types import MCPType # For type checking in MCP if needed

# Assuming API key dependency and mcp_server_registry will be passed or imported
# from ..main import get_api_key, mcp_server_registry # OLD IMPORT - REMOVE/COMMENT
from ..dependencies import get_current_subject # Changed from get_api_key to get_current_subject
# from ...core.registry import mcp_server_registry # NEW IMPORT for registry
from ...core import registry as mcp_registry_service # For MCP DB functions
from ...core.workflow_engine import WorkflowEngine # Added import
from ...schemas.mcd_constraints import ArchitecturalConstraints

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
        steps=[step.model_dump() for step in workflow_in.steps] # Store steps as JSON
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
        if key == "steps": # Only steps is a JSON field in the DB model
            setattr(db_workflow, key, value)
        elif hasattr(db_workflow, key):
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
    workflow_dict = {
        "workflow_id": str(db_workflow_definition.workflow_id),
        "name": db_workflow_definition.name,
        "description": db_workflow_definition.description,
        "steps": db_workflow_definition.steps
    }
    workflow_schema_for_engine = WorkflowSchema.model_validate(workflow_dict)

    # --- ADDED: Load Architectural Constraints (Example) ---
    constraints_file_path = Path(__file__).resolve().parent.parent.parent / "examples" / "mcd" / "sample_constraints.json"
    loaded_constraints: Optional[ArchitecturalConstraints] = None
    if constraints_file_path.exists():
        try:
            with open(constraints_file_path, 'r') as f:
                constraints_data = json.load(f)
                loaded_constraints = ArchitecturalConstraints(**constraints_data)
                print(f"Successfully loaded architectural constraints from {constraints_file_path}")
        except Exception as e:
            # Log this error, but don't necessarily block execution if constraints are optional for the engine
            print(f"Warning: Failed to load or parse architectural constraints from {constraints_file_path}: {e}")
            # loaded_constraints will remain None
    else:
        print(f"Info: Architectural constraints file not found at {constraints_file_path}. Proceeding without them.")
    # --- END ADDED ---

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
        # It's important to also update the in-memory db_workflow_run status if commit fails,
        # or ensure it's not used further if it's meant to be a placeholder until DB write.
        # For now, assume if commit fails, we raise before engine execution.
        raise HTTPException(status_code=500, detail=f"Failed to create workflow run record: {str(e)}")

    # Initialize the WorkflowEngine
    # MODIFIED: Pass db_session and loaded_constraints to WorkflowEngine
    workflow_engine = WorkflowEngine(db_session=db, constraints=loaded_constraints) 

    execution_result_schema: Optional[WorkflowExecutionResultSchema] = None
    try:
        # Update WorkflowRun status to RUNNING
        db_workflow_run.status = "RUNNING"
        db_workflow_run.started_at = datetime.utcnow()
        db.commit()
        db.refresh(db_workflow_run)

        # Execute the workflow
        # The WorkflowEngine's run_workflow method is async
        execution_result = await workflow_engine.run_workflow(
            workflow_schema_for_engine, 
            initial_inputs=initial_inputs
        )
        
        # Convert engine's result to the Pydantic schema for response and DB update
        execution_result_schema = WorkflowExecutionResultSchema(**execution_result.model_dump())

        # Update WorkflowRun with final status and results
        db_workflow_run.status = execution_result_schema.status
        db_workflow_run.finished_at = execution_result_schema.finished_at
        # Store detailed step results as JSON
        db_workflow_run.step_results = [step.model_dump() for step in execution_result_schema.step_results] if execution_result_schema.step_results else []
        # Store final outputs as JSON
        db_workflow_run.final_outputs = execution_result_schema.final_outputs if execution_result_schema.final_outputs else {}
        db_workflow_run.error_message = execution_result_schema.error_message
        
    except Exception as e:
        # This catches errors from workflow_engine.run_workflow or subsequent DB operations
        print(f"Error during workflow execution or result processing: {e}")
        db_workflow_run.status = "FAILED"
        db_workflow_run.error_message = db_workflow_run.error_message or str(e) # Preserve earlier error if any
        db_workflow_run.finished_at = datetime.utcnow()
        # execution_result_schema will be None or partially filled, response will be based on db_workflow_run
    
    finally:
        # Ensure final state of WorkflowRun is committed
        try:
            db.commit()
            db.refresh(db_workflow_run)
        except Exception as e:
            # Log this critical error, as the run record might be inconsistent
            print(f"CRITICAL: Failed to commit final WorkflowRun status for run ID {db_workflow_run.run_id}: {e}")
            # If this fails, the client might get a result, but DB record is stale.
            # For now, we'll still attempt to return what we have.
    
    # If execution_result_schema was successfully populated, return it
    if execution_result_schema:
        return execution_result_schema
    else:
        # If there was a major failure before execution_result_schema could be formed,
        # construct a minimal response from db_workflow_run
        # This ensures client always gets a WorkflowExecutionResultSchema structure
        # We need to ensure db_workflow_run has all necessary fields for this
        # (it does: workflow_id, run_id, status, started_at, finished_at, error_message)
        # Step results and final outputs might be empty/None here.
        # Ensure created_at is set if it's part of the schema and not auto-set by DB model default
        
        # Manually construct the schema if it wasn't formed due to an early critical error
        # The WorkflowExecutionResultSchema needs:
        # workflow_id: uuid.UUID
        # execution_id: uuid.UUID
        # status: str
        # started_at: datetime
        # finished_at: Optional[datetime] = None
        # step_results: Optional[List[StepExecutionResult]] = Field(default_factory=list)
        # final_outputs: Optional[Dict[str, Any]] = None
        # error_message: Optional[str] = None
        
        # The `db_workflow_run` object (WorkflowRun SQLAlchemy model) has:
        # run_id (uuid), workflow_id (uuid), status (str), started_at (datetime), 
        # finished_at (datetime), inputs (json), step_results (json), 
        # final_outputs (json), error_message (str)

        # We need to ensure the step_results from db_workflow_run (JSON) can be parsed back
        # into List[StepExecutionResult]. For now, this might be a simplification if an error
        # occurred very early.
        
        # A simple fallback:
        return WorkflowExecutionResultSchema(
            workflow_id=db_workflow_run.workflow_id,
            execution_id=db_workflow_run.run_id, # map db model's run_id to schema's execution_id
            status=db_workflow_run.status,
            started_at=db_workflow_run.started_at or datetime.utcnow(), # Ensure started_at is set
            finished_at=db_workflow_run.finished_at,
            step_results=[], # Default to empty if error was early
            final_outputs=db_workflow_run.final_outputs if db_workflow_run.final_outputs else None,
            error_message=db_workflow_run.error_message
        )

# Endpoint to get status of a specific workflow run
@router.get("/runs/{run_id}", response_model=WorkflowExecutionResultSchema) # This might need a more DB-aligned schema
async def get_workflow_run_status(
    run_id: str, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    try:
        run_uuid = uuid.UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run ID format.")

    db_run = db.query(WorkflowRun).filter(WorkflowRun.id == run_uuid).first()
    if not db_run:
        raise HTTPException(status_code=404, detail="Workflow run not found.")

    # Convert DB model to the response schema. This might need careful mapping.
    # WorkflowExecutionResultSchema expects certain fields.
    # We need to construct it from db_run and potentially related db_workflow_definition
    
    # Fetch the associated workflow definition to get the workflow_id for the response schema
    # (though db_run.workflow_id should suffice)
    # db_workflow_def = db.query(WorkflowDefinition).filter(WorkflowDefinition.workflow_id == db_run.workflow_id).first()
    # if not db_workflow_def:
        # This case should ideally not happen if DB constraints are set up
        # raise HTTPException(status_code=500, detail="Internal error: Workflow definition for the run not found.")

    return WorkflowExecutionResultSchema(
        workflow_id=str(db_run.workflow_id), # Ensure it's a string if UUID in DB
        execution_id=str(db_run.id), # Ensure it's a string
        status=db_run.status,
        started_at=db_run.started_at if db_run.started_at else datetime.min, # Handle None for started_at
        finished_at=db_run.finished_at,
        step_results=db_run.results_log if db_run.results_log else [], # Ensure it's a list
        final_outputs=db_run.outputs,
        error_message=db_run.error_message
    )

@router.get("/runs/", response_model=List[WorkflowExecutionResultSchema]) # Again, schema might need adjustment
async def list_all_workflow_runs(
    workflow_id: Optional[str] = None, # Optional filter by workflow_id
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_sub: str = Depends(get_current_subject)
):
    query = db.query(WorkflowRun)
    if workflow_id:
        try:
            wf_uuid = uuid.UUID(workflow_id)
            query = query.filter(WorkflowRun.workflow_id == wf_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid workflow_id filter format.")
    
    db_runs = query.order_by(WorkflowRun.started_at.desc().nulls_last()).offset(skip).limit(limit).all()
    
    results = []
    for db_run in db_runs:
        results.append(WorkflowExecutionResultSchema(
            workflow_id=str(db_run.workflow_id),
            execution_id=str(db_run.id),
            status=db_run.status,
            started_at=db_run.started_at if db_run.started_at else datetime.min,
            finished_at=db_run.finished_at,
            step_results=db_run.results_log if db_run.results_log else [],
            final_outputs=db_run.outputs,
            error_message=db_run.error_message
        ))
    return results

# TODO: Add endpoints for cancelling a run, retrying a failed run, etc. (more complex operations)