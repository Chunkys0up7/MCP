import json
import os
from pathlib import Path
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

def save_mcp_servers(servers: Dict[str, Dict[str, Any]]):
    serializable_servers: Dict[str, Dict[str, Any]] = {}
    for server_id, server_data in servers.items():
        config_to_save = server_data["config"]
        if hasattr(config_to_save, 'model_dump'): # If it's a Pydantic model
            config_to_save = config_to_save.model_dump(mode='json')
        elif not isinstance(config_to_save, dict):
             print(f"[WARN] Config for {server_id} is not a dict or Pydantic model, attempting to convert. Type: {type(config_to_save)}")
             config_to_save = dict(config_to_save) if config_to_save else {}


        serializable_servers[server_id] = {
            "id": server_data["id"],
            "name": server_data["name"],
            "description": server_data.get("description"),
            "type": server_data["type"],
            "config": config_to_save 
        }
    try:
        # STORAGE_DIR.mkdir(exist_ok=True) # Ensure dir exists
        with open(MCP_STORAGE_FILE, 'w') as f:
            json.dump(serializable_servers, f, indent=2)
        print(f"Successfully saved {len(serializable_servers)} MCPs to {MCP_STORAGE_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save MCPs to storage: {str(e)}")

# Initialize the global registry
mcp_server_registry: Dict[str, Dict[str, Any]] = {} # Initialize as empty dict for now
# print(f"MCP Server Registry initialized with {len(mcp_server_registry)} servers from {MCP_STORAGE_FILE}") # Removed print
print(f"MCP Server Registry initialized as empty. DB loading pending.") # Placeholder print 