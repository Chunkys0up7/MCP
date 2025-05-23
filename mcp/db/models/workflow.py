import uuid
from sqlalchemy import Column, String, Text, DateTime, func, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from ..base_models import Base  # Assuming Base is in base_models.py at mcp/db/

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    workflow_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    steps = Column(JSON, nullable=False)  # Stores the list of steps/nodes and edges

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<WorkflowDefinition(workflow_id='{self.workflow_id}', name='{self.name}')>"

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    run_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(PG_UUID(as_uuid=True), ForeignKey("workflow_definitions.workflow_id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True) # e.g., pending, running, completed, failed, cancelled
    
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True) # Nullable as it's set upon completion/failure
    
    inputs = Column(JSON, nullable=True) # Initial inputs to the workflow run
    outputs = Column(JSON, nullable=True) # Final outputs of the workflow run
    step_results = Column(JSON, nullable=True) # Detailed results/logs from each step
    error_message = Column(Text, nullable=True) # If the workflow run failed

    # Relationship to WorkflowDefinition (optional, but good for ORM-level access)
    # workflow = relationship("WorkflowDefinition", back_populates="runs") 
    # If you add this, you'd add a back_populates="workflow" to WorkflowDefinition if it had a `runs` relationship

    def __repr__(self):
        return f"<WorkflowRun(run_id='{self.run_id}', workflow_id='{self.workflow_id}', status='{self.status}')>" 