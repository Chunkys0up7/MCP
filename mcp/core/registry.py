import os
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from mcp.db.models import MCP
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