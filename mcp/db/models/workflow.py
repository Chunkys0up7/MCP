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

from uuid import UUID as PyUUID
import uuid
from datetime import datetime

from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
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

    id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    input_schema: Mapped[dict] = mapped_column(JSON, nullable=False)
    output_schema: Mapped[dict] = mapped_column(JSON, nullable=False)
    error_strategy: Mapped[str] = mapped_column(String, nullable=False)
    execution_mode: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    runs: Mapped[list["WorkflowRun"]] = relationship(
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

    id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[PyUUID] = mapped_column(
        SA_UUID(as_uuid=True), ForeignKey("workflow_definitions.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    inputs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    outputs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    workflow: Mapped["WorkflowDefinition"] = relationship(
        "WorkflowDefinition", back_populates="runs", foreign_keys=[workflow_id]
    )
    step_runs: Mapped[list["WorkflowStepRun"]] = relationship(
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

    id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id: Mapped[PyUUID] = mapped_column(
        SA_UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False
    )
    step_id: Mapped[str] = mapped_column(String, nullable=False)
    mcp_id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    inputs: Mapped[dict] = mapped_column(JSON, nullable=False)
    outputs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resource_usage: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Stores CPU/memory usage and other metrics

    # Relationships
    workflow_run: Mapped["WorkflowRun"] = relationship(
        "WorkflowRun", back_populates="step_runs", foreign_keys=[workflow_run_id]
    )

    def __repr__(self) -> str:
        """
        String representation of step run.

        Returns:
            str: Step run representation
        """
        return f"<WorkflowStepRun(step={self.step_id}, status={self.status})>"
