import logging
import os
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
import json
import asyncio

from mcp.cache.redis_manager import RedisCacheManager
from mcp.core import registry as mcp_registry_service
from mcp.core.auth import UserRole, require_any_role
from mcp.core.types import MCPType  # Union of all config types
from mcp.db.base_models import log_audit_action
from mcp.db.session import get_db_session
from mcp.schemas.mcp import (MCPCreate, MCPDetail, MCPListItem, MCPUpdate)

from ..core.registry import mcp_server_registry
from .dependencies import get_current_subject
from .routers import apikey as apikey_router
from .routers import auth as auth_router
from .routers import components as components_router
from .routers import reviews as reviews_router
from .routers import workflows as workflow_router
from .routers import execution as execution_router

# Rate limiting middleware (simple in-memory)
RATE_LIMIT = 100  # requests per minute
rate_limit_store: Dict[str, List[float]] = defaultdict(list)

app = FastAPI(
    title="Model Context Protocol (MCP) Server",
    version="0.3.0",
    description="A server to manage and execute MCPs (LLM Prompts, Python Scripts, Jupyter Notebooks, AI Assistants) and orchestrate workflows.",
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if current_time - t < 60
    ]
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})
    rate_limit_store[client_ip].append(current_time)
    response = await call_next(request)
    return response


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the workflow router
app.include_router(workflow_router.router)
app.include_router(auth_router.router)
app.include_router(reviews_router.router)
app.include_router(components_router.router)
app.include_router(apikey_router.router)
app.include_router(execution_router.router)


# API Request model for creating MCPs
class MCPCreationRequest(BaseModel):
    name: str
    type: MCPType  # Use the enum for validation
    description: Optional[str] = None
    # Config will be specific to the MCPType
    config: Dict[str, Any]  # Raw config dict from request


@app.get("/context", response_model=List[MCPListItem])
async def list_mcp_definitions(
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
    skip: int = 0,
    limit: int = 100,
):
    db_mcps = mcp_registry_service.load_all_mcp_definitions_from_db(
        db=db
    )  # Assuming this will be paginated in future
    # Convert MCP ORM models to MCPListItem Pydantic models
    # This is a simplified conversion; real implementation might involve fetching latest version string
    response_items = []
    for mcp in db_mcps:
        # Attempt to get latest version string (simplified)
        latest_version_str = None
        if mcp.versions:  # MCP model has a 'versions' relationship
            # Sort versions by created_at or a semantic version field if available
            # For simplicity, taking the first one if it exists, assuming it's ordered or just any version
            latest_version_str = mcp.versions[-1].version_str if mcp.versions else "N/A"

        response_items.append(
            MCPListItem(
                id=mcp.id,
                name=mcp.name,
                type=MCPType(mcp.type),  # Convert string from DB to Enum
                description=mcp.description,
                tags=mcp.tags,
                latest_version_str=latest_version_str,  # Placeholder
                updated_at=mcp.updated_at,
            )
        )
    return response_items


@app.post("/context", response_model=MCPDetail, status_code=201)
async def create_mcp_definition(
    mcp_data: MCPCreate,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
    _: List[str] = Depends(require_any_role([UserRole.DEVELOPER, UserRole.ADMIN])),
    response: Response = None,
):
    """Creates a new MCP definition."""
    db_mcp = mcp_registry_service.save_mcp_definition_to_db(
        db=db, mcp_data=mcp_data
    )
    # Only log audit if subject is a valid UUID
    try:
        user_id_val = uuid.UUID(current_user_sub)
    except Exception:
        user_id_val = None
    if user_id_val:
        log_audit_action(
            db,
            user_id=user_id_val,
            action_type="create_mcp",
            target_id=db_mcp.id,
            details=mcp_data.dict(),
        )
    return db_mcp


@app.get("/context/{mcp_id}", response_model=MCPDetail)
async def get_mcp_definition_details(
    mcp_id: str,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
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
        type=MCPType(db_mcp.type),  # Convert string from DB to Enum
        description=db_mcp.description,
        tags=db_mcp.tags,
        created_at=db_mcp.created_at,
        updated_at=db_mcp.updated_at,
        latest_version_config=latest_version_config,
        latest_version_str=latest_version_str,
    )


