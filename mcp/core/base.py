from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class MCPConfig(BaseModel):
    """Base configuration model for MCPs.
    
    This class defines the common configuration structure that all MCPs must follow.
    It provides basic metadata and parameter storage capabilities.
    
    Attributes:
        name (str): The name of the MCP.
        description (Optional[str]): Optional description of the MCP's purpose.
        version (str): Version of the MCP. Defaults to "1.0.0".
        parameters (Dict[str, Any]): Additional configuration parameters. Defaults to empty dict.
    """
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    parameters: Dict[str, Any] = {}

class BaseMCP(ABC):
    """Base class for all MCP implementations.
    
    This abstract base class defines the interface that all MCPs must implement.
    It provides common functionality for configuration validation and metadata access.
    
    Attributes:
        config (MCPConfig): The configuration for this MCP instance.
    """
    
    def __init__(self, config: MCPConfig):
        """Initialize the base MCP.
        
        Args:
            config (MCPConfig): The configuration for this MCP.
            
        Raises:
            ValueError: If the configuration is invalid.
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the MCP with given inputs.
        
        This method must be implemented by all MCP subclasses. It defines how the MCP
        processes its inputs and produces outputs.
        
        Args:
            inputs (Dict[str, Any]): Dictionary of input parameters for the MCP.
            
        Returns:
            Dict[str, Any]: Dictionary containing execution results.
            
        Raises:
            Exception: If execution fails for any reason.
        """
        pass
    
    def _validate_config(self) -> None:
        """Validate the MCP configuration.
        
        This method ensures that the MCP's configuration is valid. It checks for
        required fields and performs any necessary validation.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if not self.config.name:
            raise ValueError("MCP name is required")
    
    @property
    def name(self) -> str:
        """Get the MCP name.
        
        Returns:
            str: The name of the MCP.
        """
        return self.config.name
    
    @property
    def description(self) -> Optional[str]:
        """Get the MCP description.
        
        Returns:
            Optional[str]: The description of the MCP, if any.
        """
        return self.config.description
    
    @property
    def version(self) -> str:
        """Get the MCP version.
        
        Returns:
            str: The version of the MCP.
        """
        return self.config.version 