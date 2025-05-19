from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel

class MCPConfig(BaseModel):
    """Base configuration model for MCP servers.
    
    This class defines the common configuration structure that all MCP servers must follow.
    It provides configuration for model interactions, context management, and tool integration.
    
    Attributes:
        name (str): The name of the MCP server.
        description (Optional[str]): Optional description of the MCP server's purpose.
        version (str): Version of the MCP server. Defaults to "1.0.0".
        model_id (str): The ID of the AI model this server interfaces with.
        context_type (str): The type of context management (e.g., "memory", "database", "file").
        tool_configurations (Dict[str, Any]): Configuration for integrated tools. Defaults to empty dict.
    """
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    model_id: str
    context_type: str
    tool_configurations: Dict[str, Any] = {}

class BaseMCPServer(ABC):
    """Base class for all MCP server implementations.
    
    This abstract base class defines the interface that all MCP servers must implement.
    It provides common functionality for context management, model interaction, and tool integration.
    
    Attributes:
        config (MCPConfig): The configuration for this MCP server instance.
    """
    
    def __init__(self, config: MCPConfig):
        """Initialize the base MCP server.
        
        Args:
            config (MCPConfig): The configuration for this MCP server.
            
        Raises:
            ValueError: If the configuration is invalid.
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the MCP server with given inputs.
        
        This method must be implemented by all MCP server subclasses. It defines how the server
        processes inputs, manages context, and interacts with the AI model.
        
        Args:
            inputs (Dict[str, Any]): Dictionary of input parameters for the MCP server.
            
        Returns:
            Dict[str, Any]: Dictionary containing execution results.
            
        Raises:
            Exception: If execution fails for any reason.
        """
        pass
    
    def _validate_config(self) -> None:
        """Validate the MCP server configuration.
        
        This method ensures that the MCP server's configuration is valid. It checks for
        required fields and performs any necessary validation.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if not self.config.name:
            raise ValueError("MCP server name is required")
        if not self.config.model_id:
            raise ValueError("Model ID is required")
        if not self.config.context_type:
            raise ValueError("Context type is required")
    
    @property
    def name(self) -> str:
        """Get the MCP server name.
        
        Returns:
            str: The name of the MCP server.
        """
        return self.config.name
    
    @property
    def description(self) -> Optional[str]:
        """Get the MCP server description.
        
        Returns:
            Optional[str]: The description of the MCP server, if any.
        """
        return self.config.description
    
    @property
    def version(self) -> str:
        """Get the MCP server version.
        
        Returns:
            str: The version of the MCP server.
        """
        return self.config.version 