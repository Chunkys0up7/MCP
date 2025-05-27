"""
Workflow Engine Module

This module provides the core workflow execution engine for the MCP system.
It handles the orchestration of workflow steps, manages data flow between steps,
and ensures proper error handling and result aggregation.

The engine supports:
1. Sequential and parallel execution modes
2. Dynamic MCP loading from the database
3. Input resolution from various sources (static values, workflow inputs, step outputs)
4. Error handling with configurable strategies
5. Architectural constraint validation
6. Comprehensive logging and monitoring
7. DAG optimization and parallel execution

Example usage:
    ```python
    # Initialize the engine with a database session
    engine = WorkflowEngine(db_session=db, constraints=arch_constraints)

    # Execute a workflow
    result = await engine.run_workflow(workflow, initial_inputs={
        "param1": "value1",
        "param2": "value2"
    })

    # Check the result
    if result.status == "SUCCESS":
        print(f"Workflow completed successfully. Outputs: {result.final_outputs}")
    else:
        print(f"Workflow failed: {result.error_message}")
    ```
"""

import asyncio
import logging
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# ADD: Import Session for type hinting
from sqlalchemy.orm import Session

# ADD: Import registry functions
from mcp.core import \
    registry  # Assuming registry.py is in the same directory or mcp.core is a package
from mcp.core.dag import DAGOptimizer
# ADD: Import MCP model for type hinting
from mcp.db.models import MCP as MCPModel
# ADD: Import ArchitecturalConstraints
from mcp.schemas.mcd_constraints import ArchitecturalConstraints
from mcp.schemas.workflow import (InputSourceType, Workflow,
                                  WorkflowExecutionResult, WorkflowStep,
                                  WorkflowStepInput)

# Placeholder for a more detailed StepExecutionResult model
# from mcp.schemas.workflow import StepExecutionResult


logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Orchestrates the execution of defined workflows, managing step-by-step processing,
    data flow between steps, error handling, and result aggregation.

    The engine supports:
    - Sequential and parallel execution modes
    - Dynamic MCP loading from the database
    - Input resolution from various sources
    - Error handling with configurable strategies
    - Architectural constraint validation
    - DAG optimization and parallel execution

    Attributes:
        db_session (Session): The SQLAlchemy database session for MCP loading.
        constraints (Optional[ArchitecturalConstraints]): Architectural constraints for workflow validation.

    Example:
        ```python
        # Create a workflow with two steps
        workflow = Workflow(
            name="Test Workflow",
            steps=[
                WorkflowStep(
                    name="Step 1",
                    mcp_id="mcp-1",
                    inputs={
                        "input1": WorkflowStepInput(
                            source_type=InputSourceType.WORKFLOW_INPUT,
                            workflow_input_key="param1"
                        )
                    }
                ),
                WorkflowStep(
                    name="Step 2",
                    mcp_id="mcp-2",
                    inputs={
                        "input2": WorkflowStepInput(
                            source_type=InputSourceType.STEP_OUTPUT,
                            source_step_id="step-1",
                            source_output_name="output1"
                        )
                    }
                )
            ]
        )

        # Execute the workflow
        engine = WorkflowEngine(db_session=db)
        result = await engine.run_workflow(workflow, initial_inputs={"param1": "value1"})
        ```
    """

    def __init__(
        self,
        db_session: Session,
        constraints: Optional[ArchitecturalConstraints] = None,
    ):
        """
        Initialize the WorkflowEngine.

        Args:
            db_session (Session): The SQLAlchemy database session for MCP loading.
            constraints (Optional[ArchitecturalConstraints]): Architectural constraints for workflow validation.

        Example:
            ```python
            # Initialize with constraints
            constraints = ArchitecturalConstraints(
                allowed_mcp_types=[MCPType.PYTHON_SCRIPT],
                max_workflow_steps=5
            )
            engine = WorkflowEngine(db_session=db, constraints=constraints)
            ```
        """
        self.db_session = db_session
        self.constraints = constraints
        self.dag_optimizer = DAGOptimizer()

    async def run_workflow(
        self, workflow: Workflow, initial_inputs: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow with the given inputs.

        This method orchestrates the execution of a workflow by:
        1. Validating the workflow against architectural constraints
        2. Building and optimizing the workflow DAG
        3. Executing steps in the configured mode (sequential/parallel)
        4. Managing data flow between steps
        5. Handling errors according to the workflow's error strategy
        6. Aggregating results and generating the final output

        Args:
            workflow (Workflow): The workflow definition to execute.
            initial_inputs (Optional[Dict[str, Any]]): Initial inputs for the workflow.

        Returns:
            WorkflowExecutionResult: The execution result containing:
                - status: "SUCCESS" or "FAILED"
                - step_results: List of results from each step
                - final_outputs: The final outputs of the workflow
                - error_message: Error message if the workflow failed

        Raises:
            ValueError: If the workflow fails validation against architectural constraints.
            RuntimeError: If there's an error during workflow execution.

        Example:
            ```python
            # Execute a workflow with inputs
            result = await engine.run_workflow(
                workflow,
                initial_inputs={
                    "param1": "value1",
                    "param2": "value2"
                }
            )

            # Check the result
            if result.status == "SUCCESS":
                print(f"Final outputs: {result.final_outputs}")
            else:
                print(f"Error: {result.error_message}")
            ```
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        logger.info(
            f"Starting workflow '{workflow.name}' (ID: {workflow.workflow_id}, Execution ID: {execution_id})"
        )

        try:
            if self.constraints:
                self._validate_workflow_against_constraints(workflow)

            # Build and validate the workflow DAG
            self.dag_optimizer.build_graph(workflow)

            # Check for cycles
            cycles = self.dag_optimizer.detect_cycles()
            if cycles:
                error_msg = f"Workflow contains cycles: {cycles}"
                logger.error(error_msg)
                return WorkflowExecutionResult(
                    workflow_id=workflow.workflow_id,
                    status="FAILED",
                    error_message=error_msg,
                    step_results=[],
                    final_outputs=None,
                )

            # Validate dependencies
            dependency_errors = self.dag_optimizer.validate_dependencies()
            if dependency_errors:
                error_msg = "Workflow has invalid dependencies:\n" + "\n".join(
                    dependency_errors
                )
                logger.error(error_msg)
                return WorkflowExecutionResult(
                    workflow_id=workflow.workflow_id,
                    status="FAILED",
                    error_message=error_msg,
                    step_results=[],
                    final_outputs=None,
                )

            if workflow.execution_mode == "sequential":
                return await self._execute_sequential_workflow(
                    workflow, initial_inputs, execution_id, start_time
                )
            elif workflow.execution_mode == "parallel":
                return await self._execute_parallel_workflow(
                    workflow, initial_inputs, execution_id, start_time
                )
            else:
                error_msg = f"Execution mode '{workflow.execution_mode}' not supported."
                logger.error(error_msg)
                return WorkflowExecutionResult(
                    workflow_id=workflow.workflow_id,
                    status="FAILED",
                    error_message=error_msg,
                    step_results=[],
                    final_outputs=None,
                )

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return WorkflowExecutionResult(
                workflow_id=workflow.workflow_id,
                status="FAILED",
                error_message=error_msg,
                step_results=[],
                final_outputs=None,
            )

    async def _execute_sequential_workflow(
        self,
        workflow: Workflow,
        initial_inputs: Optional[Dict[str, Any]],
        execution_id: str,
        start_time: datetime,
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow in sequential mode.

        This method executes workflow steps one after another, maintaining
        the workflow context and handling errors according to the workflow's
        error strategy.

        Args:
            workflow (Workflow): The workflow to execute.
            initial_inputs (Optional[Dict[str, Any]]): Initial inputs for the workflow.
            execution_id (str): Unique identifier for this execution.
            start_time (datetime): When the workflow started.

        Returns:
            WorkflowExecutionResult: The execution result containing:
                - status: "SUCCESS" or "FAILED"
                - step_results: List of results from each step
                - final_outputs: The final outputs of the workflow
                - error_message: Error message if the workflow failed

        Example:
            ```python
            # Execute a sequential workflow
            result = await engine._execute_sequential_workflow(
                workflow,
                initial_inputs={"param1": "value1"},
                execution_id="exec-123",
                start_time=datetime.utcnow()
            )
            ```
        """
        workflow_context = (
            {"workflow_initial_inputs": initial_inputs} if initial_inputs else {}
        )
        step_results: List[Dict[str, Any]] = []

        for step in workflow.steps:
            step_result = await self._execute_workflow_step(
                step, workflow_context, workflow.error_handling.strategy
            )
            step_results.append(step_result)

            if step_result["status"] == "FAILED":
                return WorkflowExecutionResult(
                    workflow_id=workflow.workflow_id,
                    status="FAILED",
                    error_message=step_result["error"],
                    step_results=step_results,
                    final_outputs=None,
                )

        # If we get here, all steps succeeded
        final_outputs = step_results[-1]["outputs_generated"] if step_results else None
        return WorkflowExecutionResult(
            workflow_id=workflow.workflow_id,
            status="SUCCESS",
            error_message=None,
            step_results=step_results,
            final_outputs=final_outputs,
        )

    async def _execute_parallel_workflow(
        self,
        workflow: Workflow,
        initial_inputs: Optional[Dict[str, Any]],
        execution_id: str,
        start_time: datetime,
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow in parallel mode.

        This method executes workflow steps in parallel where possible, based on the DAG optimization.
        Steps that can run in parallel are executed concurrently, while maintaining proper dependency order.

        Args:
            workflow (Workflow): The workflow to execute.
            initial_inputs (Optional[Dict[str, Any]]): Initial inputs for the workflow.
            execution_id (str): Unique identifier for this execution.
            start_time (datetime): When the workflow started.

        Returns:
            WorkflowExecutionResult: The execution result containing:
                - status: "SUCCESS" or "FAILED"
                - step_results: List of results from each step
                - final_outputs: The final outputs of the workflow
                - error_message: Error message if the workflow failed
        """
        workflow_context = (
            {"workflow_initial_inputs": initial_inputs} if initial_inputs else {}
        )
        step_results: List[Dict[str, Any]] = []

        # Get parallel execution groups
        execution_groups = self.dag_optimizer.optimize_parallel_execution()

        for group in execution_groups:
            # Execute steps in this group in parallel
            group_tasks = []
            for step_id in group:
                step = next(s for s in workflow.steps if s.step_id == step_id)
                task = self._execute_workflow_step(
                    step, workflow_context, workflow.error_handling.strategy
                )
                group_tasks.append(task)

            # Wait for all steps in the group to complete
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)

            # Process results
            for result in group_results:
                if isinstance(result, Exception):
                    error_msg = f"Step execution failed: {str(result)}"
                    logger.error(error_msg)
                    return WorkflowExecutionResult(
                        workflow_id=workflow.workflow_id,
                        status="FAILED",
                        error_message=error_msg,
                        step_results=step_results,
                        final_outputs=None,
                    )
                if not isinstance(result, dict):
                    error_msg = f"Step execution returned non-dict result: {result}"
                    logger.error(error_msg)
                    return WorkflowExecutionResult(
                        workflow_id=workflow.workflow_id,
                        status="FAILED",
                        error_message=error_msg,
                        step_results=step_results,
                        final_outputs=None,
                    )
                step_results.append(result)
                if result["status"] == "FAILED":
                    return WorkflowExecutionResult(
                        workflow_id=workflow.workflow_id,
                        status="FAILED",
                        error_message=result["error"],
                        step_results=step_results,
                        final_outputs=None,
                    )
                workflow_context[result["step_id"]] = {
                    "outputs": result["outputs_generated"]
                }

        # If we get here, all steps succeeded
        final_outputs = step_results[-1]["outputs_generated"] if step_results else None
        return WorkflowExecutionResult(
            workflow_id=workflow.workflow_id,
            status="SUCCESS",
            error_message=None,
            step_results=step_results,
            final_outputs=final_outputs,
        )

    async def _execute_workflow_step(
        self, step: WorkflowStep, workflow_context: Dict[str, Any], error_strategy: str
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step.

        This method handles the execution of an individual workflow step by:
        1. Resolving the step's inputs from the workflow context
        2. Loading and instantiating the required MCP
        3. Executing the MCP with the resolved inputs
        4. Handling any errors that occur during execution
        5. Storing the step's results in the workflow context

        Args:
            step (WorkflowStep): The step to execute.
            workflow_context (Dict[str, Any]): Current workflow context containing:
                - workflow_initial_inputs: Initial inputs for the workflow
                - step_id: Outputs from previously executed steps
            error_strategy (str): How to handle errors (e.g., "stop_on_error", "continue").

        Returns:
            Dict[str, Any]: Step execution result containing:
                - step_id: ID of the executed step
                - mcp_id: ID of the MCP used
                - name: Name of the step
                - status: "SUCCESS" or "FAILED"
                - started_at: When the step started
                - finished_at: When the step finished
                - inputs_used: Inputs used for execution
                - outputs_generated: Outputs generated by the step
                - error: Error message if the step failed

        Example:
            ```python
            # Execute a workflow step
            result = await engine._execute_workflow_step(
                step,
                workflow_context={
                    "workflow_initial_inputs": {"param1": "value1"},
                    "step-1": {"outputs": {"output1": "value2"}}
                },
                error_strategy="stop_on_error"
            )
            ```
        """
        step_start_time = datetime.utcnow()
        logger.info(
            f"Executing step '{step.name}' (ID: {step.step_id}, MCP: {step.mcp_id})"
        )

        try:
            resolved_inputs = self._resolve_step_inputs(step, workflow_context)
            logger.debug(f"Resolved inputs for step '{step.name}': {resolved_inputs}")

            mcp_instance = registry.get_mcp_instance_from_db(
                db=self.db_session,
                mcp_id_str=step.mcp_id,
                mcp_version_str=step.mcp_version_id,
            )

            if not mcp_instance:
                raise ValueError(
                    f"MCP instance for ID '{step.mcp_id}' "
                    f"(Version: {step.mcp_version_id or 'latest'}) not found or failed to instantiate."
                )

            mcp_result = await mcp_instance.execute(resolved_inputs)

            if mcp_result.get("success"):
                workflow_context[step.step_id] = {"outputs": mcp_result.get("result")}
                return {
                    "step_id": step.step_id,
                    "mcp_id": step.mcp_id,
                    "name": step.name,
                    "status": "SUCCESS",
                    "started_at": step_start_time.isoformat(),
                    "finished_at": datetime.utcnow().isoformat(),
                    "inputs_used": resolved_inputs,
                    "outputs_generated": mcp_result.get("result"),
                    "error": None,
                }
            else:
                error_msg = mcp_result.get(
                    "error", "Unknown error during MCP execution."
                )
                logger.error(f"Step '{step.name}' failed: {error_msg}")
                return {
                    "step_id": step.step_id,
                    "mcp_id": step.mcp_id,
                    "name": step.name,
                    "status": "FAILED",
                    "started_at": step_start_time.isoformat(),
                    "finished_at": datetime.utcnow().isoformat(),
                    "inputs_used": resolved_inputs,
                    "outputs_generated": None,
                    "error": error_msg,
                }

        except Exception as e:
            error_msg = f"Error during step '{step.name}' execution: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return {
                "step_id": step.step_id,
                "mcp_id": step.mcp_id,
                "name": step.name,
                "status": "FAILED",
                "started_at": step_start_time.isoformat(),
                "finished_at": datetime.utcnow().isoformat(),
                "inputs_used": (
                    resolved_inputs if "resolved_inputs" in locals() else None
                ),
                "outputs_generated": None,
                "error": error_msg,
            }

    def _validate_workflow_against_constraints(self, workflow: Workflow) -> None:
        """
        Validates the workflow definition against the architectural constraints
        provided to the engine.

        This method checks:
        1. Maximum number of steps
        2. Allowed/prohibited MCP types
        3. Required/prohibited tags
        4. Other architectural constraints

        Args:
            workflow (Workflow): The workflow to validate.

        Raises:
            ValueError: If any constraint is violated.

        Example:
            ```python
            # Validate a workflow
            try:
                engine._validate_workflow_against_constraints(workflow)
                print("Workflow passed validation")
            except ValueError as e:
                print(f"Validation failed: {e}")
            ```
        """
        if (
            not self.constraints
        ):  # Should not happen if called correctly, but good practice
            return

        print(
            f"Validating workflow '{workflow.name}' against architectural constraints."
        )

        # Check max_workflow_steps
        if self.constraints.max_workflow_steps is not None:
            if len(workflow.steps) > self.constraints.max_workflow_steps:
                raise ValueError(
                    f"Workflow validation failed: Number of steps ({len(workflow.steps)}) "
                    f"exceeds maximum allowed ({self.constraints.max_workflow_steps})."
                )

        for step in workflow.steps:
            # Fetch MCP definition for type and tag checking
            # We use load_mcp_definition_from_db which returns the SQLAlchemy model
            mcp_def: Optional[MCPModel] = registry.load_mcp_definition_from_db(
                db=self.db_session, mcp_id_str=step.mcp_id
            )
            if not mcp_def:
                raise ValueError(
                    f"Workflow validation failed: MCP definition for ID '{step.mcp_id}' "
                    f"in step '{step.name}' not found."
                )

            mcp_type_str = mcp_def.type  # This is a string from the DB model
            mcp_tags: List[str] = (
                mcp_def.tags if mcp_def.tags else []
            )  # Tags stored as JSON in DB, expect list

            # Check allowed_mcp_types
            if self.constraints.allowed_mcp_types:
                # The constraint stores MCPType enum members. Their .value gives the string.
                # mcp_type_str is already the string value from the DB model.
                allowed_type_values = [
                    mcp_enum_member.value
                    for mcp_enum_member in self.constraints.allowed_mcp_types
                ]
                if mcp_type_str not in allowed_type_values:
                    raise ValueError(
                        f"Workflow validation failed: MCP type '{mcp_type_str}' for step '{step.name}' (MCP ID: {step.mcp_id}) "
                        f"is not in the list of allowed types: {allowed_type_values}."
                    )

            # Check prohibited_mcp_types
            if self.constraints.prohibited_mcp_types:
                prohibited_type_values = [
                    mcp_enum_member.value
                    for mcp_enum_member in self.constraints.prohibited_mcp_types
                ]
                if mcp_type_str in prohibited_type_values:
                    raise ValueError(
                        f"Workflow validation failed: MCP type '{mcp_type_str}' for step '{step.name}' (MCP ID: {step.mcp_id}) "
                        f"is in the list of prohibited types: {prohibited_type_values}."
                    )

            # Check required_tags_all_steps
            if self.constraints.required_tags_all_steps:
                for req_tag in self.constraints.required_tags_all_steps:
                    if req_tag not in mcp_tags:
                        raise ValueError(
                            f"Workflow validation failed: MCP for step '{step.name}' (ID: {step.mcp_id}) "
                            f"is missing required tag '{req_tag}'. Required: {self.constraints.required_tags_all_steps}. Present: {mcp_tags}"
                        )

            # Check prohibited_tags_any_step
            if self.constraints.prohibited_tags_any_step:
                for pro_tag in self.constraints.prohibited_tags_any_step:
                    if pro_tag in mcp_tags:
                        raise ValueError(
                            f"Workflow validation failed: MCP for step '{step.name}' (ID: {step.mcp_id}) "
                            f"has prohibited tag '{pro_tag}'. Prohibited: {self.constraints.prohibited_tags_any_step}. Present: {mcp_tags}"
                        )

        print(f"Workflow '{workflow.name}' passed architectural constraint validation.")

    def _resolve_step_inputs(
        self, step: WorkflowStep, workflow_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolves the actual input values for an MCP step based on its input definitions
        and the current workflow context.

        This method handles three types of input sources:
        1. STATIC_VALUE: A constant value defined in the workflow
        2. WORKFLOW_INPUT: A value from the workflow's initial inputs
        3. STEP_OUTPUT: A value from a previously executed step's output

        Args:
            step (WorkflowStep): The workflow step for which to resolve inputs.
            workflow_context (Dict[str, Any]): The current context of the workflow execution:
                {
                    "workflow_initial_inputs": { "input1": "value1", ... },
                    "step_id_1": { "outputs": { "output_A": "dataA" } },
                    "step_id_2": { "outputs": { "output_B": "dataB" } },
                    ...
                }

        Returns:
            Dict[str, Any]: A dictionary where keys are the MCP's expected input parameter names
                            and values are the resolved actual input values.

        Raises:
            ValueError: If an input cannot be resolved (e.g., missing source step output,
                        missing workflow input, or invalid configuration).

        Example:
            ```python
            # Resolve inputs for a step
            inputs = engine._resolve_step_inputs(
                step,
                workflow_context={
                    "workflow_initial_inputs": {"param1": "value1"},
                    "step-1": {"outputs": {"output1": "value2"}}
                }
            )
            ```
        """
        resolved_inputs: Dict[str, Any] = {}
        for mcp_input_name, step_input_config in step.inputs.items():
            # Ensure step_input_config is a WorkflowStepInput instance.
            # If step.inputs is already Dict[str, WorkflowStepInput], this is fine.
            # If step.inputs is Dict[str, dict], then this converts dict to WorkflowStepInput.
            if isinstance(step_input_config, dict):
                step_input_config_typed = WorkflowStepInput(**step_input_config)
            elif isinstance(step_input_config, WorkflowStepInput):
                step_input_config_typed = step_input_config  # Already correct type
            else:
                # Fallback or error if it's neither (shouldn't happen with Pydantic)
                raise TypeError(
                    f"Unexpected type for step_input_config: {type(step_input_config)}"
                )

            if step_input_config_typed.source_type == InputSourceType.STATIC_VALUE:
                resolved_inputs[mcp_input_name] = step_input_config_typed.value

            elif step_input_config_typed.source_type == InputSourceType.WORKFLOW_INPUT:
                if not step_input_config_typed.workflow_input_key:
                    raise ValueError(
                        f"Input '{mcp_input_name}' for step '{step.name}' is type WORKFLOW_INPUT but 'workflow_input_key' is not defined."
                    )

                initial_inputs_from_ctx = workflow_context.get(
                    "workflow_initial_inputs", {}
                )

                if (
                    step_input_config_typed.workflow_input_key
                    not in initial_inputs_from_ctx
                ):
                    raise ValueError(
                        f"Workflow input key '{step_input_config_typed.workflow_input_key}' not found for step '{step.name}', input '{mcp_input_name}'. Available: {list(initial_inputs_from_ctx.keys())}"
                    )
                resolved_inputs[mcp_input_name] = initial_inputs_from_ctx[
                    step_input_config_typed.workflow_input_key
                ]

            elif step_input_config_typed.source_type == InputSourceType.STEP_OUTPUT:
                if (
                    not step_input_config_typed.source_step_id
                    or not step_input_config_typed.source_output_name
                ):
                    raise ValueError(
                        f"Input '{mcp_input_name}' for step '{step.name}' is type STEP_OUTPUT but 'source_step_id' or 'source_output_name' is not defined."
                    )

                source_step_output_data = workflow_context.get(
                    step_input_config_typed.source_step_id
                )
                if (
                    not source_step_output_data
                    or "outputs" not in source_step_output_data
                ):
                    raise ValueError(
                        f"Output data for source step ID '{step_input_config_typed.source_step_id}' not found in workflow context for step '{step.name}', input '{mcp_input_name}'. Context keys: {list(workflow_context.keys())}"
                    )

                source_outputs = source_step_output_data["outputs"]
                if (
                    not isinstance(source_outputs, dict)
                    or step_input_config_typed.source_output_name not in source_outputs
                ):
                    raise ValueError(
                        f"Output name '{step_input_config_typed.source_output_name}' not found in outputs of source step '{step_input_config_typed.source_step_id}' for step '{step.name}', input '{mcp_input_name}'. Available outputs: {list(source_outputs.keys()) if isinstance(source_outputs, dict) else 'N/A'}"
                    )
                resolved_inputs[mcp_input_name] = source_outputs[
                    step_input_config_typed.source_output_name
                ]

            else:
                # This should not happen if Pydantic validation on source_type (Enum) is working
                raise ValueError(
                    f"Unsupported source_type '{step_input_config_typed.source_type}' for input '{mcp_input_name}' in step '{step.name}'."
                )

        return resolved_inputs


# To use this engine in an API endpoint (e.g., in mcp/api/routers/workflows.py):
# from mcp.core.workflow_engine import WorkflowEngine
# from mcp.api.main import mcp_server_registry # Assuming direct access or passed via Depends
#
# engine = WorkflowEngine(mcp_server_registry=mcp_server_registry)
# execution_result = await engine.run_workflow(workflow_to_execute, initial_inputs)
# return execution_result
