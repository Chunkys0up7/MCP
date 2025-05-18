from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uuid
import json
import os
from pathlib import Path

from ..core.base import MCPConfig
from ..core.llm_prompt import LLMPromptMCP, LLMPromptConfig
from ..core.jupyter_notebook import JupyterNotebookMCP, JupyterNotebookConfig

app = FastAPI(title="MCP API", description="Microservice Control Panel API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP registry and persistence
MCP_STORAGE_FILE = Path(__file__).parent.parent.parent / "mcp_storage.json"

def load_mcps() -> Dict[str, Any]:
    """Load MCPs from storage file"""
    print(f"[DEBUG] MCP_STORAGE_FILE absolute path: {MCP_STORAGE_FILE.resolve()}")
    if MCP_STORAGE_FILE.exists():
        with open(MCP_STORAGE_FILE, 'r') as f:
            data = json.load(f)
            print(f"[DEBUG] Raw data loaded from storage: {data}")
            # Recreate MCP instances
            for mcp_id, mcp_data in data.items():
                if mcp_data["type"] == "llm_prompt":
                    try:
                        print(f"Loading MCP {mcp_id} with config: {mcp_data['config']}")
                        # Create config with model name from storage
                        config = LLMPromptConfig(**mcp_data["config"])
                        print(f"Created config with model name: {config.model_name}")
                        # Create MCP instance with config
                        mcp_data["instance"] = LLMPromptMCP(config)
                        print(f"Successfully created MCP instance for {mcp_id}")
                    except ValueError as e:
                        print(f"Error creating MCP instance for {mcp_id}: {str(e)}")
                        # Skip this MCP if there's an error
                        continue
            return data
    print("[DEBUG] MCP_STORAGE_FILE does not exist!")
    return {}

def save_mcps(mcps: Dict[str, Any]):
    """Save MCPs to storage file"""
    # Convert to serializable format
    serializable_mcps = {}
    for mcp_id, mcp_data in mcps.items():
        # Create a copy of the config to modify
        config = mcp_data["config"].copy()
        
        serializable_mcps[mcp_id] = {
            "id": mcp_data["id"],
            "name": mcp_data["name"],
            "description": mcp_data["description"],
            "type": mcp_data["type"],
            "config": config
        }
    
    with open(MCP_STORAGE_FILE, 'w') as f:
        json.dump(serializable_mcps, f, indent=2)

# Initialize MCP registry from storage
mcp_registry: Dict[str, Any] = load_mcps()

class MCPRequest(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    config: Optional[dict] = None

@app.get("/")
async def root():
    return {"message": "Welcome to MCP API"}

@app.get("/mcps")
async def get_mcps():
    """Get all MCP instances"""
    return {"mcps": [
        {
            "id": mcp_id,
            "name": mcp["name"],
            "description": mcp["description"],
            "type": mcp["type"],
            "config": mcp["config"]
        }
        for mcp_id, mcp in mcp_registry.items()
    ]}

@app.post("/mcps", response_model=Dict[str, Any])
async def create_mcp(request: MCPRequest):
    """Create a new MCP"""
    try:
        mcp_id = str(uuid.uuid4())  # Generate a unique ID
        if request.type == "llm_prompt":
            if not request.config:
                raise HTTPException(status_code=400, detail="Config is required for LLM Prompt MCP")
            
            # Set default model name if not provided
            if "model_name" not in request.config:
                request.config["model_name"] = "claude-3-sonnet-20240229"
            
            config = LLMPromptConfig(**request.config)
            mcp = LLMPromptMCP(config)
            mcp_registry[mcp_id] = {
                "id": mcp_id,
                "name": request.name,
                "description": request.description,
                "type": request.type,
                "config": request.config,
                "instance": mcp
            }
            # Save to storage
            save_mcps(mcp_registry)
            return {
                "id": mcp_id,
                "name": request.name,
                "type": request.type,
                "description": request.description,
                "config": request.config
            }
        elif request.type == "jupyter_notebook":
            # TODO: Implement notebook MCP
            raise HTTPException(status_code=501, detail="Notebook MCP not implemented yet")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported MCP type: {request.type}")
    except ValueError as e:
        if "PERPLEXITY_API_KEY" in str(e):
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcps/{mcp_id}/execute")
async def execute_mcp(mcp_id: str, inputs: Dict[str, Any]):
    """Execute an MCP instance with given inputs"""
    if mcp_id not in mcp_registry:
        raise HTTPException(status_code=404, detail="MCP not found")
    
    mcp = mcp_registry[mcp_id]
    try:
        result = await mcp["instance"].execute(inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcps/{mcp_id}")
async def delete_mcp(mcp_id: str):
    """Delete an MCP instance"""
    if mcp_id not in mcp_registry:
        raise HTTPException(status_code=404, detail="MCP not found")
    
    del mcp_registry[mcp_id]
    # Save to storage after deletion
    save_mcps(mcp_registry)
    return {"status": "success"} 