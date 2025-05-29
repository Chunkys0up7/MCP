import json
from pathlib import Path
from typing import Any, Dict, Optional, Type

from fastapi import APIRouter, Body, Depends, HTTPException

from mcp.core.base import BaseMCPServer
from mcp.core.types import (LLMPromptConfig, JupyterNotebookConfig, MCPConfig,
                            MCPResult, MCPType, PythonScriptConfig, AIAssistantConfig)
from mcp.core.llm_prompt import LLMPromptMCP
from mcp.core.jupyter_notebook import JupyterNotebookMCP
from mcp.core.python_script import PythonScriptMCP
# from mcp.core.ai_assistant import AIAssistantMCP # Assuming this will exist

from ..dependencies import get_current_subject

# Directory where MCP configuration JSON files are stored
MCP_CONFIGS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "examples"

router = APIRouter(
    prefix="/execute",
    tags=["Execution"],
    dependencies=[Depends(get_current_subject)],
)

# Mapping from MCPType to the corresponding configuration model and server class
# TODO: Add AIAssistantMCP to this map when available
MCP_TYPE_MAP: Dict[MCPType, Dict[str, Type]] = {
    MCPType.LLM_PROMPT: {"config": LLMPromptConfig, "server": LLMPromptMCP},
    MCPType.JUPYTER_NOTEBOOK: {"config": JupyterNotebookConfig, "server": JupyterNotebookMCP},
    MCPType.PYTHON_SCRIPT: {"config": PythonScriptConfig, "server": PythonScriptMCP},
    # MCPType.AI_ASSISTANT: {"config": AIAssistantConfig, "server": AIAssistantMCP},
}

def load_mcp_config_from_file(mcp_config_id: str) -> Optional[MCPConfig]:
    """Loads a specific MCP configuration JSON file by its 'id' field."""
    if not MCP_CONFIGS_DIR.exists() or not MCP_CONFIGS_DIR.is_dir():
        print(f"MCP_CONFIGS_DIR not found or not a directory: {MCP_CONFIGS_DIR}")
        return None

    for file_path in MCP_CONFIGS_DIR.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                if data.get("id") == mcp_config_id:
                    # Validate and parse against the base MCPConfig to get the type,
                    # then Pydantic will use the correct sub-model.
                    return MCPConfig(**data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}. Skipping.")
        except Exception as e:
            print(f"Error processing MCP config file {file_path}: {e}. Skipping.")
    return None


@router.post("/mcp/{mcp_config_id}", response_model=MCPResult)
async def execute_single_mcp(
    mcp_config_id: str,
    initial_inputs: Optional[Dict[str, Any]] = Body(None, description="Initial inputs for the MCP"),
    # current_user_sub: str = Depends(get_current_subject), # Already in router dependencies
):
    """Executes a single MCP configuration identified by its ID."""
    mcp_config_instance = load_mcp_config_from_file(mcp_config_id)

    if not mcp_config_instance:
        raise HTTPException(status_code=404, detail=f"MCP configuration with ID '{mcp_config_id}' not found in {MCP_CONFIGS_DIR}.")

    mcp_type = mcp_config_instance.type
    if mcp_type not in MCP_TYPE_MAP:
        raise HTTPException(status_code=501, detail=f"MCP type '{mcp_type}' is not supported for direct execution yet.")

    server_class = MCP_TYPE_MAP[mcp_type]["server"]
    
    # Ensure the loaded config instance is of the correct specific type for the server
    # Pydantic's discriminated union should ensure mcp_config_instance is already the correct type
    # but an explicit check or re-validation might be desired in some cases.
    # For now, we assume mcp_config_instance is correctly typed.

    try:
        # Instantiate the server with its specific config model
        mcp_server: BaseMCPServer = server_class(config=mcp_config_instance)
        
        # TODO: Implement asynchronous execution if server methods are async
        # For now, assuming synchronous execute method in BaseMCPServer
        # If execute is async, it should be: result = await mcp_server.execute(inputs=initial_inputs)
        result = mcp_server.execute(inputs=initial_inputs)
        return result
    except Exception as e:
        # Log the full exception for debugging
        print(f"Error during MCP execution for ID {mcp_config_id}: {type(e).__name__} - {e}")
        # Consider if more specific error details should be exposed to the client
        raise HTTPException(status_code=500, detail=f"MCP execution failed: {str(e)}") 