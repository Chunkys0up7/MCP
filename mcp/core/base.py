from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class MCPConfig(BaseModel):
    """Base configuration model for MCPs"""
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    parameters: Dict[str, Any] = {}

class BaseMCP(ABC):
    """Base class for all MCP implementations"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the MCP with given inputs
        
        Args:
            inputs: Dictionary of input parameters
            
        Returns:
            Dictionary containing execution results
        """
        pass
    
    def _validate_config(self) -> None:
        """Validate the MCP configuration
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config.name:
            raise ValueError("MCP name is required")
    
    @property
    def name(self) -> str:
        """Get the MCP name"""
        return self.config.name
    
    @property
    def description(self) -> Optional[str]:
        """Get the MCP description"""
        return self.config.description
    
    @property
    def version(self) -> str:
        """Get the MCP version"""
        return self.config.version 