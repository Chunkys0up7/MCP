from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uuid
import json
import os
from pathlib import Path
from datetime import datetime
import secrets
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import time
from collections import defaultdict

from ..core.base import BaseMCPServer
from ..core.llm_prompt import LLMPromptMCP
from ..core.jupyter_notebook import JupyterNotebookMCP
from ..core.python_script import PythonScriptMCP

# Import Config models and MCPType Enum from mcp.core.types
from mcp.core.types import (
    BaseMCPConfig, # For type checking if needed
    LLMPromptConfig,
    JupyterNotebookConfig,
    PythonScriptConfig,
    AIAssistantConfig,
    MCPType,
    MCPConfig as AllMCPConfigUnion # Union of all config types
)
from ..core.models import MCPResult

from mcp.db.session import SessionLocal
from mcp.cache.redis_manager import RedisCacheManager

# API Key management
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("MCP_API_KEY", secrets.token_urlsafe(32))
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=403, detail="Invalid API Key"
        )
    return api_key_header

app = FastAPI(title="MCP Server API", description="Model Context Protocol Server API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (simple in-memory)
RATE_LIMIT = 100  # requests per minute
rate_limit_store: Dict[str, List[float]] = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if current_time - t < 60]
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})
    rate_limit_store[client_ip].append(current_time)
    response = await call_next(request)
    return response

# MCP server registry and persistence
STORAGE_DIR = Path(__file__).parent.parent.parent / ".mcp_data"
STORAGE_DIR.mkdir(exist_ok=True)
MCP_STORAGE_FILE = STORAGE_DIR / "mcp_storage.json"

def load_mcp_servers() -> Dict[str, Dict[str, Any]]:
    if not MCP_STORAGE_FILE.exists():
        return {}
    with open(MCP_STORAGE_FILE, 'r') as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError:
            return {} # Return empty if storage is corrupt
            
    loaded_servers: Dict[str, Dict[str, Any]] = {}
    for server_id, server_disk_data in raw_data.items():
        try:
            # Ensure essential keys are present
            if not all(k in server_disk_data for k in ["id", "name", "type", "config"]):
                print(f"[WARN] Skipping server ID {server_id} due to missing essential keys in storage.")
                continue

            config_data = server_disk_data["config"].copy()
            mcp_type_str = server_disk_data["type"]
            
            # Add 'name', 'id', 'type' to config_data if not already present, for Pydantic model init
            config_data.setdefault('id', server_disk_data['id'])
            config_data.setdefault('name', server_disk_data['name'])
            # The 'type' field in config_data will be validated by Pydantic if it matches the enum
            config_data.setdefault('type', mcp_type_str)

            config_obj: Optional[AllMCPConfigUnion] = None # Union of all config types
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
                # mcp_instance = AIAssistantMCP(config_obj) # No implementation yet
                print(f"[WARN] AI Assistant MCP type ({mcp_type_str}) loaded, but no executor is implemented.")
            else:
                print(f"[WARN] Unknown MCP type '{mcp_type_str}' for server ID {server_id}. Skipping.")
                continue
            
            if mcp_instance and config_obj: # If AI assistant, mcp_instance might be None
                loaded_servers[server_id] = {
                    "id": server_disk_data["id"],
                    "name": config_obj.name, # Use name from Pydantic model
                    "description": config_obj.description, # Use description from Pydantic model
                    "type": mcp_type_str,
                    "config": config_obj.model_dump(), # Store validated and typed config
                    "instance": mcp_instance
                }
            elif config_obj: # For types like AI_ASSISTANT that might not have an instance yet
                 loaded_servers[server_id] = {
                    "id": server_disk_data["id"],
                    "name": config_obj.name,
                    "description": config_obj.description,
                    "type": mcp_type_str,
                    "config": config_obj.model_dump(),
                    "instance": None # No instance to execute
                }

        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to recreate MCP instance for {server_id} from storage data: {server_disk_data}. Error: {str(e)}\n{traceback.format_exc()}")
            continue
    return loaded_servers

