class MCPError(Exception):
    """Base exception for MCP errors."""
    pass

class MCPAPIError(MCPError):
    """Exception raised for API errors."""
    pass

class MCPNotFoundError(MCPError):
    """Exception raised when a resource is not found."""
    pass

class MCPValidationError(MCPError):
    """Exception raised for validation errors."""
    pass

class MCPExecutionError(MCPError):
    """Exception raised when MCP execution fails."""
    pass 