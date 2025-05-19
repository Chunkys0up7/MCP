from pydantic import BaseModel
from typing import Dict, Any, Optional

class MCPResult(BaseModel):
    """Model for MCP execution results."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None 