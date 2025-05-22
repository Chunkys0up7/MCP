import os
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from mcp.db.models import MCP, MCPVersion
from mcp.schemas.mcp import MCPCreate, MCPUpdate
import uuid

# Imports needed from mcp.core for MCP instantiation
from .base import BaseMCPServer
from .llm_prompt import LLMPromptMCP
from .jupyter_notebook import JupyterNotebookMCP
from .python_script import PythonScriptMCP
from .ai_assistant import AIAssistantMCP

from .types import (
    LLMPromptConfig,
    JupyterNotebookConfig,
    PythonScriptConfig,
    AIAssistantConfig,
    MCPType,
    MCPConfig as AllMCPConfigUnion # Union of all config types
)

# MCP server registry and persistence
# STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / ".mcp_data" # Adjusted path relative to this file
# STORAGE_DIR.mkdir(exist_ok=True)
# MCP_STORAGE_FILE = STORAGE_DIR / "mcp_storage.json"

# def save_mcp_servers(servers: Dict[str, Dict[str, Any]]): # Removed function
    # ... (content of function removed)

# Initialize the global registry
mcp_server_registry: Dict[str, Dict[str, Any]] = {} # Initialize as empty dict for now
# print(f"MCP Server Registry initialized with {len(mcp_server_registry)} servers from {MCP_STORAGE_FILE}") # Removed print
print(f"MCP Server Registry initialized as empty. DB loading pending.") # Placeholder print

def load_mcp_definition_from_db(db: Session, mcp_id_str: str) -> Optional[MCP]:
    """Loads a single MCP definition from the database by its ID."""
    try:
        mcp_uuid = uuid.UUID(mcp_id_str)
    except ValueError:
        # Invalid UUID format
        return None
    return db.query(MCP).filter(MCP.id == mcp_uuid).first()

def load_all_mcp_definitions_from_db(db: Session) -> List[MCP]:
    """Loads all MCP definitions from the database."""
    return db.query(MCP).all()

def save_mcp_definition_to_db(db: Session, mcp_data: MCPCreate) -> MCP:
    """Saves a new MCP definition and its initial version to the database."""
    db_mcp = MCP(
        name=mcp_data.name,
        type=mcp_data.type.value, # Use enum value
        description=mcp_data.description,
        tags=mcp_data.tags
    )
    # The MCP ID is generated upon instantiation if default=uuid.uuid4 is set in model

    db_initial_version = MCPVersion(
        mcp=db_mcp, # Associate with the MCP object
        version_str=mcp_data.initial_version_str,
        description=mcp_data.initial_version_description,
        config_snapshot=mcp_data.initial_config
    )
    
    # Add MCP first, so it gets an ID if not already set by default factory (though it should)
    db.add(db_mcp)
    # Then add version. Cascading might handle this, but explicit add is fine.
    db.add(db_initial_version)
    
    try:
        db.commit()
        db.refresh(db_mcp)
        # db.refresh(db_initial_version) # Optional: refresh if you need its generated fields immediately
    except Exception as e: # Catch potential DB errors
        db.rollback()
        # Consider logging the error e
        # Consider raising a custom exception or re-raising
        raise e # Re-raise for now, API layer can handle it
    return db_mcp

def update_mcp_definition_in_db(db: Session, mcp_id_str: str, mcp_data: MCPUpdate) -> Optional[MCP]:
    """Updates an existing MCP definition in the database."""
    try:
        mcp_uuid = uuid.UUID(mcp_id_str)
    except ValueError:
        return None

    db_mcp = db.query(MCP).filter(MCP.id == mcp_uuid).first()
    if not db_mcp:
        return None

    update_data = mcp_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mcp, key, value)
    
    try:
        db.commit()
        db.refresh(db_mcp)
    except Exception as e:
        db.rollback()
        raise e
    return db_mcp

def delete_mcp_definition_from_db(db: Session, mcp_id_str: str) -> bool:
    """Deletes an MCP definition from the database. 
    Note: MCPVersions associated with this MCP will also be deleted due to cascade settings.
    """
    try:
        mcp_uuid = uuid.UUID(mcp_id_str)
    except ValueError:
        return False # Invalid ID format

    db_mcp = db.query(MCP).filter(MCP.id == mcp_uuid).first()
    if not db_mcp:
        return False # MCP not found
    
    try:
        db.delete(db_mcp)
        db.commit()
    except Exception as e:
        db.rollback()
        # Log error e
        raise e # Or return False, depending on desired error handling
    return True 