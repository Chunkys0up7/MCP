import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class InputSourceType(str, Enum):
    """
    Enumerates the possible sources for an input value within a workflow step.
    - STATIC_VALUE: The input is a hardcoded, static value.
    - STEP_OUTPUT: The input comes from the output of a previous step in the same workflow.
    - WORKFLOW_INPUT: The input is provided when the workflow execution is initiated.
    """

    STATIC_VALUE = "static_value"
    STEP_OUTPUT = "step_output"
    WORKFLOW_INPUT = "workflow_input"


class WorkflowStepInput(BaseModel):
    """
    Defines the source and necessary details for an input parameter of an MCP
    when it's used as a step in a workflow.
    """

    source_type: InputSourceType = Field(..., description="The type of source for this input.")

    value: Optional[Any] = Field(
        default=None,
        description="The static value for the input. Required and must be set if source_type is STATIC_VALUE.",
    )
    source_step_id: Optional[str] = Field(
        default=None,
        description="The ID of the step from which to pull the output. Required if source_type is STEP_OUTPUT.",
    )
    source_output_name: Optional[str] = Field(
        default=None,
        description="The name of the output field from the source_step_id. Required if source_type is STEP_OUTPUT.",
    )
    workflow_input_key: Optional[str] = Field(
        default=None,
        description="The key referencing an input provided at the start of the workflow execution. Required if source_type is WORKFLOW_INPUT.",
    )

    # For Pydantic v2 compatibility (preferred)
    @model_validator(mode="after")
    def check_conditional_fields_v2(self) -> "WorkflowStepInput":
        """
        Validates that the correct fields are populated based on the source_type.
        This is the Pydantic v2 style using @model_validator.
        """
        if self.source_type == InputSourceType.STATIC_VALUE:
            if self.value is None:
                raise ValueError("For STATIC_VALUE source_type, 'value' must be provided.")
            # Optionally, ensure other fields are None if strict
            # if self.source_step_id is not None or self.source_output_name is not None or self.workflow_input_key is not None:
            #     raise ValueError("For STATIC_VALUE, only 'value' should be set.")
        elif self.source_type == InputSourceType.STEP_OUTPUT:
            if not self.source_step_id or not self.source_output_name:
                raise ValueError(
                    "For STEP_OUTPUT source_type, both 'source_step_id' and 'source_output_name' must be provided."
                )
            # Optionally, ensure other fields are None
            # if self.value is not None or self.workflow_input_key is not None:
            #     raise ValueError("For STEP_OUTPUT, only 'source_step_id' and 'source_output_name' should be set.")
        elif self.source_type == InputSourceType.WORKFLOW_INPUT:
            if not self.workflow_input_key:
                raise ValueError(
                    "For WORKFLOW_INPUT source_type, 'workflow_input_key' must be provided."
                )
            # Optionally, ensure other fields are None
            # if self.value is not None or self.source_step_id is not None or self.source_output_name is not None:
            #     raise ValueError("For WORKFLOW_INPUT, only 'workflow_input_key' should be set.")
        return self

    # # For Pydantic v1 compatibility (fallback if model_validator is not available)
    # # Pydantic v1 uses @root_validator. If Pydantic v2 is guaranteed, the above @model_validator is cleaner.
    # # This is a basic structure; Pydantic v1 root_validator might need `pre=True` for some cases
    # # or careful handling of `values` dict.
    # @validator('*', pre=True, always=True) # Generic validator to trigger root_validator logic if needed or use root_validator directly
    # @classmethod
    # def check_conditional_fields_v1_root(cls, values):
    #     """
    #     Validates that the correct fields are populated based on the source_type.
    #     This is the Pydantic v1 style using @root_validator (or a similar mechanism).
    #     Note: Pydantic v1's root_validator gets a dictionary of `values`.
    #     """
    #     source_type = values.get('source_type')
    #     value = values.get('value')
    #     source_step_id = values.get('source_step_id')
    #     source_output_name = values.get('source_output_name')
    #     workflow_input_key = values.get('workflow_input_key')

    #     if source_type == InputSourceType.STATIC_VALUE.value: # Enum value for comparison with dict
    #         if value is None:
    #             raise ValueError("For STATIC_VALUE source_type, 'value' must be provided.")
    #     elif source_type == InputSourceType.STEP_OUTPUT.value:
    #         if not source_step_id or not source_output_name:
    #             raise ValueError("For STEP_OUTPUT source_type, both 'source_step_id' and 'source_output_name' must be provided.")
    #     elif source_type == InputSourceType.WORKFLOW_INPUT.value:
    #         if not workflow_input_key:
    #             raise ValueError("For WORKFLOW_INPUT source_type, 'workflow_input_key' must be provided.")

    #     return values

    class Config:
        """Pydantic model configuration."""

        try:
            from pydantic import ConfigDict

            model_config = ConfigDict(from_attributes=True, use_enum_values=True)
        except ImportError:  # Fallback for Pydantic v1
            orm_mode = True
            use_enum_values = True


