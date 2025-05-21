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
STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / ".mcp_data" # Adjusted path relative to this file
STORAGE_DIR.mkdir(exist_ok=True)
MCP_STORAGE_FILE = STORAGE_DIR / "mcp_storage.json"

def load_mcp_servers() -> Dict[str, Dict[str, Any]]:
    if not MCP_STORAGE_FILE.exists():
        return {}
    with open(MCP_STORAGE_FILE, 'r') as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError:
            print("[WARN] MCP_STORAGE_FILE is corrupted. Returning empty registry.")
            return {} # Return empty if storage is corrupt
            
    loaded_servers: Dict[str, Dict[str, Any]] = {}
    for server_id, server_disk_data in raw_data.items():
        try:
            if not isinstance(server_disk_data, dict):
                print(f"[WARN] Skipping server ID {server_id} due to invalid data format (not a dict) in storage.")
                continue

            if not all(k in server_disk_data for k in ["id", "name", "type", "config"]):
                print(f"[WARN] Skipping server ID {server_id} due to missing essential keys in storage.")
                continue

            config_data = server_disk_data["config"]
            if not isinstance(config_data, dict):
                print(f"[WARN] Skipping server ID {server_id} due to invalid config format (not a dict) in storage.")
                continue
            
            config_data = config_data.copy() # Work with a copy
            mcp_type_str = server_disk_data["type"]
            
            config_data.setdefault('id', server_disk_data['id'])
            config_data.setdefault('name', server_disk_data['name'])
            config_data.setdefault('type', mcp_type_str)
            if 'description' in server_disk_data and server_disk_data['description'] is not None:
                 config_data.setdefault('description', server_disk_data['description'])


            config_obj: Optional[AllMCPConfigUnion] = None
            mcp_instance: Optional[BaseMCPServer] = None

            if mcp_type_str == MCPType.LLM_PROMPT.value:
                config_obj = LLMPromptConfig(**config_data)
                mcp_instance = LLMPromptMCP(config_obj)
            elif mcp_type_str == MCPType.JUPYTER_NOTEBOOK.value:
                config_obj = JupyterNotebookConfig(**config_data)
                mcp_instance = JupyterNotebookMCP(config_obj)
            elif mcp_type_str == MCPType.PYTHON_SCRIPT.value:
                config_obj = PythonScriptConfig(**config_data)
                mcp_instance = PythonScriptMCP(config_obj)
            elif mcp_type_str == MCPType.AI_ASSISTANT.value:
                config_obj = AIAssistantConfig(**config_data)
                mcp_instance = AIAssistantMCP(config_obj) # AIAssistantMCP might handle None instance internally
            else:
                print(f"[WARN] Unknown MCP type '{mcp_type_str}' for server ID {server_id}. Skipping.")
                continue
            
            if mcp_instance and config_obj:
                loaded_servers[server_id] = {
                    "id": server_disk_data["id"],
                    "name": config_obj.name,
                    "description": config_obj.description,
                    "type": mcp_type_str,
                    "config": config_obj.model_dump(),
                    "instance": mcp_instance
                }
            elif config_obj: # For types like AI_ASSISTANT that might not have an instance immediately
                 loaded_servers[server_id] = {
                    "id": server_disk_data["id"],
                    "name": config_obj.name,
                    "description": config_obj.description,
                    "type": mcp_type_str,
                    "config": config_obj.model_dump(),
                    "instance": None # Instance can be None
                }

        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to recreate MCP instance for {server_id} from storage. Error: {str(e)}\\n{traceback.format_exc()}")
            continue
    print(f"Successfully loaded {len(loaded_servers)} MCPs into registry.")
    return loaded_servers

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
        STORAGE_DIR.mkdir(exist_ok=True) # Ensure dir exists
        with open(MCP_STORAGE_FILE, 'w') as f:
            json.dump(serializable_servers, f, indent=2)
        print(f"Successfully saved {len(serializable_servers)} MCPs to {MCP_STORAGE_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save MCPs to storage: {str(e)}")

# Initialize the global registry
mcp_server_registry: Dict[str, Dict[str, Any]] = load_mcp_servers()
print(f"MCP Server Registry initialized with {len(mcp_server_registry)} servers from {MCP_STORAGE_FILE}") 