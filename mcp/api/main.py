from fastapi import FastAPI, HTTPException, Depends, Security
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

from ..core.base import MCPConfig, BaseMCPServer
from ..core.llm_prompt import LLMPromptMCP, LLMPromptConfig
from ..core.jupyter_notebook import JupyterNotebookMCP, JupyterNotebookConfig
from ..core.python_script import PythonScriptMCP, PythonScriptConfig
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

# Enable CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
from fastapi import Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict

# Simple in-memory rate limiting
RATE_LIMIT = 100  # requests per minute
rate_limit_store = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] 
                                  if current_time - t < 60]
    
    # Check rate limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

# MCP server registry and persistence
MCP_STORAGE_FILE = Path(__file__).parent.parent.parent / "mcp_storage.json"

def load_mcp_servers() -> Dict[str, Any]:
    """Load MCP servers from storage file"""
    print(f"[DEBUG] MCP_STORAGE_FILE absolute path: {MCP_STORAGE_FILE.resolve()}")
    if MCP_STORAGE_FILE.exists():
        with open(MCP_STORAGE_FILE, 'r') as f:
            data = json.load(f)
            print(f"[DEBUG] Raw data loaded from storage: {data}")
            # Recreate MCP server instances
            for server_id, server_data in data.items():
                try:
                    config = server_data["config"].copy()
                    
                    # Add required fields based on type
                    if server_data["type"] == "llm_prompt":
                        config["model_id"] = config.get("model_name", "claude-3-sonnet-20240229")
                        config["context_type"] = "memory"
                        config_obj = LLMPromptConfig(**config)
                        server_data["instance"] = LLMPromptMCP(config_obj)
                    elif server_data["type"] == "jupyter_notebook":
                        config["model_id"] = "jupyter"
                        config["context_type"] = "file"
                        config_obj = JupyterNotebookConfig(**config)
                        server_data["instance"] = JupyterNotebookMCP(config_obj)
                    elif server_data["type"] == "python_script":
                        config["model_id"] = "python"
                        config["context_type"] = "file"
                        config_obj = PythonScriptConfig(**config)
                        server_data["instance"] = PythonScriptMCP(config_obj)
                except Exception as e:
                    print(f"[ERROR] Failed to recreate MCP instance for {server_id}: {str(e)}")
                    continue
            return data
    print("[DEBUG] MCP_STORAGE_FILE does not exist!")
    return {}

def save_mcp_servers(servers: Dict[str, Any]):
    """Save MCP servers to storage file"""
    # Convert to serializable format
    serializable_servers = {}
    for server_id, server_data in servers.items():
        # Create a copy of the config to modify
        config = server_data["config"].copy()
        
        serializable_servers[server_id] = {
            "id": server_data["id"],
            "name": server_data["name"],
            "description": server_data["description"],
            "type": server_data["type"],
            "config": config
        }
    
    with open(MCP_STORAGE_FILE, 'w') as f:
        json.dump(serializable_servers, f, indent=2)

# Initialize MCP server registry from storage
mcp_server_registry: Dict[str, Any] = load_mcp_servers()

