from typing import Dict, Any, List, Optional
import requests
from ..core.config import config
from ..core.types import MCPConfig, MCPResult
from .exceptions import MCPAPIError, MCPNotFoundError, MCPValidationError

class MCPClient:
    """Client for interacting with MCP API."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or config.api_base_url
        self.api_key = api_key or config.api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 404:
            raise MCPNotFoundError(f"Resource not found: {response.url}")
        elif response.status_code == 400:
            raise MCPValidationError(f"Validation error: {response.text}")
        elif response.status_code >= 400:
            raise MCPAPIError(f"API error: {response.text}")
        
        return response.json()
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """Get all MCP servers."""
        response = requests.get(
            f"{self.base_url}/context",
            headers=self.headers
        )
        data = self._handle_response(response)
        return data.get('servers', [])
    
    def create_server(self, config: MCPConfig) -> Dict[str, Any]:
        """Create a new MCP server."""
        response = requests.post(
            f"{self.base_url}/mcps",
            headers=self.headers,
            json=config.dict()
        )
        return self._handle_response(response)
    
    def delete_server(self, server_id: str) -> bool:
        """Delete an MCP server."""
        response = requests.delete(
            f"{self.base_url}/context/{server_id}",
            headers=self.headers
        )
        return response.status_code == 200
    
    def execute_server(self, server_id: str, inputs: Dict[str, Any]) -> MCPResult:
        """Execute an MCP server with given inputs."""
        try:
            response = requests.post(
                f"{self.base_url}/context/{server_id}/execute",
                headers=self.headers,
                json=inputs
            )
            data = self._handle_response(response)
            
            # Ensure the response has the required fields
            if not isinstance(data, dict):
                raise MCPAPIError(f"Invalid response format: {data}")
                
            # Add success field if not present
            if 'success' not in data:
                data['success'] = True
                
            # Add error field if not present
            if 'error' not in data:
                data['error'] = None
                
            return MCPResult(**data)
        except requests.exceptions.RequestException as e:
            raise MCPAPIError(f"Failed to execute server: {str(e)}")
        except Exception as e:
            raise MCPAPIError(f"Unexpected error during execution: {str(e)}")
    
    def get_server(self, server_id: str) -> Dict[str, Any]:
        """Get a specific MCP server."""
        response = requests.get(
            f"{self.base_url}/context/{server_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    async def execute_llm_prompt(self, config, inputs):
        return self.execute_server(config.id, inputs)

    async def execute_notebook(self, config, inputs):
        return self.execute_server(config.id, inputs)

    async def execute_script(self, config, inputs):
        return self.execute_server(config.id, inputs)

# Create global client instance
client = MCPClient() 