class WorkflowStep(BaseModel):
    """
    Represents a single step (an MCP execution) in a workflow.
    Each step involves running a specific MCP with defined inputs.
    """

    step_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this workflow step.",
    )
    mcp_id: str = Field(..., description="Identifier of the MCP to be executed in this step.")
    mcp_version_id: Optional[str] = Field(
        default=None,
        description="Optional identifier for a specific version of the MCP. If None, the latest version might be used.",
    )
    name: str = Field(
        ..., description="A user-defined, descriptive name for this step within the workflow."
    )
    inputs: Dict[str, WorkflowStepInput] = Field(
        default_factory=dict,
        description="A dictionary mapping the MCP's input parameter names to their WorkflowStepInput definitions, specifying how each input is sourced.",
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="List of step_ids that must complete before this step can start. For DAGs.",
    )
    # Consider adding:
    # description: Optional[str] = Field(default=None, description="Optional further description for this step.")


class ErrorHandlingConfig(BaseModel):
    """
    Configuration for how errors should be handled during workflow execution.
    Applies to the entire workflow, but could potentially be overridden at step level in future.
    """

    strategy: str = Field(
        default="Stop on Error",
        examples=["Stop on Error", "Retry with Backoff", "Fallback Chain"],
        description="The strategy to employ when an error occurs in a step.",
    )
    max_retries: Optional[int] = Field(
        default=None,
        ge=0,
        description="Maximum number of retry attempts if strategy is 'Retry with Backoff'. Must be >= 0.",
    )
    backoff_factor: Optional[float] = Field(
        default=None,
        ge=1.0,
        description="The factor by which the delay increases for each retry attempt if strategy is 'Retry with Backoff'. Must be >= 1.0.",
    )
    fallback_workflow_id: Optional[str] = Field(
        default=None,
        description="The ID of another workflow to execute if the 'Fallback Chain' strategy is chosen and an error occurs.",
    )


class WorkflowBase(BaseModel):
    """
    Base model for workflow configuration, containing common fields for creation and representation.
    """

    name: str = Field(..., description="The user-defined name of the workflow.")
    description: Optional[str] = Field(
        default=None, description="An optional detailed description of what the workflow does."
    )
    execution_mode: str = Field(
        default="sequential",
        examples=["sequential", "parallel"],
        description="Defines how the steps in the workflow are executed. 'sequential' means steps run one after another. 'parallel' (for future implementation) could mean steps run concurrently where possible based on dependencies.",
    )
    error_handling: ErrorHandlingConfig = Field(
        default_factory=ErrorHandlingConfig,
        description="Configuration for error handling within the workflow.",
    )
    # Consider adding:
    # version: str = Field(default="1.0.0", description="Semantic version of the workflow definition.")
    # tags: List[str] = Field(default_factory=list, description="Tags for categorizing or searching workflows.")


class WorkflowCreate(WorkflowBase):
    """
    Model for creating a new workflow. Includes the list of steps that make up the workflow.
    """

    steps: List[WorkflowStep] = Field(
        default_factory=list,
        description="An ordered list of steps that constitute the workflow. For sequential execution, order matters. For future parallel/DAG execution, dependencies would be specified within steps.",
    )


class Workflow(WorkflowBase):
    """
    Full representation of a workflow, including system-generated fields like ID and timestamps.
    This model is typically used when retrieving or representing an existing workflow.
    """

    workflow_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the workflow, generated by the system.",
    )
    steps: List[WorkflowStep] = Field(
        ..., description="The list of steps that define the workflow's operations."
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of when the workflow was created."
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of when the workflow was last updated.",
    )

    class Config:
        """Pydantic model configuration."""

        try:
            from pydantic import ConfigDict

            model_config = ConfigDict(from_attributes=True, use_enum_values=True)
        except ImportError:  # Fallback for Pydantic v1
            orm_mode = True
            use_enum_values = True


class WorkflowExecutionResult(BaseModel):
    """
    Model representing the outcome of a workflow execution.
    """

    workflow_id: str = Field(..., description="The ID of the workflow that was executed.")
    execution_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID for this specific execution instance of the workflow.",
    )
    status: str = Field(
        ...,
        examples=["PENDING", "RUNNING", "SUCCESS", "FAILED", "CANCELLED"],
        description="The overall status of the workflow execution.",
    )
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of when the workflow execution began.",
    )
    finished_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of when the workflow execution completed (either successfully or with failure).",
    )
    step_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="A list containing the results from each executed step. Each item in the list should ideally conform to a StepExecutionResult model (to be defined).",
    )
    final_outputs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="The final designated outputs of the workflow, if any. This could be an aggregation or specific step outputs.",
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if the workflow execution failed."
    )


# It would be good to also define a StepExecutionResult model:
# class StepExecutionResult(BaseModel):
#     step_id: str
#     mcp_id: str
#     status: str # e.g., "SUCCESS", "FAILED", "SKIPPED"
#     started_at: datetime
#     finished_at: Optional[datetime]
#     inputs_used: Dict[str, Any]
#     outputs_generated: Optional[Dict[str, Any]] # This could be the MCPResult.result
#     error: Optional[str]
#     logs: Optional[List[str]]


class WorkflowStepGantt(BaseModel):
    id: uuid.UUID
    step_id: str
    mcp_id: uuid.UUID
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    status: str
    # Optionally, add step_name if available in the future

    class Config:
        from_attributes = True
