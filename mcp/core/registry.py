import os
from typing import Any, Dict, Optional

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