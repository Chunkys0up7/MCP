from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from mcp.core.types import MCPType # MCPType enum and the Union of all config types


# --- MCP Version Schemas ---
class MCPVersionBase(BaseModel):
    version_str: str = Field(..., description="Semantic version string (e.g., \"1.0.0\", \"latest\") or a commit hash.")
    description: Optional[str] = Field(default=None, description="Optional description for this specific version.")
    config_snapshot: Dict[str, Any] = Field(..., description="A snapshot of the MCP's specific configuration for this version.")
    # manifest_hash: Optional[str] = Field(default=None, description="A hash of the version's manifest for integrity and uniqueness.")

class MCPVersionCreate(MCPVersionBase):
    mcp_id: uuid.UUID # Will be set by the system when creating a version for an existing MCP
    pass

class MCPVersionRead(MCPVersionBase):
    id: uuid.UUID
    mcp_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True

# --- MCP Schemas (Component Core) ---
class MCPBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="User-defined name for the MCP.")
    type: MCPType = Field(..., description="The type of the MCP.")
    description: Optional[str] = Field(default=None, max_length=500, description="Optional detailed description of the MCP.")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing and searching MCPs.")

class MCPCreate(MCPBase):
    # Configuration for the initial version will be part of this payload
    initial_config: Dict[str, Any] = Field(..., description="The configuration for the first version of this MCP.")
    initial_version_str: str = Field(default="0.1.0", description="Version string for the initial version.")
    initial_version_description: Optional[str] = Field(default=None, description="Description for the initial version.")

class MCPUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100, description="User-defined name for the MCP.")
    description: Optional[str] = Field(default=None, max_length=500, description="Optional detailed description of the MCP.")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorizing and searching MCPs.")

    class Config:
        from_attributes = True # Allow creating from ORM model if needed, though this is for input

class MCPRead(MCPBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # latest_version: Optional[MCPVersionRead] = None # Could be populated by a service
    # versions: List[MCPVersionRead] = Field(default_factory=list) # Could be populated by a service

    class Config:
        from_attributes = True
        use_enum_values = True


# --- API Specific Schemas (can reuse/compose from above) ---
class MCPDetail(MCPRead): # Inherits from MCPRead, effectively the same for now but can diverge
    """Detailed representation of an MCP (Component) for API responses, potentially with more info."""
    # Example: Add specific fields not in MCPRead if needed for API output
    # config: Dict[str, Any] # This was in the old MCPDetail, now config is version-specific.
                            # For GET /context/{id}, we might show the config of the *latest* version.
    latest_version_config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration of the latest version of this MCP.")
    latest_version_str: Optional[str] = Field(default=None, description="Version string of the latest version.")

# Request model for creating a new version for an existing MCP
class MCPNewVersionRequest(BaseModel):
    version_str: str = Field(..., description="The new version string (e.g., \"1.1.0\").")
    description: Optional[str] = Field(default=None, description="Description for this new version.")
    config_snapshot: Dict[str, Any] = Field(..., description="The full configuration snapshot for this new version.")
    # based_on_version_id: Optional[uuid.UUID] = Field(default=None, description="Optionally, the ID of the version this new one is based on.")


# For listing MCPs, we might want a more lightweight representation
class MCPListItem(MCPBase):
    id: uuid.UUID
    latest_version_str: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True 