from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback
import uuid # ADDED

from mcp.schemas.workflow import (
    Workflow, 
    WorkflowStep, 
    WorkflowStepInput, 
    InputSourceType, 
    WorkflowExecutionResult
)

# Placeholder for a more detailed StepExecutionResult model
# from mcp.schemas.workflow import StepExecutionResult 

# ADD: Import Session for type hinting
from sqlalchemy.orm import Session
# ADD: Import registry functions
from mcp.core import registry # Assuming registry.py is in the same directory or mcp.core is a package

class WorkflowEngine:
    """
    Orchestrates the execution of a defined workflow, managing step-by-step processing,
    data flow between steps, error handling, and result aggregation.
    """

    def __init__(self, db_session: Session): # MODIFIED: Accept db_session
        """
        Initializes the WorkflowEngine.

        Args:
            db_session (Session): The SQLAlchemy database session.
        """
        self.db_session = db_session # MODIFIED: Store db_session
        # self.mcp_server_registry = mcp_server_registry # REMOVED

    async def run_workflow(
        self, 
        workflow: Workflow, 
        initial_inputs: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecutionResult:
        """
        Executes the given workflow.

        Args:
            workflow (Workflow): The workflow definition to execute.
            initial_inputs (Optional[Dict[str, Any]]): 
                A dictionary of inputs provided at the start of the workflow execution.
                These can be referenced by steps using `InputSourceType.WORKFLOW_INPUT`.

        Returns:
            WorkflowExecutionResult: An object detailing the outcome of the workflow execution,
                                     including status, step results, and any final outputs or errors.
        """
        execution_id = str(uuid.uuid4()) # Generate a unique ID for this execution run
        start_time = datetime.utcnow()
        overall_status = "RUNNING" # Initial status
        step_results_log: List[Dict[str, Any]] = [] # To store results of each step
        workflow_context: Dict[str, Any] = {} # Stores outputs of completed steps, keyed by step_id
        final_workflow_outputs: Optional[Dict[str, Any]] = None
        workflow_error_message: Optional[str] = None

        if initial_inputs:
            workflow_context["workflow_initial_inputs"] = initial_inputs

        print(f"[{start_time}] Starting workflow '{workflow.name}' (ID: {workflow.workflow_id}, Execution ID: {execution_id})")

        try:
            if workflow.execution_mode == "sequential":
                for step in workflow.steps:
                    print(f"  Executing step '{step.name}' (ID: {step.step_id}, MCP: {step.mcp_id})")
                    step_start_time = datetime.utcnow()
                    step_status = "FAILED" # Default to FAILED
                    step_output_data: Optional[Dict[str, Any]] = None
                    step_error: Optional[str] = None
                    resolved_inputs: Dict[str, Any] = {}

                    try:
                        # 1. Resolve Inputs for the current step
                        resolved_inputs = self._resolve_step_inputs(step, workflow_context)
                        print(f"    Resolved inputs for step '{step.name}': {resolved_inputs}")

                        # 2. Get MCP Instance from DB
                        # MODIFIED: Use registry to get MCP instance
                        mcp_instance = registry.get_mcp_instance_from_db(
                            db=self.db_session, 
                            mcp_id_str=step.mcp_id, 
                            mcp_version_str=step.mcp_version_id # Pass the version from the step
                        )
                        
                        if not mcp_instance:
                            raise ValueError(f"MCP instance for ID '{step.mcp_id}' (Version: {step.mcp_version_id or 'latest'}) not found or failed to instantiate.")
                        
                        # Old way:
                        # mcp_data = self.mcp_server_registry.get(step.mcp_id)
                        # if not mcp_data or not mcp_data.get("instance"):
                        #     raise ValueError(f"MCP instance for ID '{step.mcp_id}' not found or not executable.")
                        # mcp_instance: BaseMCPServer = mcp_data["instance"]

                        # 3. Execute MCP
                        # Assuming mcp_instance.execute returns a dict like MCPResult Pydantic model
                        # (or at least fields: success, result, error, stdout, stderr)
                        mcp_execution_result: Dict[str, Any] = await mcp_instance.execute(resolved_inputs)
                        
                        if mcp_execution_result.get("success"):
                            step_status = "SUCCESS"
                            step_output_data = mcp_execution_result.get("result")
                            # Store step output in workflow_context for subsequent steps
                            workflow_context[step.step_id] = {"outputs": step_output_data}
                            print(f"    Step '{step.name}' completed successfully. Output: {step_output_data}")
                        else:
                            step_error = mcp_execution_result.get("error", "Unknown error during MCP execution.")
                            print(f"    Step '{step.name}' failed. Error: {step_error}")
                            # Apply error handling strategy
                            if workflow.error_handling.strategy == "Stop on Error":
                                overall_status = "FAILED"
                                workflow_error_message = f"Workflow failed at step '{step.name}': {step_error}"
                                break # Stop workflow execution
                            # TODO: Implement other strategies like "Retry with Backoff", "Fallback Chain"
                            # For Retry: a loop here with delays (asyncio.sleep)
                            # For Fallback: trigger another workflow (would need another run_workflow call)

                    except Exception as e:
                        step_error = f"Error during step '{step.name}' execution: {str(e)}\n{traceback.format_exc()}"
                        print(f"    {step_error}")
                        if workflow.error_handling.strategy == "Stop on Error":
                            overall_status = "FAILED"
                            workflow_error_message = step_error
                            break 
                        # Handle other strategies if applicable
                    
                    finally:
                        step_end_time = datetime.utcnow()
                        step_results_log.append({
                            "step_id": step.step_id,
                            "mcp_id": step.mcp_id,
                            "name": step.name,
                            "status": step_status,
                            "started_at": step_start_time.isoformat(),
                            "finished_at": step_end_time.isoformat(),
                            "inputs_used": resolved_inputs, # For debugging and auditing
                            "outputs_generated": step_output_data,
                            "error": step_error
                        })
                        if overall_status == "FAILED": # If a step caused workflow to fail and stop
                            break
            else:
                # TODO: Implement parallel execution logic if mode is "parallel"
                # This would involve graph traversal (based on step.depends_on) and asyncio.gather for concurrent tasks.
                overall_status = "FAILED"
                workflow_error_message = f"Execution mode '{workflow.execution_mode}' not yet implemented."
                print(workflow_error_message)

            if overall_status != "FAILED":
                overall_status = "SUCCESS"
                # TODO: Define how final_workflow_outputs are determined. 
                # E.g., output of the last step, or a specifically designated set of outputs from various steps.
                # For now, let's assume the output of the last successful step if sequential.
                if workflow.steps and step_results_log and step_results_log[-1]["status"] == "SUCCESS":
                    final_workflow_outputs = step_results_log[-1]["outputs_generated"]
                print(f"Workflow '{workflow.name}' completed successfully.")

        except Exception as e:
            overall_status = "FAILED"
            workflow_error_message = f"Critical error during workflow execution: {str(e)}\n{traceback.format_exc()}"
            print(workflow_error_message)
        
        finally:
            end_time = datetime.utcnow()
            print(f"[{end_time}] Workflow '{workflow.name}' finished with status: {overall_status}")
            return WorkflowExecutionResult(
                workflow_id=workflow.workflow_id,
                execution_id=execution_id,
                status=overall_status,
                started_at=start_time,
                finished_at=end_time,
                step_results=step_results_log,
                final_outputs=final_workflow_outputs,
                error_message=workflow_error_message
            )

    def _resolve_step_inputs(
        self, 
        step: WorkflowStep, 
        workflow_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolves the actual input values for an MCP step based on its input definitions
        and the current workflow context (initial inputs, outputs of previous steps).

        Args:
            step (WorkflowStep): The workflow step for which to resolve inputs.
            workflow_context (Dict[str, Any]): 
                The current context of the workflow execution, containing initial inputs 
                and outputs from already executed steps.
                Example structure:
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
        """
        resolved_inputs: Dict[str, Any] = {}
        for mcp_input_name, step_input_config in step.inputs.items():
            # Ensure step_input_config is a WorkflowStepInput instance.
            # If step.inputs is already Dict[str, WorkflowStepInput], this is fine.
            # If step.inputs is Dict[str, dict], then this converts dict to WorkflowStepInput.
            if isinstance(step_input_config, dict):
                step_input_config_typed = WorkflowStepInput(**step_input_config)
            elif isinstance(step_input_config, WorkflowStepInput):
                step_input_config_typed = step_input_config # Already correct type
            else:
                # Fallback or error if it's neither (shouldn't happen with Pydantic)
                raise TypeError(f"Unexpected type for step_input_config: {type(step_input_config)}")

            if step_input_config_typed.source_type == InputSourceType.STATIC_VALUE:
                resolved_inputs[mcp_input_name] = step_input_config_typed.value
            
            elif step_input_config_typed.source_type == InputSourceType.WORKFLOW_INPUT:
                if not step_input_config_typed.workflow_input_key:
                    raise ValueError(f"Input '{mcp_input_name}' for step '{step.name}' is type WORKFLOW_INPUT but 'workflow_input_key' is not defined.")
                
                initial_inputs_from_ctx = workflow_context.get("workflow_initial_inputs", {})
                
                if step_input_config_typed.workflow_input_key not in initial_inputs_from_ctx:
                    raise ValueError(f"Workflow input key '{step_input_config_typed.workflow_input_key}' not found for step '{step.name}', input '{mcp_input_name}'. Available: {list(initial_inputs_from_ctx.keys())}")
                resolved_inputs[mcp_input_name] = initial_inputs_from_ctx[step_input_config_typed.workflow_input_key]
            
            elif step_input_config_typed.source_type == InputSourceType.STEP_OUTPUT:
                if not step_input_config_typed.source_step_id or not step_input_config_typed.source_output_name:
                    raise ValueError(f"Input '{mcp_input_name}' for step '{step.name}' is type STEP_OUTPUT but 'source_step_id' or 'source_output_name' is not defined.")
                
                source_step_output_data = workflow_context.get(step_input_config_typed.source_step_id)
                if not source_step_output_data or "outputs" not in source_step_output_data:
                    raise ValueError(f"Output data for source step ID '{step_input_config_typed.source_step_id}' not found in workflow context for step '{step.name}', input '{mcp_input_name}'. Context keys: {list(workflow_context.keys())}")
                
                source_outputs = source_step_output_data["outputs"]
                if not isinstance(source_outputs, dict) or step_input_config_typed.source_output_name not in source_outputs:
                    raise ValueError(f"Output name '{step_input_config_typed.source_output_name}' not found in outputs of source step '{step_input_config_typed.source_step_id}' for step '{step.name}', input '{mcp_input_name}'. Available outputs: {list(source_outputs.keys()) if isinstance(source_outputs, dict) else 'N/A'}")
                resolved_inputs[mcp_input_name] = source_outputs[step_input_config_typed.source_output_name]
            
            else:
                # This should not happen if Pydantic validation on source_type (Enum) is working
                raise ValueError(f"Unsupported source_type '{step_input_config_typed.source_type}' for input '{mcp_input_name}' in step '{step.name}'.")
        
        return resolved_inputs

# To use this engine in an API endpoint (e.g., in mcp/api/routers/workflows.py):
# from mcp.core.workflow_engine import WorkflowEngine
# from mcp.api.main import mcp_server_registry # Assuming direct access or passed via Depends
#
# engine = WorkflowEngine(mcp_server_registry=mcp_server_registry)
# execution_result = await engine.run_workflow(workflow_to_execute, initial_inputs)
# return execution_result 