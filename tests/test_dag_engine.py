"""Tests for the DAG workflow engine."""

import pytest
import asyncio
from datetime import datetime
from typing import List

from mcp.core.dag_engine import DAGWorkflowEngine, StepStatus, DAGStep
from mcp.core.workflow_engine import WorkflowStep, WorkflowExecutionResult
from mcp.schemas.workflow import WorkflowDefinition

@pytest.fixture
def sample_workflow() -> WorkflowDefinition:
    """Create a sample workflow for testing."""
    return WorkflowDefinition(
        id="test_workflow",
        name="Test Workflow",
        description="A test workflow",
        steps=[
            WorkflowStep(
                id="step1",
                name="Step 1",
                depends_on=[],
                config={}
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                depends_on=["step1"],
                config={}
            ),
            WorkflowStep(
                id="step3",
                name="Step 3",
                depends_on=["step1"],
                config={}
            ),
            WorkflowStep(
                id="step4",
                name="Step 4",
                depends_on=["step2", "step3"],
                config={}
            )
        ]
    )

@pytest.fixture
def cyclic_workflow() -> WorkflowDefinition:
    """Create a workflow with a cycle for testing."""
    return WorkflowDefinition(
        id="cyclic_workflow",
        name="Cyclic Workflow",
        description="A workflow with a cycle",
        steps=[
            WorkflowStep(
                id="step1",
                name="Step 1",
                depends_on=["step3"],
                config={}
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                depends_on=["step1"],
                config={}
            ),
            WorkflowStep(
                id="step3",
                name="Step 3",
                depends_on=["step2"],
                config={}
            )
        ]
    )

def test_build_dag(sample_workflow: WorkflowDefinition):
    """Test building a valid DAG."""
    engine = DAGWorkflowEngine()
    engine.build_dag(sample_workflow)
    
    # Verify step dependencies
    assert len(engine.steps) == 4
    assert engine.steps["step1"].dependencies == set()
    assert engine.steps["step2"].dependencies == {"step1"}
    assert engine.steps["step3"].dependencies == {"step1"}
    assert engine.steps["step4"].dependencies == {"step2", "step3"}

def test_cyclic_dag(cyclic_workflow: WorkflowDefinition):
    """Test handling of cyclic dependencies."""
    engine = DAGWorkflowEngine()
    with pytest.raises(ValueError, match="Invalid DAG: Contains cycles"):
        engine.build_dag(cyclic_workflow)

def test_execution_order(sample_workflow: WorkflowDefinition):
    """Test calculation of execution order."""
    engine = DAGWorkflowEngine()
    engine.build_dag(sample_workflow)
    
    # Verify execution order
    assert len(engine.execution_order) == 4
    assert engine.execution_order[0] == "step1"  # First step
    assert engine.execution_order[-1] == "step4"  # Last step
    assert "step2" in engine.execution_order
    assert "step3" in engine.execution_order

@pytest.mark.asyncio
async def test_execute_workflow(sample_workflow: WorkflowDefinition):
    """Test workflow execution."""
    engine = DAGWorkflowEngine()
    results = await engine.execute_workflow(sample_workflow)
    
    # Verify all steps were executed
    assert len(results) == 4
    assert all(result.success for result in results.values())
    
    # Verify execution status
    status = engine.get_execution_status()
    assert all(status[step_id] == StepStatus.COMPLETED for step_id in status)

@pytest.mark.asyncio
async def test_parallel_execution(sample_workflow: WorkflowDefinition):
    """Test parallel execution of independent steps."""
    engine = DAGWorkflowEngine()
    engine.max_parallel_steps = 2
    
    # Track execution times
    execution_times = {}
    
    async def mock_execute_step(step_id: str) -> WorkflowExecutionResult:
        start_time = datetime.now()
        await asyncio.sleep(0.1)  # Simulate work
        execution_times[step_id] = datetime.now() - start_time
        return WorkflowExecutionResult(success=True, output=f"Step {step_id} completed")
    
    # Replace execute_step with mock
    engine.execute_step = mock_execute_step
    
    await engine.execute_workflow(sample_workflow)
    
    # Verify parallel execution
    assert len(execution_times) == 4
    # Step 1 should complete first
    assert min(execution_times.items(), key=lambda x: x[1])[0] == "step1"
    # Steps 2 and 3 should run in parallel
    assert abs(execution_times["step2"].total_seconds() - 
              execution_times["step3"].total_seconds()) < 0.1

def test_get_step_dependencies(sample_workflow: WorkflowDefinition):
    """Test retrieving step dependencies."""
    engine = DAGWorkflowEngine()
    engine.build_dag(sample_workflow)
    
    # Test step1 dependencies
    deps, dependents = engine.get_step_dependencies("step1")
    assert deps == set()
    assert dependents == {"step2", "step3"}
    
    # Test step4 dependencies
    deps, dependents = engine.get_step_dependencies("step4")
    assert deps == {"step2", "step3"}
    assert dependents == set()

def test_invalid_step_id(sample_workflow: WorkflowDefinition):
    """Test handling of invalid step IDs."""
    engine = DAGWorkflowEngine()
    engine.build_dag(sample_workflow)
    
    with pytest.raises(ValueError, match="Step invalid_id not found in workflow"):
        engine.get_step_dependencies("invalid_id") 