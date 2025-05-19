from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..core.types import MCPConfig, MCPResult
from ..api.client import client

class BaseMCP(ABC):
    """Base class for all MCP types."""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self._id: Optional[str] = None
    
    @property
    def id(self) -> Optional[str]:
        """Get the MCP server ID."""
        return self._id
    
    @id.setter
    def id(self, value: str):
        """Set the MCP server ID."""
        self._id = value
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the MCP configuration."""
        pass
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the MCP with given inputs."""
        pass
    
    def create(self) -> bool:
        """Create the MCP server."""
        if not self.validate_config():
            return False
        
        try:
            result = client.create_server(self.config)
            self.id = result.get('id')
            return True
        except Exception as e:
            print(f"Error creating MCP: {str(e)}")
            return False
    
    def delete(self) -> bool:
        """Delete the MCP server."""
        if not self.id:
            return False
        
        try:
            return client.delete_server(self.id)
        except Exception as e:
            print(f"Error deleting MCP: {str(e)}")
            return False
    
    def get_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the MCP server."""
        if not self.id:
            return None
        
        try:
            return client.get_server(self.id)
        except Exception as e:
            print(f"Error getting MCP info: {str(e)}")
            return None 