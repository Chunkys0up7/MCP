from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uuid

from ..core.base import MCPConfig
from ..core.llm_prompt import LLMPromptMCP, LLMPromptConfig
from ..core.jupyter_notebook import JupyterNotebookMCP, JupyterNotebookConfig

app = FastAPI(title="MCP API", version="0.1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory MCP registry (replace with database in production)
mcp_registry: Dict[str, Any] = {}

class MCPCreateRequest(BaseModel):
    """Request model for creating a new MCP"""
    type: str
    config: Dict[str, Any]

class MCPExecuteRequest(BaseModel):
    """Request model for executing an MCP"""
    inputs: Dict[str, Any]

@app.post("/mcps")
async def create_mcp(request: MCPCreateRequest):
    """Create a new MCP instance"""
    mcp_id = str(uuid.uuid4())
    
    try:
        if request.type == "llm_prompt":
            config = LLMPromptConfig(**request.config)
            mcp = LLMPromptMCP(config)
        elif request.type == "jupyter_notebook":
            config = JupyterNotebookConfig(**request.config)
            mcp = JupyterNotebookMCP(config)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported MCP type: {request.type}")
        
        mcp_registry[mcp_id] = mcp
        return {"id": mcp_id, "name": mcp.name, "type": request.type}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mcps")
async def list_mcps():
    """List all registered MCPs"""
    return [
        {
            "id": mcp_id,
            "name": mcp.name,
            "type": mcp.__class__.__name__,
            "version": mcp.version
        }
        for mcp_id, mcp in mcp_registry.items()
    ]

@app.post("/mcps/{mcp_id}/execute")
async def execute_mcp(mcp_id: str, request: MCPExecuteRequest):
    """Execute an MCP with given inputs"""
    if mcp_id not in mcp_registry:
        raise HTTPException(status_code=404, detail="MCP not found")
    
    try:
        mcp = mcp_registry[mcp_id]
        result = await mcp.execute(request.inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcps/{mcp_id}")
async def delete_mcp(mcp_id: str):
    """Delete an MCP instance"""
    if mcp_id not in mcp_registry:
        raise HTTPException(status_code=404, detail="MCP not found")
    
    del mcp_registry[mcp_id]
    return {"status": "success"} 