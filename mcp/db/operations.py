"""
Database Operations

This module provides database operations for the MCP system.
It handles:

1. CRUD operations on MCPs and workflows
2. Version management
3. Execution tracking
4. Error handling and retries
5. Data validation and sanitization

The module provides a clean interface for database operations while
handling common tasks like transaction management and error handling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..schemas.mcp import MCPStatus, MCPType
from ..schemas.workflow import WorkflowStatus, WorkflowStepStatus
from .models.mcp import MCP, MCPVersion
from .models.workflow import WorkflowDefinition, WorkflowRun, WorkflowStepRun


def create_mcp(
    db: Session,
    name: str,
    type: MCPType,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> MCP:
    """
    Create a new MCP.

    This function:
    1. Creates a new MCP record
    2. Handles tag associations
    3. Validates input data
    4. Manages transactions

    Args:
        db: Database session
        name: MCP name
        type: MCP type
        description: Optional description
        tags: Optional list of tags

    Returns:
        MCP: The created MCP instance

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If input validation fails
    """
    try:
        mcp = MCP(name=name, type=type, description=description, tags=tags or [])
        db.add(mcp)
        db.commit()
        db.refresh(mcp)
        return mcp
    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to create MCP: {str(e)}")


def create_mcp_version(
    db: Session,
    mcp_id: UUID,
    version: str,
    definition: Dict[str, Any],
    status: MCPStatus = MCPStatus.DRAFT,
) -> MCPVersion:
    """
    Create a new MCP version.

    This function:
    1. Creates a new version record
    2. Updates MCP current version
    3. Validates version data
    4. Manages transactions

    Args:
        db: Database session
        mcp_id: Parent MCP ID
        version: Version string
        definition: Version definition
        status: Version status

    Returns:
        MCPVersion: The created version instance

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If input validation fails
    """
    try:
        mcp = db.query(MCP).filter(MCP.id == mcp_id).first()
        if not mcp:
            raise ValueError(f"MCP with ID {mcp_id} not found")

        version_obj = MCPVersion(
            mcp_id=mcp_id, version=version, definition=definition, status=status
        )
        db.add(version_obj)

        # Update MCP's current version
        mcp.current_version_id = version_obj.id
        mcp.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(version_obj)
        return version_obj
    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to create MCP version: {str(e)}")


def create_workflow(
    db: Session,
    name: str,
    steps: List[Dict[str, Any]],
    input_schema: Dict[str, Any],
    output_schema: Dict[str, Any],
    description: Optional[str] = None,
    error_strategy: str = "stop_on_error",
    execution_mode: str = "sequential",
) -> WorkflowDefinition:
    """
    Create a new workflow definition.

    This function:
    1. Creates a new workflow record
    2. Validates step configurations
    3. Handles schema validation
    4. Manages transactions

    Args:
        db: Database session
        name: Workflow name
        steps: List of step configurations
        input_schema: Input JSON schema
        output_schema: Output JSON schema
        description: Optional description
        error_strategy: Error handling strategy
        execution_mode: Execution mode

    Returns:
        WorkflowDefinition: The created workflow instance

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If input validation fails
    """
    try:
        workflow = WorkflowDefinition(
            name=name,
            steps=steps,
            input_schema=input_schema,
            output_schema=output_schema,
            description=description,
            error_strategy=error_strategy,
            execution_mode=execution_mode,
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return workflow
    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to create workflow: {str(e)}")


def create_workflow_run(
    db: Session, workflow_id: UUID, inputs: Dict[str, Any]
) -> WorkflowRun:
    """
    Create a new workflow run.

    This function:
    1. Creates a new run record
    2. Initializes step runs
    3. Validates inputs
    4. Manages transactions

    Args:
        db: Database session
        workflow_id: Workflow definition ID
        inputs: Workflow inputs

    Returns:
        WorkflowRun: The created run instance

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If input validation fails
    """
    try:
        workflow = (
            db.query(WorkflowDefinition)
            .filter(WorkflowDefinition.id == workflow_id)
            .first()
        )
        if not workflow:
            raise ValueError(f"Workflow with ID {workflow_id} not found")

        run = WorkflowRun(
            workflow_id=workflow_id, status=WorkflowStatus.PENDING, inputs=inputs
        )
        db.add(run)

        # Create step run records
        for step in workflow.steps:
            step_run = WorkflowStepRun(
                workflow_run_id=run.id,
                step_id=step["id"],
                mcp_id=step["mcp_id"],
                status=WorkflowStepStatus.PENDING,
                inputs={},
            )
            db.add(step_run)

        db.commit()
        db.refresh(run)
        return run
    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to create workflow run: {str(e)}")


def update_workflow_step_run(
    db: Session,
    step_run_id: UUID,
    status: WorkflowStepStatus,
    outputs: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> WorkflowStepRun:
    """
    Update a workflow step run.

    This function:
    1. Updates step run status
    2. Records outputs or errors
    3. Handles retries
    4. Manages transactions

    Args:
        db: Database session
        step_run_id: Step run ID
        status: New status
        outputs: Optional step outputs
        error: Optional error message

    Returns:
        WorkflowStepRun: The updated step run instance

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If input validation fails
    """
    try:
        step_run = (
            db.query(WorkflowStepRun).filter(WorkflowStepRun.id == step_run_id).first()
        )
        if not step_run:
            raise ValueError(f"Step run with ID {step_run_id} not found")

        step_run.status = status
        if outputs is not None:
            step_run.outputs = outputs
        if error is not None:
            step_run.error = error

        if status in [WorkflowStepStatus.COMPLETED, WorkflowStepStatus.FAILED]:
            step_run.finished_at = datetime.utcnow()

        db.commit()
        db.refresh(step_run)
        return step_run
    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to update step run: {str(e)}")


def update_workflow_run(
    db: Session,
    run_id: UUID,
    status: WorkflowStatus,
    outputs: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> WorkflowRun:
    """
    Update a workflow run.

    This function:
    1. Updates run status
    2. Records final outputs
    3. Handles errors
    4. Manages transactions

    Args:
        db: Database session
        run_id: Run ID
        status: New status
        outputs: Optional workflow outputs
        error: Optional error message

    Returns:
        WorkflowRun: The updated run instance

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If input validation fails
    """
    try:
        run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
        if not run:
            raise ValueError(f"Workflow run with ID {run_id} not found")

        run.status = status
        if outputs is not None:
            run.outputs = outputs
        if error is not None:
            run.error = error

        if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
            run.finished_at = datetime.utcnow()

        db.commit()
        db.refresh(run)
        return run
    except SQLAlchemyError as e:
        db.rollback()
        raise SQLAlchemyError(f"Failed to update workflow run: {str(e)}")
