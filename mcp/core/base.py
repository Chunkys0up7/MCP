from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from mcp.core.types import BaseMCPConfig

class BaseMCPServer(ABC):
    """Base class for all MCP server implementations.
    
    This abstract base class defines the interface that all MCP servers must implement.
    It provides common functionality for context management, model interaction, and tool integration.
    
    Attributes:
        config (MCPConfig): The configuration for this MCP server instance.
    """
    
    def __init__(self, config: BaseMCPConfig):
        """Initialize the base MCP server.
        
        Args:
            config (BaseMCPConfig): The configuration for this MCP server.
            
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
        if not self.config.type:
            raise ValueError("MCP server type is required")
    
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
    
    # Removing the version property as it's not in types.BaseMCPConfig
    # @property
    # def version(self) -> str:
    #     """Get the MCP server version.
    #     
    #     Returns:
    #         str: The version of the MCP server.
    #     """
    #     return self.config.version 