class MCPRequest(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    config: Optional[dict] = None

@app.get("/context")
async def get_context():
    """Get all MCP server instances"""
    return {"servers": [
        {
            "id": server_id,
            "name": server["name"],
            "description": server["description"],
            "type": server["type"],
            "config": server["config"]
        }
        for server_id, server in mcp_server_registry.items()
    ]}

@app.post("/context", response_model=Dict[str, Any])
async def create_server(request: MCPRequest):
    """Create a new MCP server"""
    try:
        server_id = str(uuid.uuid4())  # Generate a unique ID
        if request.type == "llm_prompt":
            if not request.config:
                raise HTTPException(status_code=400, detail="Config is required for LLM Prompt MCP")
            
            # Set default model name if not provided
            if "model_name" not in request.config:
                request.config["model_name"] = "claude-3-sonnet-20240229"
            
            # Add required fields
            request.config["model_id"] = request.config.get("model_name", "claude-3-sonnet-20240229")
            request.config["context_type"] = "memory"
            
            config = LLMPromptConfig(**request.config)
            server = LLMPromptMCP(config)
            mcp_server_registry[server_id] = {
                "id": server_id,
                "name": request.name,
                "description": request.description,
                "type": request.type,
                "config": request.config,
                "instance": server
            }
            # Save to storage
            save_mcp_servers(mcp_server_registry)
            return {
                "id": server_id,
                "name": request.name,
                "type": request.type,
                "description": request.description,
                "config": request.config
            }
        elif request.type == "jupyter_notebook":
            if not request.config:
                raise HTTPException(status_code=400, detail="Config is required for Jupyter Notebook MCP")
            
            # Add required fields
            request.config["model_id"] = "jupyter"
            request.config["context_type"] = "file"
            
            config = JupyterNotebookConfig(**request.config)
            server = JupyterNotebookMCP(config)
            mcp_server_registry[server_id] = {
                "id": server_id,
                "name": request.name,
                "description": request.description,
                "type": request.type,
                "config": request.config,
                "instance": server
            }
            # Save to storage
            save_mcp_servers(mcp_server_registry)
            return {
                "id": server_id,
                "name": request.name,
                "type": request.type,
                "description": request.description,
                "config": request.config
            }
        elif request.type == "python_script":
            if not request.config:
                raise HTTPException(status_code=400, detail="Config is required for Python Script MCP")
            
            # Add required fields
            request.config["model_id"] = "python"
            request.config["context_type"] = "file"
            
            config = PythonScriptConfig(**request.config)
            server = PythonScriptMCP(config)
            mcp_server_registry[server_id] = {
                "id": server_id,
                "name": request.name,
                "description": request.description,
                "type": request.type,
                "config": request.config,
                "instance": server
            }
            # Save to storage
            save_mcp_servers(mcp_server_registry)
            return {
                "id": server_id,
                "name": request.name,
                "type": request.type,
                "description": request.description,
                "config": request.config
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported MCP server type: {request.type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context/{server_id}/execute", response_model=MCPResult)
async def execute_server(server_id: str, inputs: Dict[str, Any] = None):
    """Execute an MCP server with the given inputs."""
    try:
        server = mcp_server_registry.get(server_id)
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        raw_result = await server["instance"].execute(inputs or {})
        if isinstance(raw_result, dict):
            result = raw_result.get("result")
            if result is None and "output" in raw_result:
                result = raw_result["output"]
            error = raw_result.get("error")
            context = raw_result.get("context", {})
            stdout = raw_result.get("stdout")
            stderr = raw_result.get("stderr")
            success = error is None and (result is not None or stdout is not None)
        else:
            result = raw_result
            error = None
            context = {}
            stdout = None
            stderr = None
            success = True
        return {
            "success": success,
            "result": result,
            "error": error,
            "context": context,
            "stdout": stdout,
            "stderr": stderr
        }
    except Exception as e:
        logger.error(f"Error executing server {server_id}: {str(e)}")
        return {
            "success": False,
            "result": None,
            "error": str(e),
            "context": {},
            "stdout": None,
            "stderr": None
        }

@app.delete("/context/{server_id}")
async def delete_mcp_server(server_id: str, api_key: str = Depends(get_api_key)):
    """Delete an MCP server by ID."""
    if server_id not in mcp_server_registry:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    # Remove from storage
    save_mcp_servers(mcp_server_registry)
    
    # Remove from memory
    del mcp_server_registry[server_id]
    
    return {"message": f"MCP server {server_id} deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health = {"status": "healthy", "message": "Service is running"}
    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health["database"] = "ok"
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"
    # Check Redis
    try:
        redis = RedisCacheManager()
        redis.ping()
        health["redis"] = "ok"
    except Exception as e:
        health["redis"] = f"error: {str(e)}"
        health["status"] = "degraded"
    return health

@app.get("/stats")
async def get_stats():
    """Get statistics about MCP servers"""
    try:
        servers = load_mcp_servers()
        
        # Count servers by type
        type_counts = {}
        for server in servers.values():
            server_type = server["type"]
            type_counts[server_type] = type_counts.get(server_type, 0) + 1
            
        # Get model usage statistics
        model_usage = {}
        for server in servers.values():
            if "config" in server and "model_name" in server["config"]:
                model = server["config"]["model_name"]
                model_usage[model] = model_usage.get(model, 0) + 1
                
        return {
            "total_servers": len(servers),
            "server_types": type_counts,
            "model_usage": model_usage,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Prometheus metrics
REQUEST_COUNT = Counter(
    'mcp_request_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'mcp_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

SERVER_EXECUTION_COUNT = Counter(
    'mcp_server_execution_total',
    'Total number of server executions',
    ['server_type', 'status']
)

SERVER_EXECUTION_LATENCY = Histogram(
    'mcp_server_execution_latency_seconds',
    'Server execution latency in seconds',
    ['server_type']
)

# Initialize Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Configure structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": getattr(record, "request_id", None),
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)

# Configure logger
logger = logging.getLogger("mcp")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Request ID middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info("Request started", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host
    })
    
    try:
        response = await call_next(request)
        logger.info("Request completed", extra={
            "request_id": request_id,
            "status_code": response.status_code
        })
        return response
    except Exception as e:
        logger.error("Request failed", extra={
            "request_id": request_id,
            "error": str(e)
        })
        raise 