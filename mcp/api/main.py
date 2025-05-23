from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import os
from datetime import datetime
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import time
from collections import defaultdict
from sqlalchemy.orm import Session

from mcp.core.types import (
    MCPType # Union of all config types
)

from ..core.registry import mcp_server_registry

from mcp.db.session import SessionLocal, get_db
from mcp.cache.redis_manager import RedisCacheManager

from mcp.schemas.mcp import MCPDetail, MCPCreate, MCPUpdate, MCPListItem, MCPRead
from mcp.core import registry as mcp_registry_service
from mcp.core.security import get_current_subject

from .routers import workflows as workflow_router
from .routers import auth as auth_router

# Rate limiting middleware (simple in-memory)
RATE_LIMIT = 100  # requests per minute
rate_limit_store: Dict[str, List[float]] = defaultdict(list)

app = FastAPI(
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
app.include_router(auth_router.router)

# API Request model for creating MCPs
class MCPCreationRequest(BaseModel):
    name: str
    type: MCPType # Use the enum for validation
    description: Optional[str] = None
    # Config will be specific to the MCPType
    config: Dict[str, Any] # Raw config dict from request

@app.get("/context", response_model=List[MCPListItem])
async def list_mcp_definitions(
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject),
    skip: int = 0,
    limit: int = 100
):
    db_mcps = mcp_registry_service.load_all_mcp_definitions_from_db(db=db) # Assuming this will be paginated in future
    # Convert MCP ORM models to MCPListItem Pydantic models
    # This is a simplified conversion; real implementation might involve fetching latest version string
    response_items = []
    for mcp in db_mcps:
        # Attempt to get latest version string (simplified)
        latest_version_str = None
        if mcp.versions: # MCP model has a 'versions' relationship
            # Sort versions by created_at or a semantic version field if available
            # For simplicity, taking the first one if it exists, assuming it's ordered or just any version
            latest_version_str = mcp.versions[-1].version_str if mcp.versions else "N/A"

        response_items.append(
            MCPListItem(
                id=mcp.id,
                name=mcp.name,
                type=MCPType(mcp.type), # Convert string from DB to Enum
                description=mcp.description,
                tags=mcp.tags,
                latest_version_str=latest_version_str, # Placeholder
                updated_at=mcp.updated_at
            )
        )
    return response_items

@app.post("/context", response_model=MCPRead, status_code=201)
async def create_mcp_definition(
    mcp_in: MCPCreate, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    try:
        created_mcp = mcp_registry_service.save_mcp_definition_to_db(db=db, mcp_data=mcp_in)
        return created_mcp # MCPRead schema should be compatible if ORM mode is enabled
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=400, detail=f"Error creating MCP definition: {str(e)}")

@app.get("/context/{mcp_id}", response_model=MCPDetail)
async def get_mcp_definition_details(
    mcp_id: str, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    db_mcp = mcp_registry_service.load_mcp_definition_from_db(db=db, mcp_id_str=mcp_id)
    if db_mcp is None:
        raise HTTPException(status_code=404, detail="MCP definition not found")
    
    # Populate latest version info for MCPDetail
    latest_version_config = None
    latest_version_str = None
    if db_mcp.versions:
        # Assuming versions are ordered by creation or semantic version in the relationship
        # For simplicity, using the "last" version in the list as latest.
        # A more robust approach would sort them or have a dedicated 'latest_version' pointer.
        latest_version = db_mcp.versions[-1] if db_mcp.versions else None
        if latest_version:
            latest_version_config = latest_version.config_snapshot
            latest_version_str = latest_version.version_str
            
    return MCPDetail(
        id=db_mcp.id,
        name=db_mcp.name,
        type=MCPType(db_mcp.type), # Convert string from DB to Enum
        description=db_mcp.description,
        tags=db_mcp.tags,
        created_at=db_mcp.created_at,
        updated_at=db_mcp.updated_at,
        latest_version_config=latest_version_config,
        latest_version_str=latest_version_str
    )

@app.put("/context/{mcp_id}", response_model=MCPRead)
async def update_mcp_definition(
    mcp_id: str, 
    mcp_in: MCPUpdate, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    updated_mcp = mcp_registry_service.update_mcp_definition_in_db(db=db, mcp_id_str=mcp_id, mcp_data=mcp_in)
    if updated_mcp is None:
        raise HTTPException(status_code=404, detail="MCP definition not found for update")
    return updated_mcp

@app.delete("/context/{mcp_id}", status_code=204)
async def delete_mcp_definition(
    mcp_id: str, 
    db: Session = Depends(get_db), 
    current_user_sub: str = Depends(get_current_subject)
):
    deleted = mcp_registry_service.delete_mcp_definition_from_db(db=db, mcp_id_str=mcp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="MCP definition not found for deletion")
    return Response(status_code=204) # Return 204 No Content

@app.get("/context/search", response_model=List[MCPListItem])
async def search_mcp_definitions(
    query: str,
    db: Session = Depends(get_db),
    current_user_sub: str = Depends(get_current_subject),
    limit: int = 10
):
    """
    Searches for MCP definitions using semantic text search based on the query.
    Results are ordered by relevance.
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
    
    # Use the mcp_registry_service alias consistent with other /context endpoints
    db_mcps = mcp_registry_service.search_mcp_definitions_by_text(db=db, query_text=query, limit=limit)

    response_items = []
    for mcp in db_mcps:
        latest_version_str = None
        if mcp.versions:
            latest_version_str = mcp.versions[-1].version_str if mcp.versions else "N/A" # Simplified

        response_items.append(
            MCPListItem(
                id=mcp.id,
                name=mcp.name,
                type=MCPType(mcp.type), # Convert string from DB to Enum
                description=mcp.description,
                tags=mcp.tags,
                latest_version_str=latest_version_str,
                updated_at=mcp.updated_at
                # MCPListItem does not include embedding
            )
        )
    return response_items

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