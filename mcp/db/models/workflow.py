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

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy import Column, String, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from mcp.db.models.base import BaseModel, UUIDMixin, TimestampMixin

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
    
    __tablename__ = 'workflow_definitions'
    
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    steps = Column(JSON, nullable=False)
    input_schema = Column(JSON, nullable=False)
    output_schema = Column(JSON, nullable=False)
    error_strategy = Column(Enum('stop', 'continue', 'retry', name='error_strategy'), nullable=False)
    execution_mode = Column(Enum('sequential', 'parallel', name='execution_mode'), nullable=False)
    
    # Relationships
    runs = relationship('WorkflowRun', back_populates='workflow', cascade='all, delete-orphan')
    
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
    
    __tablename__ = 'workflow_runs'
    
    workflow_id = Column(UUID(as_uuid=True), ForeignKey('workflow_definitions.id'), nullable=False)
    status = Column(Enum('pending', 'running', 'completed', 'failed', name='workflow_status'), nullable=False)
    inputs = Column(JSON, nullable=False)
    outputs = Column(JSON)
    error = Column(String)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    
    # Relationships
    workflow = relationship('WorkflowDefinition', back_populates='runs', foreign_keys=[workflow_id])
    step_runs = relationship('WorkflowStepRun', back_populates='workflow_run', cascade='all, delete-orphan')
    
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
    """
    
    __tablename__ = 'workflow_step_runs'
    
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey('workflow_runs.id'), nullable=False)
    step_id = Column(String, nullable=False)
    mcp_id = Column(UUID(as_uuid=True), ForeignKey('mcps.id'), nullable=False)
    status = Column(Enum('pending', 'running', 'completed', 'failed', name='step_status'), nullable=False)
    inputs = Column(JSON, nullable=False)
    outputs = Column(JSON)
    error = Column(String)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    workflow_run = relationship('WorkflowRun', back_populates='step_runs', foreign_keys=[workflow_run_id])
    
    def __repr__(self) -> str:
        """
        String representation of step run.
        
        Returns:
            str: Step run representation
        """
        return f"<WorkflowStepRun(step={self.step_id}, status={self.status})>" 