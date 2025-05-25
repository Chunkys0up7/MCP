from typing import List, Optional

from pydantic import BaseModel, Field, conint

from mcp.core.types import MCPType  # Assuming MCPType is defined here


class ArchitecturalConstraints(BaseModel):
    """
    Defines a set of architectural constraints that can be applied to
    workflow generation or execution. These constraints would typically
    originate from an MCD (Mission Context Definition) system.
    """

    allowed_mcp_types: Optional[List[MCPType]] = Field(
        default=None,
        description="If specified, only MCPs of these types are allowed in the workflow.",
    )
    prohibited_mcp_types: Optional[List[MCPType]] = Field(
        default=None,
        description="If specified, MCPs of these types are prohibited in the workflow.",
    )
    max_workflow_steps: Optional[conint(ge=1)] = Field(
        default=None, description="Maximum number of steps allowed in a workflow."
    )
    # Example: max_total_execution_time_seconds: Optional[conint(ge=1)] = None
    # Example: max_cost_usd: Optional[confloat(ge=0.0)] = None

    # Tag-based constraints
    required_tags_all_steps: Optional[List[str]] = Field(
        default=None,
        description="All steps in the workflow must use MCPs that possess ALL of these tags.",
    )
    prohibited_tags_any_step: Optional[List[str]] = Field(
        default=None,
        description="No step in the workflow can use MCPs that possess ANY of these tags.",
    )
    # Example: allow_only_mcp_ids: Optional[List[str]] = None # UUIDs of specific MCPs

    class Config:
        extra = "forbid"  # Ensure no unknown constraints are passed
        use_enum_values = False  # MODIFIED: To store MCPType enum members, not their string values


# Example Usage (for documentation or testing):
# constraints_example = ArchitecturalConstraints(
#     allowed_mcp_types=[MCPType.PYTHON_SCRIPT, MCPType.LLM_PROMPT],
#     max_workflow_steps=10,
#     required_tags_all_steps=["production-ready"]
# )