def save_mcp_servers(servers: Dict[str, Dict[str, Any]]):
    serializable_servers: Dict[str, Dict[str, Any]] = {}
    for server_id, server_data in servers.items():
        # Ensure config is a dict (it should be if from model_dump())
        config_to_save = server_data["config"]
        if not isinstance(config_to_save, dict):
             # If config is a Pydantic model, dump it. This handles cases where it might not have been dumped yet.
            if hasattr(config_to_save, 'model_dump'):
                config_to_save = config_to_save.model_dump()
            else: # Fallback, though ideally should always be a Pydantic model or dict
                config_to_save = dict(config_to_save) if config_to_save else {}

        serializable_servers[server_id] = {
            "id": server_data["id"],
            "name": server_data["name"],
            "description": server_data.get("description"),
            "type": server_data["type"],
            "config": config_to_save 
            # Instance is not saved, it's recreated on load
        }
    with open(MCP_STORAGE_FILE, 'w') as f:
        json.dump(serializable_servers, f, indent=2)

mcp_server_registry: Dict[str, Dict[str, Any]] = load_mcp_servers()

# API Request model for creating MCPs
class MCPCreationRequest(BaseModel):
    name: str
    type: MCPType # Use the enum for validation
    description: Optional[str] = None
    # Config will be specific to the MCPType
    config: Dict[str, Any] # Raw config dict from request

@app.get("/context")
async def get_all_mcp_servers():
    return [
        {key: value for key, value in server_data.items() if key != 'instance'}
        for server_data in mcp_server_registry.values()
    ]

@app.post("/context", response_model=Dict[str, Any], status_code=201)
async def create_mcp_server(request: MCPCreationRequest, api_key: str = Depends(get_api_key)):
    server_id = str(uuid.uuid4())
    
    # Prepare config_data for Pydantic model initialization
    # It needs id, name, description (optional), type (from enum value)
    config_init_data = request.config.copy()
    config_init_data['id'] = server_id
    config_init_data['name'] = request.name
    if request.description:
        config_init_data['description'] = request.description
    config_init_data['type'] = request.type.value # Crucial: Pydantic model expects the enum value

    try:
        config_obj: Optional[AllMCPConfigUnion] = None
        mcp_instance: Optional[BaseMCPServer] = None

        if request.type == MCPType.LLM_PROMPT:
            config_obj = LLMPromptConfig(**config_init_data)
            mcp_instance = LLMPromptMCP(config_obj)
        elif request.type == MCPType.JUPYTER_NOTEBOOK:
            config_obj = JupyterNotebookConfig(**config_init_data)
            mcp_instance = JupyterNotebookMCP(config_obj)
        elif request.type == MCPType.PYTHON_SCRIPT:
            config_obj = PythonScriptConfig(**config_init_data)
            mcp_instance = PythonScriptMCP(config_obj)
        elif request.type == MCPType.AI_ASSISTANT:
            config_obj = AIAssistantConfig(**config_init_data)
            # mcp_instance = AIAssistantMCP(config_obj) # No implementation yet
            print(f"[WARN] AI Assistant MCP type ({request.type.value}) created, but no executor is implemented.")
        else:
            # This case should ideally be caught by Pydantic validation of MCPType enum in MCPCreationRequest
            raise HTTPException(status_code=400, detail=f"Unsupported MCP server type: {request.type.value}")

        if not config_obj:
             # Should not happen if type is validated by Pydantic
            raise HTTPException(status_code=500, detail="Failed to create config object.")

        server_entry = {
            "id": server_id,
            "name": config_obj.name,
            "description": config_obj.description,
            "type": request.type.value,
            "config": config_obj.model_dump(), # Store the validated and typed config
            "instance": mcp_instance # Can be None for AI Assistant for now
        }
        mcp_server_registry[server_id] = server_entry
        save_mcp_servers(mcp_server_registry)
        
        # Return all data except the instance itself
        return {key: value for key, value in server_entry.items() if key != 'instance'}

    except HTTPException: # Re-raise HTTP exceptions
        raise
    except Exception as e: # Catch Pydantic validation errors or other issues
        import traceback
        raise HTTPException(status_code=400, detail=f"Error creating MCP server: {str(e)}\n{traceback.format_exc()}")

