from typing import Dict, Any, List, Optional
import requests
import logging
import traceback
from ..core.config import config
from ..core.types import MCPConfig, MCPResult
from .exceptions import MCPAPIError, MCPNotFoundError, MCPValidationError

# Use a more unique name for the logger
MCP_CLIENT_SPECIFIC_LOGGER = logging.getLogger("MCPClient_API") 
# Log initial type and ID of the logger when module is loaded
MCP_CLIENT_SPECIFIC_LOGGER.debug(f"MCP_CLIENT_SPECIFIC_LOGGER initialized. Type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")

class MCPClient:
    """Client for interacting with MCP API."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or config.api_base_url
        self.api_key = api_key or config.api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"MCPClient instance created. Logger type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        # Log type and ID of the logger at the beginning of the method call
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"_handle_response received response with status: {response.status_code} from URL: {response.url}")
        if response.status_code == 404:
            MCP_CLIENT_SPECIFIC_LOGGER.error(f"MCPNotFoundError for URL: {response.url}")
            raise MCPNotFoundError(f"Resource not found: {response.url}")
        elif response.status_code == 400:
            MCP_CLIENT_SPECIFIC_LOGGER.error(f"MCPValidationError for URL: {response.url}. Response text: {response.text}")
            raise MCPValidationError(f"Validation error: {response.text}")
        elif response.status_code >= 400:
            MCP_CLIENT_SPECIFIC_LOGGER.error(f"MCPAPIError for URL: {response.url}. Status: {response.status_code}. Response text: {response.text}")
            raise MCPAPIError(f"API error: {response.text}")
        
        try:
            MCP_CLIENT_SPECIFIC_LOGGER.debug(f"Type of 'response' object in _handle_response BEFORE .json() call: {type(response)}")
            MCP_CLIENT_SPECIFIC_LOGGER.debug(f"_handle_response raw response text: {response.text}")
            json_response = response.json()
            try:
                MCP_CLIENT_SPECIFIC_LOGGER.debug(f"_handle_response: successfully parsed JSON. Type of json_response: {type(json_response)}")
            except AttributeError as ae_type_log:
                MCP_CLIENT_SPECIFIC_LOGGER.error(f"AttributeError SPECIFICALLY WHEN LOGGING type(json_response): {str(ae_type_log)}")
                MCP_CLIENT_SPECIFIC_LOGGER.error(f"Type of json_response at this point was: {type(json_response)}")
                MCP_CLIENT_SPECIFIC_LOGGER.error(f"Content of json_response: {json_response}")
                raise
            
            MCP_CLIENT_SPECIFIC_LOGGER.debug(f"_handle_response content being returned: {json_response}")
            return json_response
        except requests.exceptions.JSONDecodeError as e:
            MCP_CLIENT_SPECIFIC_LOGGER.error(f"JSONDecodeError in _handle_response for URL: {response.url}. Error: {str(e)}. Response text: {response.text}")
            raise MCPAPIError(f"Failed to decode JSON response from {response.url}: {str(e)}. Response text: {response.text}")
        except AttributeError as ae_general: # Catch any other AttributeErrors in this block
            MCP_CLIENT_SPECIFIC_LOGGER.error(f"A GENERAL AttributeError occurred in _handle_response try block: {str(ae_general)}")
            MCP_CLIENT_SPECIFIC_LOGGER.error(traceback.format_exc()) # Ensure traceback is imported
            raise
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """Get all MCP servers."""
        url = f"{self.base_url}/context"
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"get_servers attempting to GET from URL: {url}. Logger type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")
        try:
            response = requests.get(
                url,
                headers=self.headers
            )
            MCP_CLIENT_SPECIFIC_LOGGER.debug(f"get_servers received response. Status: {response.status_code}, URL: {response.url}")
        except requests.exceptions.RequestException as e:
            MCP_CLIENT_SPECIFIC_LOGGER.error(f"RequestException in get_servers for URL: {url}. Error: {str(e)}")
            raise MCPAPIError(f"Request failed for {url}: {str(e)}")
            
        data = self._handle_response(response)
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"get_servers received data from _handle_response.")
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"Type of data: {type(data)}")
        # MCP_CLIENT_SPECIFIC_LOGGER.debug(f"Content of data: {data}") # Temporarily comment out to isolate error
        MCP_CLIENT_SPECIFIC_LOGGER.debug("get_servers is about to return data.")
        return data
    
    def create_server(self, name: str, mcp_type: str, description: Optional[str], specific_config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new MCP server."""
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"create_server called for name: {name}, type: {mcp_type}. Logger type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")
        
        payload = {
            "name": name,
            "type": mcp_type, # This should be the string value of the MCPType enum
            "description": description,
            "config": specific_config_dict # This is the dict of type-specific params
        }
        
        response = requests.post(
            f"{self.base_url}/context", # Corrected URL
            headers=self.headers,
            json=payload # Send the constructed payload
        )
        return self._handle_response(response)
    
    def delete_server(self, server_id: str) -> bool:
        """Delete an MCP server."""
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"delete_server called for ID: {server_id}. Logger type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")
        try:
            response = requests.delete(
                f"{self.base_url}/context/{server_id}",
                headers=self.headers
            )
            if response.status_code == 204: # No Content, successful deletion
                return True
            elif response.status_code == 404:
                MCP_CLIENT_SPECIFIC_LOGGER.error(f"MCPNotFoundError for delete URL: {response.url}")
                raise MCPNotFoundError(f"Server ID '{server_id}' not found for deletion.")
            else:
                # Attempt to parse error detail from JSON response, fallback to raw text
                try:
                    error_detail = response.json().get('detail', response.text)
                except requests.exceptions.JSONDecodeError:
                    error_detail = response.text
                MCP_CLIENT_SPECIFIC_LOGGER.error(f"MCPAPIError for delete URL: {response.url}. Status: {response.status_code}. Detail: {error_detail}")
                raise MCPAPIError(f"Failed to delete server '{server_id}'. Status: {response.status_code}. Error: {error_detail}")
        except requests.exceptions.RequestException as e:
            MCP_CLIENT_SPECIFIC_LOGGER.error(f"RequestException in delete_server for ID {server_id}. Error: {str(e)}")
            raise MCPAPIError(f"Request failed while trying to delete server '{server_id}': {str(e)}")
    
    def execute_server(self, server_id: str, inputs: Dict[str, Any]) -> MCPResult:
        """Execute an MCP server with given inputs."""
        try:
            response = requests.post(
                f"{self.base_url}/context/{server_id}/execute",
                headers=self.headers,
                json=inputs
            )
            data = self._handle_response(response)
            
            if not isinstance(data, dict):
                raise MCPAPIError(f"Invalid response format from API: {data}")
                
            # Backend should always return fields according to MCPResult model.
            # Pydantic will validate upon instantiation.
            # if 'success' not in data:
            #     data['success'] = True # Should not be needed
            # if 'error' not in data:
            #     data['error'] = None   # Should not be needed
                
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
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"execute_llm_prompt called. Logger type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")
        return self.execute_server(config.id, inputs)

    async def execute_notebook(self, config, inputs):
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"execute_notebook called. Logger type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")
        return self.execute_server(config.id, inputs)

    async def execute_script(self, config, inputs):
        MCP_CLIENT_SPECIFIC_LOGGER.debug(f"execute_script called. Logger type: {type(MCP_CLIENT_SPECIFIC_LOGGER)}, ID: {id(MCP_CLIENT_SPECIFIC_LOGGER)}")
        return self.execute_server(config.id, inputs)

# Remove global client instance
# client = MCPClient() 
if __name__ == "__main__":
    # Basic setup for standalone testing of the client, if ever needed.
    logging.basicConfig(level=logging.DEBUG)
    MCP_CLIENT_SPECIFIC_LOGGER.info("MCPClient module run directly. This is for testing only.")
    # test_client = MCPClient(base_url="http://localhost:8000")
    # try:
    #     servers = test_client.get_servers()
    #     MCP_CLIENT_SPECIFIC_LOGGER.info(f"Standalone test get_servers(): {servers}")
    # except Exception as e:
    #     MCP_CLIENT_SPECIFIC_LOGGER.error(f"Standalone test error: {e}")
    pass 