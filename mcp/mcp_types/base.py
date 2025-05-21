import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..core.types import MCPConfig, MCPResult
from ..api.client import MCPClient
from ..api.exceptions import MCPAPIError, MCPNotFoundError, MCPValidationError

logger = logging.getLogger(__name__)

class BaseMCP(ABC):
    """Base class for all MCP types."""
    
    def __init__(self, config: MCPConfig, client: MCPClient):
        self.config = config
        self._id: Optional[str] = None
        self.client: MCPClient = client
    
    @property
    def id(self) -> Optional[str]:
        """Get the MCP server ID."""
        return self._id
    
    @id.setter
    def id(self, value: str):
        """Set the MCP server ID."""
        self._id = value
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the MCP with given inputs."""
        pass
    
    def create(self) -> bool:
        """Create the MCP server."""
        try:
            mcp_type_value = self.config.type.value if hasattr(self.config.type, 'value') else self.config.type

            result = self.client.create_server(
                name=self.config.name,
                mcp_type=mcp_type_value,
                description=self.config.description,
                specific_config_dict=self.config.model_dump(exclude_none=True)
            )
            
            if result and result.get('id'):
                self.id = result.get('id')
                return True
            logger.error(f"MCP creation via API did not return an ID or success. Result: {result}")
            return False
        except (MCPAPIError, MCPNotFoundError, MCPValidationError) as api_e:
            logger.error(f"API Error during MCP creation: {str(api_e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating MCP: {str(e)}")
            raise MCPAPIError(f"Unexpected error during MCP creation: {str(e)}")
    
    def delete(self) -> bool:
        """Delete the MCP server."""
        if not self.id:
            logger.warning("Attempted to delete MCP with no ID set.")
            return False
        
        try:
            return self.client.delete_server(self.id)
        except Exception as e:
            logger.error(f"Error deleting MCP {self.id}: {str(e)}")
            return False
    
    def get_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the MCP server."""
        if not self.id:
            logger.warning("Attempted to get info for MCP with no ID set.")
            return None
        
        try:
            return self.client.get_server(self.id)
        except Exception as e:
            logger.error(f"Error getting MCP info for {self.id}: {str(e)}")
            return None 