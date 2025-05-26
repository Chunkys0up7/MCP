class MCPError(Exception):
    """Base exception for MCP errors."""



class MCPAPIError(MCPError):
    """Exception raised for API errors."""



class MCPNotFoundError(MCPError):
    """Exception raised when a resource is not found."""



class MCPValidationError(MCPError):
    """Exception raised for validation errors."""



class MCPExecutionError(MCPError):
    """Exception raised when MCP execution fails."""

