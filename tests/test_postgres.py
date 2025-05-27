# from mcp.db.operations import DatabaseOperations
from mcp.db.operations import create_mcp, create_mcp_version, create_workflow
from mcp.db.models.mcp import MCP, MCPVersion
from mcp.db.models.workflow import WorkflowDefinition, WorkflowRun, WorkflowStepRun
from mcp.schemas.mcp import MCPType, MCPStatus
import uuid

def test_mcp_crud_and_relationships(test_db_session):
    # Create MCP
    mcp = create_mcp(test_db_session, name="Test MCP", type=MCPType.PYTHON_SCRIPT, description="desc", tags=["tag1"])
    assert mcp.id is not None
    # Read MCP
    fetched = test_db_session.query(MCP).filter_by(id=mcp.id).first()
    assert fetched.name == "Test MCP"
    # Update MCP
    fetched.name = "Updated MCP"
    test_db_session.commit()
    updated = test_db_session.query(MCP).filter_by(id=mcp.id).first()
    assert updated.name == "Updated MCP"
    # Create MCPVersion
    version = create_mcp_version(test_db_session, mcp_id=mcp.id, version="1.0.0", definition={"foo": "bar"}, status=MCPStatus.ACTIVE)
    assert version.id is not None
    # Relationship: MCP.versions
    mcp = test_db_session.query(MCP).filter_by(id=mcp.id).first()
    assert len(mcp.versions) >= 1
    # Delete MCPVersion
    test_db_session.delete(version)
    test_db_session.commit()
    assert test_db_session.query(MCPVersion).filter_by(id=version.id).first() is None
    # Delete MCP
    test_db_session.delete(mcp)
    test_db_session.commit()
    assert test_db_session.query(MCP).filter_by(id=mcp.id).first() is None

def test_workflow_crud_and_relationships(test_db_session):
    # Create WorkflowDefinition
    wf = create_workflow(
        test_db_session,
        name="Test Workflow",
        steps=[{"id": "step1", "type": "noop"}],
        input_schema={},
        output_schema={},
        description="desc",
        error_strategy="stop_on_error",
        execution_mode="sequential",
    )
    assert wf.id is not None
    # Read WorkflowDefinition
    fetched = test_db_session.query(WorkflowDefinition).filter_by(id=wf.id).first()
    assert fetched.name == "Test Workflow"
    # Update WorkflowDefinition
    fetched.name = "Updated Workflow"
    test_db_session.commit()
    updated = test_db_session.query(WorkflowDefinition).filter_by(id=wf.id).first()
    assert updated.name == "Updated Workflow"
    # Relationship: WorkflowDefinition.runs
    run = WorkflowRun(
        workflow_id=wf.id,
        status="PENDING",
        started_at=None,
        finished_at=None,
        inputs={},
        outputs={},
        error=None,
        created_at=None,
        updated_at=None,
    )
    test_db_session.add(run)
    test_db_session.commit()
    wf = test_db_session.query(WorkflowDefinition).filter_by(id=wf.id).first()
    assert len(wf.runs) >= 1
    # Add WorkflowStepRun
    step_run = WorkflowStepRun(
        workflow_run_id=run.id,
        step_id="step1",
        mcp_id=uuid.uuid4(),
        status="PENDING",
        inputs={},
        outputs={},
        error=None,
        started_at=None,
        finished_at=None,
        retry_count=0,
        created_at=None,
        updated_at=None,
        resource_usage={},
    )
    test_db_session.add(step_run)
    test_db_session.commit()
    run = test_db_session.query(WorkflowRun).filter_by(id=run.id).first()
    assert len(run.step_runs) >= 1
    # Delete WorkflowStepRun
    test_db_session.delete(step_run)
    test_db_session.commit()
    assert test_db_session.query(WorkflowStepRun).filter_by(id=step_run.id).first() is None
    # Delete WorkflowRun
    test_db_session.delete(run)
    test_db_session.commit()
    assert test_db_session.query(WorkflowRun).filter_by(id=run.id).first() is None
    # Delete WorkflowDefinition
    test_db_session.delete(wf)
    test_db_session.commit()
    assert test_db_session.query(WorkflowDefinition).filter_by(id=wf.id).first() is None
