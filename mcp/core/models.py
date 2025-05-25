from typing import Any, Dict, Optional

from pydantic import BaseModel


class MCPResult(BaseModel):
    """Model for MCP execution results."""

    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
