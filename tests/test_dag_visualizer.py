"""Tests for the DAG visualizer component."""

import pytest
import os
from datetime import datetime, timedelta
from typing import List

from mcp.core.dag_engine import DAGWorkflowEngine, StepStatus
from mcp.core.workflow_engine import WorkflowStep, WorkflowExecutionResult
from mcp.db.models import WorkflowDefinition
from mcp.components.dag_visualizer import DAGVisualizer

@pytest.fixture
def sample_workflow() -> WorkflowDefinition:
    """Create a sample workflow for testing."""
    return WorkflowDefinition(
        id="test_workflow",
        name="Test Workflow",
        description="A test workflow",
        steps=[
            WorkflowStep(
                step_id="step1",
                name="Step 1",
                depends_on=[],
                config={},
                mcp_id="mcp1"
            ),
            WorkflowStep(
                step_id="step2",
                name="Step 2",
                depends_on=["step1"],
                config={},
                mcp_id="mcp2"
            ),
            WorkflowStep(
                step_id="step3",
                name="Step 3",
                depends_on=["step1"],
                config={},
                mcp_id="mcp3"
            ),
            WorkflowStep(
                step_id="step4",
                name="Step 4",
                depends_on=["step2", "step3"],
                config={},
                mcp_id="mcp4"
            )
        ]
    )

@pytest.fixture
def engine_with_execution(sample_workflow: WorkflowDefinition) -> DAGWorkflowEngine:
    """Create a DAG engine with simulated execution times."""
    engine = DAGWorkflowEngine()
    engine.build_dag(sample_workflow)
    
    # Simulate execution times
    base_time = datetime.now()
    for idx, (step_id, dag_step) in enumerate(engine.steps.items()):
        dag_step.start_time = base_time + timedelta(minutes=idx)
        dag_step.end_time = dag_step.start_time + timedelta(minutes=1)
        dag_step.status = StepStatus.COMPLETED
    
    return engine

def test_create_graph(engine_with_execution: DAGWorkflowEngine):
    """Test graph creation from DAG engine."""
    visualizer = DAGVisualizer()
    G = visualizer.create_graph(engine_with_execution)
    
    # Verify graph structure
    assert len(G.nodes) == 4
    assert len(G.edges) == 4
    
    # Verify node attributes
    for node in G.nodes:
        assert 'name' in G.nodes[node]
        assert 'status' in G.nodes[node]
        assert 'start_time' in G.nodes[node]
        assert 'end_time' in G.nodes[node]

def test_visualize(engine_with_execution: DAGWorkflowEngine, tmp_path):
    """Test DAG visualization."""
    visualizer = DAGVisualizer()
    output_path = tmp_path / "dag_visualization.png"
    
    # Test visualization with output
    visualizer.visualize(engine_with_execution, output_path=str(output_path), show=False)
    assert output_path.exists()
    
    # Test visualization without output
    visualizer.visualize(engine_with_execution, show=False)

def test_get_execution_times(engine_with_execution: DAGWorkflowEngine):
    """Test execution time retrieval."""
    visualizer = DAGVisualizer()
    times = visualizer.get_execution_times(engine_with_execution)
    
    assert len(times) == 4
    for step_id, (start_time, end_time) in times.items():
        assert isinstance(start_time, datetime)
        assert isinstance(end_time, datetime)
        assert end_time > start_time

def test_get_critical_path(engine_with_execution: DAGWorkflowEngine):
    """Test critical path calculation."""
    visualizer = DAGVisualizer()
    critical_path = visualizer.get_critical_path(engine_with_execution)
    
    # Verify critical path
    assert len(critical_path) > 0
    assert critical_path[0] == "step1"  # First step should be in critical path
    assert critical_path[-1] == "step4"  # Last step should be in critical path

def test_get_parallel_steps(engine_with_execution: DAGWorkflowEngine):
    """Test parallel step group calculation."""
    visualizer = DAGVisualizer()
    parallel_groups = visualizer.get_parallel_steps(engine_with_execution)
    
    # Verify parallel groups
    assert len(parallel_groups) > 0
    assert ["step1"] in parallel_groups  # First step should be alone
    assert set(["step2", "step3"]) in [set(group) for group in parallel_groups]  # Steps 2 and 3 should be parallel
    assert ["step4"] in parallel_groups  # Last step should be alone

def test_visualization_colors():
    """Test visualization color mapping."""
    visualizer = DAGVisualizer()
    
    # Verify color mapping for all statuses
    for status in StepStatus:
        assert status in visualizer.colors
        assert isinstance(visualizer.colors[status], str)

def test_invalid_engine():
    """Test handling of invalid engine state."""
    visualizer = DAGVisualizer()
    engine = DAGWorkflowEngine()
    
    # Test with empty engine
    G = visualizer.create_graph(engine)
    assert len(G.nodes) == 0
    assert len(G.edges) == 0
    
    # Test critical path with empty engine
    critical_path = visualizer.get_critical_path(engine)
    assert len(critical_path) == 0
    
    # Test parallel steps with empty engine
    parallel_groups = visualizer.get_parallel_steps(engine)
    assert len(parallel_groups) == 0 