@app.post("/context/{server_id}/execute", response_model=MCPResult)
async def execute_mcp_server(server_id: str, inputs: Dict[str, Any], api_key: str = Depends(get_api_key)):
    server_data = mcp_server_registry.get(server_id)
    if not server_data:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    
    mcp_instance = server_data.get("instance")
    if not mcp_instance:
        raise HTTPException(status_code=400, detail=f"MCP Server type {server_data.get('type')} cannot be executed (no implementation).")

    try:
        # The execute method in MCP classes should return a dict adhering to MCPResult structure,
        # or at least containing 'success', 'result', 'error'.
        execution_output = await mcp_instance.execute(inputs or {})
        
        # Ensure the output conforms to MCPResult structure as much as possible
        # The MCP classes were refactored to return {"success", "result", "error"}
        # stdout/stderr are specific to PythonScriptMCP and Jupyter, handled within their results.
        return MCPResult(
            success=execution_output.get("success", False),
            result=execution_output.get("result"),
            error=execution_output.get("error"),
            stdout=execution_output.get("stdout"), # May be None if not applicable
            stderr=execution_output.get("stderr")  # May be None if not applicable
        )

    except Exception as e:
        import traceback
        logger.error(f"Error executing server {server_id}: {str(e)}\n{traceback.format_exc()}")
        return MCPResult(success=False, error=f"Execution failed: {str(e)}")

@app.delete("/context/{server_id}", status_code=204) # 204 No Content for successful deletion
async def delete_mcp_server(server_id: str, api_key: str = Depends(get_api_key)):
    if server_id not in mcp_server_registry:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    del mcp_server_registry[server_id]
    save_mcp_servers(mcp_server_registry)
    return # Return None for 204 No Content

@app.get("/health")
async def health_check():
    health = {"status": "healthy", "message": "Service is running", "database": "not_checked", "redis": "not_checked"}
    try:
        db = SessionLocal()
        db.execute("SELECT 1") # type: ignore
        db.close()
        health["database"] = "ok"
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"
    try:
        redis_manager = RedisCacheManager()
        redis_manager.ping()
        health["redis"] = "ok"
    except Exception as e:
        health["redis"] = f"error: {str(e)}"
        health["status"] = "degraded" 
    return health

@app.get("/stats")
async def get_stats_summary():
    # Uses the in-memory registry, which is already loaded
    type_counts: Dict[str, int] = defaultdict(int)
    model_usage: Dict[str, int] = defaultdict(int)

    for server_data in mcp_server_registry.values():
        type_counts[server_data["type"]] += 1
        # Config should be a dict after model_dump() during load/create
        config_dict = server_data.get("config", {})
        if isinstance(config_dict, dict) and "model_name" in config_dict:
            model_usage[config_dict["model_name"]] += 1
            
    return {
        "total_servers": len(mcp_server_registry),
        "server_types": dict(type_counts),
        "model_usage": dict(model_usage),
        "timestamp": datetime.now().isoformat()
    }

# Prometheus metrics (ensure these are only registered once)
# The Instrumentator handles its own registration.
if not hasattr(app, 'prometheus_instrumentator'): # Basic check to prevent re-instrumentation on reload
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        inprogress_name="mcp_inprogress_requests",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app)
    app.prometheus_instrumentator = instrumentator # Mark as instrumented

# Configure structured logging (JSONFormatter might be defined elsewhere or simplified)
# Basic logger setup for now
logger = logging.getLogger("mcp_api")
logger.setLevel(os.getenv("MCP_LOG_LEVEL", "INFO").upper())
# Ensure handlers are not duplicated on reload if uvicorn handles logging setup
if not logger.hasHandlers():
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

# Example of how request_id_middleware might look, it needs to be placed correctly
# with other middlewares. Uvicorn/Starlette might provide access_log features.
# @app.middleware("http")
# async def request_id_middleware(request: Request, call_next):
#     request_id = str(uuid.uuid4())
#     # You might want to use a request context library or pass it via state
#     # logger.info("Request started", extra={"request_id": request_id, ...})
#     response = await call_next(request)
#     return response

# Ensure this is after all route definitions if it processes all requests
# The prometheus_middleware you had before was overriding the Instrumentator's one.
# The Instrumentator already provides similar metrics.

logger.info("MCP API Application configured and starting...") 