@app.put("/context/{mcp_id}", response_model=MCPDetail)
async def update_mcp_definition(
    mcp_id: str,
    mcp_data: MCPUpdate,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
    _: List[str] = Depends(require_any_role([UserRole.DEVELOPER, UserRole.ADMIN])),
):
    """Updates an existing MCP definition."""
    try:
        db_mcp = mcp_registry_service.update_mcp_definition_in_db(
            db=db, mcp_id_str=mcp_id, mcp_data=mcp_data
        )
        if not db_mcp:
            raise HTTPException(status_code=404, detail="MCP definition not found for update")
        # Only log audit if subject is a valid UUID
        try:
            user_id_val = uuid.UUID(current_user_sub)
        except Exception:
            user_id_val = None
        if user_id_val:
            log_audit_action(
                db,
                user_id=user_id_val,
                action_type="update_mcp",
                target_id=db_mcp.id,
                details=mcp_data.dict(),
            )
        return db_mcp
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/context/{mcp_id}", status_code=204)
async def delete_mcp_definition(
    mcp_id: str,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
    _: List[str] = Depends(require_any_role([UserRole.DEVELOPER, UserRole.ADMIN])),
):
    """Deletes an MCP definition."""
    try:
        success = mcp_registry_service.delete_mcp_definition_from_db(
            db=db, mcp_id_str=mcp_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="MCP definition not found for deletion")
        # Only log audit if subject is a valid UUID
        try:
            user_id_val = uuid.UUID(current_user_sub)
        except Exception:
            user_id_val = None
        if user_id_val:
            log_audit_action(
                db,
                user_id=user_id_val,
                action_type="delete_mcp",
                target_id=mcp_id,
                details={"mcp_id": mcp_id},
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_search_func():
    return mcp_registry_service.search_mcp_definitions_by_text


@app.get("/context/search", response_model=List[MCPListItem])
async def search_mcp_definitions(
    query: str,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
    limit: int = 10,
    search_func=Depends(get_search_func),
):
    """
    Searches for MCP definitions using semantic text search based on the query.
    Results are ordered by relevance.
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    db_mcps = search_func(db=db, query_text=query, limit=limit)

    response_items = []
    for mcp in db_mcps:
        latest_version_str = None
        if mcp.versions:
            latest_version_str = (
                mcp.versions[-1].version_str if mcp.versions else "N/A"
            )  # Simplified

        response_items.append(
            MCPListItem(
                id=mcp.id,
                name=mcp.name,
                type=MCPType(mcp.type),  # Convert string from DB to Enum
                description=mcp.description,
                tags=mcp.tags,
                latest_version_str=latest_version_str,
                updated_at=mcp.updated_at,
                # MCPListItem does not include embedding
            )
        )
    return response_items  # Always return 200 with a list (possibly empty)


@app.get("/health")
async def health_check():
    health = {
        "status": "healthy",
        "message": "Service is running",
        "database": "not_checked",
        "redis": "not_checked",
    }
    try:
        db = get_db_session()
        db.execute("SELECT 1")  # type: ignore
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
        "timestamp": datetime.now().isoformat(),
    }


# Prometheus metrics (ensure these are only registered once)
# The Instrumentator handles its own registration.
if not hasattr(
    app, "prometheus_instrumentator"
):  # Basic check to prevent re-instrumentation on reload
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        inprogress_name="mcp_inprogress_requests",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app)
    app.prometheus_instrumentator = instrumentator  # Mark as instrumented

# Configure structured logging (JSONFormatter might be defined elsewhere or simplified)
# Basic logger setup for now
logger = logging.getLogger("mcp_api")
logger.setLevel(os.getenv("MCP_LOG_LEVEL", "INFO").upper())
# Ensure handlers are not duplicated on reload if uvicorn handles logging setup
if not logger.hasHandlers():
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
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

@app.websocket("/ws/execution")
async def websocket_execution_endpoint(websocket: WebSocket):
    await websocket.accept()
    workflow_id = None
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # If the message is a status subscription, start sending updates
                if message.get("type") == "status" and "workflowId" in message.get("payload", {}):
                    workflow_id = message["payload"]["workflowId"]
                    # Start sending periodic updates (mock)
                    for i in range(5):  # Send 5 updates for demo; remove limit for real
                        await asyncio.sleep(1)
                        # Resource update
                        await websocket.send_text(json.dumps({
                            "type": "resource_update",
                            "payload": {
                                "cpu": 30 + i * 5,
                                "memory": 100 + i * 10,
                                "network": {"bytesIn": 1000 + i * 100, "bytesOut": 500 + i * 50}
                            },
                            "timestamp": int(time.time())
                        }))
                        # Execution update
                        await websocket.send_text(json.dumps({
                            "type": "execution_update",
                            "payload": {
                                "nodeId": f"step-{i+1}",
                                "status": "running" if i < 4 else "completed",
                                "progress": (i+1)*20,
                                "startTime": int(time.time()) - 10 + i,
                                "endTime": int(time.time()) if i == 4 else None
                            },
                            "timestamp": int(time.time())
                        }))
                        # Log message
                        await websocket.send_text(json.dumps({
                            "type": "log",
                            "payload": {
                                "timestamp": datetime.now().isoformat(),
                                "level": "INFO",
                                "message": f"Step {i+1} running",
                                "step_id": f"step-{i+1}"
                            },
                            "timestamp": int(time.time())
                        }))
                    # After updates, send a final status
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "payload": {"connected": True, "workflowId": workflow_id},
                        "timestamp": int(time.time())
                    }))
                else:
                    # Echo the message back as JSON
                    await websocket.send_text(json.dumps({"type": "echo", "payload": message, "timestamp": int(time.time())}))
            except json.JSONDecodeError:
                # Send an error message in JSON format
                await websocket.send_text(json.dumps({"type": "error", "payload": {"error": "Invalid JSON received"}, "timestamp": int(time.time())}))
    except WebSocketDisconnect:
        print("WebSocket disconnected")

@app.get("/api/dashboard/recommendations")
async def dashboard_recommendations():
    return [
        {
            "id": "1",
            "title": "Try the new Workflow Builder!",
            "description": "Build and automate workflows visually.",
            "confidence": 95,
            "type": "workflow"
        },
        {
            "id": "2",
            "title": "Optimize your pipeline",
            "description": "Check out trending components.",
            "confidence": 88,
            "type": "component"
        }
    ]

@app.get("/api/dashboard/trending")
async def dashboard_trending():
    return [
        {
            "id": "1",
            "name": "Data Cleaner",
            "description": "Cleans and preprocesses your data.",
            "usageCount": 120,
            "rating": 4.7
        },
        {
            "id": "2",
            "name": "Model Trainer",
            "description": "Trains ML models efficiently.",
            "usageCount": 98,
            "rating": 4.5
        }
    ]

@app.get("/api/dashboard/collaborations")
async def dashboard_collaborations():
    return [
        {
            "id": "1",
            "name": "Credit Approval Workflow",
            "lastModified": "2024-05-27T10:00:00Z",
            "collaborators": ["Alice", "Bob"],
            "type": "workflow"
        },
        {
            "id": "2",
            "name": "Data Cleaning Component",
            "lastModified": "2024-05-26T15:30:00Z",
            "collaborators": ["Charlie"],
            "type": "component"
        }
    ]

class ResourceUsageEntry(BaseModel):
    step_id: str
    label: str
    cpu: float  # percent
    memory: float  # MB

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    step_id: str = None

class StepHistoryEntry(BaseModel):
    step_id: str
    status: str
    started_at: str
    finished_at: str
    result: Any = None
    error: str = None

@app.get("/api/execution/runs/{run_id}/resource-usage", response_model=List[ResourceUsageEntry])
async def get_resource_usage(run_id: str):
    """Get resource usage (CPU, memory, etc.) for each step in a workflow run. (Mock data)"""
    # TODO: Integrate with real resource tracking
    return [
        ResourceUsageEntry(step_id="step-1", label="Step 1", cpu=32, memory=120),
        ResourceUsageEntry(step_id="step-2", label="Step 2", cpu=68, memory=210),
        ResourceUsageEntry(step_id="step-3", label="Step 3", cpu=15, memory=80),
    ]

@app.get("/api/execution/runs/{run_id}/logs", response_model=List[LogEntry])
async def get_run_logs(run_id: str):
    """Get logs for a workflow run. (Mock data, filter from log file in future)"""
    # TODO: Integrate with real log filtering by run_id
    return [
        LogEntry(timestamp="2024-05-30T10:00:00Z", level="INFO", message="Step 1 started", step_id="step-1"),
        LogEntry(timestamp="2024-05-30T10:00:01Z", level="INFO", message="Step 1 completed", step_id="step-1"),
        LogEntry(timestamp="2024-05-30T10:00:02Z", level="INFO", message="Step 2 started", step_id="step-2"),
        LogEntry(timestamp="2024-05-30T10:00:03Z", level="ERROR", message="Step 2 failed: OOM", step_id="step-2"),
    ]

@app.get("/api/execution/runs/{run_id}/history", response_model=List[StepHistoryEntry])
async def get_run_history(run_id: str):
    """Get step-by-step execution history for a workflow run. (Mock data)"""
    # TODO: Integrate with real execution history
    return [
        StepHistoryEntry(step_id="step-1", status="completed", started_at="2024-05-30T10:00:00Z", finished_at="2024-05-30T10:00:01Z", result={"output": "ok"}),
        StepHistoryEntry(step_id="step-2", status="failed", started_at="2024-05-30T10:00:02Z", finished_at="2024-05-30T10:00:03Z", error="OOM"),
    ]
