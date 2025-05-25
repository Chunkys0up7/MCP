"""
DAG Workflow Engine for MCP

This module implements a Directed Acyclic Graph (DAG) based workflow engine
that supports parallel execution of workflow steps while maintaining dependencies.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from mcp.core.workflow_engine import WorkflowExecutionResult, WorkflowStep
from mcp.db.models import WorkflowDefinition

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a workflow step in the DAG."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGStep:
    """Represents a step in the DAG with its dependencies and status."""

    step: WorkflowStep
    dependencies: Set[str]  # IDs of steps this step depends on
    dependents: Set[str]  # IDs of steps that depend on this step
    status: StepStatus = StepStatus.PENDING
    result: Optional[WorkflowExecutionResult] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DAGWorkflowEngine:
    """Engine for executing workflows as DAGs with parallel execution support."""

    def __init__(self):
        self.steps: Dict[str, DAGStep] = {}
        self.execution_order: List[str] = []
        self.max_parallel_steps: int = 4  # Configurable parallel execution limit

    def build_dag(self, workflow: WorkflowDefinition) -> None:
        """
        Build the DAG from workflow definition.

        Args:
            workflow: The workflow definition to build the DAG from
        """
        self.steps.clear()
        self.execution_order.clear()

        # Create DAG steps
        for step in workflow.steps:
            depends_on = getattr(step, "depends_on", [])
            if depends_on is None:
                depends_on = []
            self.steps[step.step_id] = DAGStep(
                step=step, dependencies=set(depends_on), dependents=set()
            )

        # Build dependency graph
        for step_id, dag_step in self.steps.items():
            for dep_id in dag_step.dependencies:
                if dep_id in self.steps:
                    self.steps[dep_id].dependents.add(step_id)

        # Validate DAG
        if not self._validate_dag():
            raise ValueError("Invalid DAG: Contains cycles")

        # Calculate execution order
        self._calculate_execution_order()

    def _validate_dag(self) -> bool:
        """
        Validate that the DAG has no cycles.

        Returns:
            bool: True if DAG is valid (no cycles), False otherwise
        """
        visited = set()
        temp_visited = set()

        def visit(node_id: str) -> bool:
            if node_id in temp_visited:
                return False  # Cycle detected
            if node_id in visited:
                return True

            temp_visited.add(node_id)
            for dependent in self.steps[node_id].dependents:
                if not visit(dependent):
                    return False
            temp_visited.remove(node_id)
            visited.add(node_id)
            return True

        return all(visit(node_id) for node_id in self.steps)

    def _calculate_execution_order(self) -> None:
        """Calculate the topological order of steps for execution."""
        visited = set()
        temp_visited = set()

        def visit(node_id: str) -> None:
            if node_id in temp_visited:
                raise ValueError("Cycle detected in DAG")
            if node_id in visited:
                return

            temp_visited.add(node_id)
            for dependent in self.steps[node_id].dependents:
                visit(dependent)
            temp_visited.remove(node_id)
            visited.add(node_id)
            self.execution_order.append(node_id)

        for node_id in self.steps:
            if node_id not in visited:
                visit(node_id)

        self.execution_order.reverse()

    async def execute_step(self, step_id: str) -> WorkflowExecutionResult:
        """
        Execute a single step in the workflow.

        Args:
            step_id: ID of the step to execute

        Returns:
            WorkflowExecutionResult: Result of the step execution
        """
        dag_step = self.steps[step_id]
        dag_step.status = StepStatus.RUNNING
        dag_step.start_time = datetime.now()

        try:
            # Execute the step using the existing workflow engine
            result = await self._execute_workflow_step(dag_step.step)
            dag_step.status = StepStatus.COMPLETED
            dag_step.result = result
        except Exception as e:
            logger.error(f"Step {step_id} failed: {str(e)}")
            dag_step.status = StepStatus.FAILED
            result = WorkflowExecutionResult(success=False, error=str(e), output=None)
        finally:
            dag_step.end_time = datetime.now()

        return result

    async def _execute_workflow_step(self, step: WorkflowStep) -> WorkflowExecutionResult:
        """
        Execute a workflow step using the existing workflow engine.

        Args:
            step: The workflow step to execute

        Returns:
            WorkflowExecutionResult: Result of the step execution
        """
        # TODO: Implement actual step execution using the existing workflow engine
        # This is a placeholder that should be replaced with actual implementation
        return WorkflowExecutionResult(success=True, output="Step executed successfully")

    async def execute_workflow(
        self, workflow: WorkflowDefinition
    ) -> Dict[str, WorkflowExecutionResult]:
        """
        Execute the workflow as a DAG with parallel execution support.

        Args:
            workflow: The workflow definition to execute

        Returns:
            Dict[str, WorkflowExecutionResult]: Results of all step executions
        """
        self.build_dag(workflow)
        results = {}
        running_steps = set()
        completed_steps = set()

        while len(completed_steps) < len(self.steps):
            # Find steps that can be executed
            available_steps = [
                step_id
                for step_id in self.execution_order
                if step_id not in completed_steps
                and step_id not in running_steps
                and all(dep_id in completed_steps for dep_id in self.steps[step_id].dependencies)
            ]

            # Start new steps up to the parallel limit
            while available_steps and len(running_steps) < self.max_parallel_steps:
                step_id = available_steps.pop(0)
                running_steps.add(step_id)
                asyncio.create_task(
                    self._execute_and_track(step_id, results, running_steps, completed_steps)
                )

            # Wait for some steps to complete if we're at the limit
            if len(running_steps) >= self.max_parallel_steps:
                await asyncio.sleep(0.1)

        return results

    async def _execute_and_track(
        self,
        step_id: str,
        results: Dict[str, WorkflowExecutionResult],
        running_steps: Set[str],
        completed_steps: Set[str],
    ) -> None:
        """
        Execute a step and track its completion.

        Args:
            step_id: ID of the step to execute
            results: Dictionary to store results
            running_steps: Set of currently running steps
            completed_steps: Set of completed steps
        """
        try:
            result = await self.execute_step(step_id)
            results[step_id] = result
        finally:
            running_steps.remove(step_id)
            completed_steps.add(step_id)

    def get_execution_status(self) -> Dict[str, StepStatus]:
        """
        Get the current status of all steps in the workflow.

        Returns:
            Dict[str, StepStatus]: Mapping of step IDs to their current status
        """
        return {step_id: dag_step.status for step_id, dag_step in self.steps.items()}

    def get_step_dependencies(self, step_id: str) -> Tuple[Set[str], Set[str]]:
        """
        Get the dependencies and dependents of a step.

        Args:
            step_id: ID of the step to get dependencies for

        Returns:
            Tuple[Set[str], Set[str]]: Tuple of (dependencies, dependents)
        """
        if step_id not in self.steps:
            raise ValueError(f"Step {step_id} not found in workflow")
        return self.steps[step_id].dependencies, self.steps[step_id].dependents
