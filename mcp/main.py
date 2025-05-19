from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from typing import Dict, Any, List
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage file path
STORAGE_FILE = Path("mcp_storage.json")

def load_storage() -> Dict[str, Any]:
    """Load MCP storage from file."""
    if not STORAGE_FILE.exists():
        return {}
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading storage: {e}")
        return {}

def save_storage(data: Dict[str, Any]) -> None:
    """Save MCP storage to file."""
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving storage: {e}")

@app.get("/context")
async def get_context() -> Dict[str, Any]:
    """Get all MCPs."""
    return load_storage()

@app.get("/context/{mcp_id}")
async def get_mcp(mcp_id: str) -> Dict[str, Any]:
    """Get a specific MCP by ID."""
    storage = load_storage()
    if mcp_id not in storage:
        raise HTTPException(status_code=404, detail="MCP not found")
    return storage[mcp_id]

@app.post("/context/{mcp_id}/execute")
async def execute_mcp(mcp_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP with given inputs."""
    storage = load_storage()
    if mcp_id not in storage:
        raise HTTPException(status_code=404, detail="MCP not found")
    
    mcp = storage[mcp_id]
    
    # For now, just return a mock response
    return {
        "status": "success",
        "result": f"Executed {mcp['name']} with inputs: {inputs}",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/context")
async def create_mcp(mcp: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new MCP."""
    storage = load_storage()
    mcp_id = str(uuid.uuid4())
    mcp["id"] = mcp_id
    storage[mcp_id] = mcp
    save_storage(storage)
    return mcp

@app.put("/context/{mcp_id}")
async def update_mcp(mcp_id: str, mcp: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing MCP."""
    storage = load_storage()
    if mcp_id not in storage:
        raise HTTPException(status_code=404, detail="MCP not found")
    mcp["id"] = mcp_id
    storage[mcp_id] = mcp
    save_storage(storage)
    return mcp

@app.delete("/context/{mcp_id}")
async def delete_mcp(mcp_id: str) -> Dict[str, Any]:
    """Delete an MCP."""
    storage = load_storage()
    if mcp_id not in storage:
        raise HTTPException(status_code=404, detail="MCP not found")
    mcp = storage.pop(mcp_id)
    save_storage(storage)
    return mcp 