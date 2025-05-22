from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional
import uuid
import os
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import time
from collections import defaultdict
from dotenv import load_dotenv

from ..core.base import BaseMCPServer
from ..core.llm_prompt import LLMPromptMCP
from ..core.jupyter_notebook import JupyterNotebookMCP
from ..core.python_script import PythonScriptMCP
from ..core.ai_assistant import AIAssistantMCP

from mcp.core.types import (
    BaseMCPConfig,
    LLMPromptConfig,
    JupyterNotebookConfig,
    PythonScriptConfig,
    AIAssistantConfig,
    MCPType,
    MCPConfig as AllMCPConfigUnion # Union of all config types
)
from ..core.models import MCPResult

from ..core.registry import mcp_server_registry, save_mcp_servers

from mcp.db.session import SessionLocal
from mcp.cache.redis_manager import RedisCacheManager

from .dependencies import get_api_key # Import the dependency
from .routers import workflows as workflow_router # Added import
from mcp.schemas.mcp import MCPDetail # Import the new schema

# Rate limiting middleware (simple in-memory)
RATE_LIMIT = 100  # requests per minute
rate_limit_store: Dict[str, List[float]] = defaultdict(list)

app = FastAPI( # ADD app initialization here
    title="Model Context Protocol (MCP) Server",
    version="0.3.0",
    description="A server to manage and execute MCPs (LLM Prompts, Python Scripts, Jupyter Notebooks, AI Assistants) and orchestrate workflows."
)

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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Include the workflow router
app.include_router(workflow_router.router)

# API Request model for creating MCPs
class MCPCreationRequest(BaseModel):
    name: str
    type: MCPType # Use the enum for validation
    description: Optional[str] = None
    # Config will be specific to the MCPType
    config: Dict[str, Any] # Raw config dict from request

@app.get("/context", response_model=List[MCPDetail]) # Changed response model to List[MCPDetail]
async def get_all_mcp_servers(api_key_dependency: str = Depends(get_api_key)):
    response_list = []
    for server_id, server_data in mcp_server_registry.items():
        mcp_detail_data = {
            "id": server_data.get("id"),
            "name": server_data.get("name"),
            "type": server_data.get("type"),
            "description": server_data.get("description"),
            "config": server_data.get("config")
        }
        try:
            response_list.append(MCPDetail(**mcp_detail_data))
        except ValidationError as e:
            logger.error(f"Data validation error for MCP {server_id} in list view: {e.errors()}")
            # Decide: skip this MCP, or raise an error for the whole request
            # For now, skipping problematic ones from the list
            continue 
    return response_list

@app.get("/context/{server_id}", response_model=MCPDetail) # New endpoint
async def get_mcp_server_details(server_id: str, api_key_dependency: str = Depends(get_api_key)):
    server_data = mcp_server_registry.get(server_id)
    if not server_data:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    
    # Prepare data for MCPDetail schema, excluding the 'instance'
    mcp_detail_data = {
        "id": server_data.get("id"),
        "name": server_data.get("name"),
        "type": server_data.get("type"), # This should be MCPType enum value already if stored correctly
        "description": server_data.get("description"),
        "config": server_data.get("config") # This is already a dict
    }
    try:
        return MCPDetail(**mcp_detail_data)
    except ValidationError as e: # Should not happen if data in registry is valid
        # Log this error, as it indicates an inconsistency
        logger.error(f"Data validation error for MCP {server_id} from registry: {e.errors()}")
        raise HTTPException(status_code=500, detail="Error retrieving MCP details: Invalid data format in registry.")

@app.post("/context", response_model=Dict[str, Any], status_code=201)
async def create_mcp_server(request: MCPCreationRequest, api_key_dependency: str = Depends(get_api_key)):
    server_id = str(uuid.uuid4())
    
    config_init_data = request.config.copy()
    config_init_data['id'] = server_id
    config_init_data['name'] = request.name
    if request.description:
        config_init_data['description'] = request.description
    config_init_data['type'] = request.type.value

    try:
        config_obj: Optional[AllMCPConfigUnion] = None
        mcp_instance: Optional[BaseMCPServer] = None

        # MCP Instantiation logic
        if request.type == MCPType.LLM_PROMPT:
            config_obj = LLMPromptConfig(**config_init_data)
            mcp_instance = LLMPromptMCP(config_obj)
        elif request.type == MCPType.JUPYTER_NOTEBOOK:
            config_obj = JupyterNotebookConfig(**config_init_data)
            mcp_instance = JupyterNotebookMCP(config_obj)
        elif request.type == MCPType.PYTHON_SCRIPT:
            config_obj = PythonScriptConfig(**config_init_data) # This is where validation happens for PythonScriptConfig
            mcp_instance = PythonScriptMCP(config_obj)
        elif request.type == MCPType.AI_ASSISTANT:
            config_obj = AIAssistantConfig(**config_init_data)
            mcp_instance = AIAssistantMCP(config_obj)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported MCP server type: {request.type.value}")

        if not config_obj:
            raise HTTPException(status_code=500, detail="Failed to create config object.")

        server_entry = {
            "id": server_id,
            "name": config_obj.name,
            "description": config_obj.description,
            "type": request.type.value,
            "config": config_obj.model_dump(),
            "instance": mcp_instance
        }
        mcp_server_registry[server_id] = server_entry
        save_mcp_servers(mcp_server_registry)
        
        return {key: value for key, value in server_entry.items() if key != 'instance'}

    except ValidationError as ve: # EXPLICITLY CATCH PYDANTIC VALIDATIONERROR
        logger.error(f"PYDANTIC VALIDATION ERROR in create_mcp_server: {ve.errors()}")
        raise HTTPException(status_code=422, detail=ve.errors())
    except HTTPException: 
        raise
    except Exception as e: 
        import traceback
        logger.error(f"UNEXPECTED ERROR in create_mcp_server: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error creating MCP server: {str(e)}")

@app.post("/context/{server_id}/execute", response_model=MCPResult)
async def execute_mcp_server(server_id: str, inputs: Dict[str, Any], api_key_dependency: str = Depends(get_api_key)):
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
async def delete_mcp_server(server_id: str, api_key_dependency: str = Depends(get_api_key)):
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