"""
Workflow Models

This module provides models for workflow definitions and execution.
It includes:

1. WorkflowDefinition model for definitions
2. WorkflowRun model for executions
3. WorkflowStepRun model for step executions
4. Model relationships
5. Model utilities

The models support:
- Workflow definition storage
- Step configuration
- Execution tracking
- Input/output management
- Error handling
"""

import uuid
from uuid import UUID

from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mcp.db.models.base import BaseModel, TimestampMixin, UUIDMixin


class WorkflowDefinition(BaseModel, UUIDMixin, TimestampMixin):
    """
    Workflow definition model.

    This model:
    1. Stores workflow definitions
    2. Manages steps
    3. Handles schemas
    4. Tracks metadata

    Attributes:
        id: UUID primary key
        name: Workflow name
        description: Optional description
        steps: List of step configurations
        input_schema: Input JSON schema
        output_schema: Output JSON schema
        error_strategy: Error handling strategy
        execution_mode: Execution mode
        created_at: Creation timestamp
        updated_at: Last update timestamp
        runs: List of workflow runs
    """

    __tablename__ = "workflow_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    steps = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    input_schema = Column(JSON, nullable=False)
    output_schema = Column(JSON, nullable=False)
    error_strategy = Column(
        String, nullable=False
    )  # Enum in DB, can be mapped to Enum if needed
    execution_mode = Column(
        String, nullable=False
    )  # Enum in DB, can be mapped to Enum if needed

    # Relationships
    runs = relationship(
        "WorkflowRun", back_populates="workflow", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        String representation of workflow definition.

        Returns:
            str: Workflow definition representation
        """
        return f"<WorkflowDefinition(name={self.name})>"


class WorkflowRun(BaseModel, UUIDMixin, TimestampMixin):
    """
    Workflow execution model.

    This model:
    1. Tracks workflow executions
    2. Manages status
    3. Handles inputs/outputs
    4. Records errors

    Attributes:
        id: UUID primary key
        workflow_id: Workflow definition ID
        status: Execution status
        inputs: Workflow inputs
        outputs: Workflow outputs
        error: Error message
        started_at: Start timestamp
        finished_at: Finish timestamp
        workflow: Workflow definition
        step_runs: List of step runs
    """

    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_definitions.id"), nullable=False
    )
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime)
    inputs = Column(JSON)
    outputs = Column(JSON)
    error = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    # Relationships
    workflow = relationship(
        "WorkflowDefinition", back_populates="runs", foreign_keys=[workflow_id]
    )
    step_runs = relationship(
        "WorkflowStepRun", back_populates="workflow_run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        String representation of workflow run.

        Returns:
            str: Workflow run representation
        """
        return f"<WorkflowRun(workflow={self.workflow.name}, status={self.status})>"


class WorkflowStepRun(BaseModel, UUIDMixin, TimestampMixin):
    """
    Workflow step execution model.

    This model:
    1. Tracks step executions
    2. Manages status
    3. Handles inputs/outputs
    4. Records errors

    Attributes:
        id: UUID primary key
        workflow_run_id: Workflow run ID
        step_id: Step ID
        mcp_id: MCP ID
        status: Execution status
        inputs: Step inputs
        outputs: Step outputs
        error: Error message
        started_at: Start timestamp
        finished_at: Finish timestamp
        retry_count: Number of retries
        workflow_run: Parent workflow run
        resource_usage: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # Stores CPU/memory usage and other metrics
    """

    __tablename__ = "workflow_step_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False
    )
    step_id = Column(String, nullable=False)
    mcp_id = Column(UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False)
    status = Column(
        String, nullable=False
    )  # Enum in DB, can be mapped to Enum if needed
    inputs = Column(JSON, nullable=False)
    outputs = Column(JSON)
    error = Column(String)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    retry_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    resource_usage: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Stores CPU/memory usage and other metrics

    # Relationships
    workflow_run = relationship(
        "WorkflowRun", back_populates="step_runs", foreign_keys=[workflow_run_id]
    )

    def __repr__(self) -> str:
        """
        String representation of step run.

        Returns:
            str: Step run representation
        """
        return f"<WorkflowStepRun(step={self.step_id}, status={self.status})>"
