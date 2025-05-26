from typing import Any, Dict

from ..api.client import MCPClient
from ..core.types import AIAssistantConfig, MCPResult  # Use AIAssistantConfig
from .base import BaseMCP


class AIAssistantMCP(BaseMCP):
    """AI Assistant MCP (UI Facade)."""

    def __init__(self, config: AIAssistantConfig, client: MCPClient):
        super().__init__(config, client)
        self.config: AIAssistantConfig = config  # Specific type hint

    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the AI Assistant MCP.
        `inputs` is expected to contain a 'message' field.
        """
        if not self.id:
            return MCPResult(
                success=False, error="MCP not created or ID not set for execution"
            )

        # The client.execute_server will send the `inputs` dict as JSON body.
        # The backend AIAssistantMCP.execute expects {"message": "user_query"}
        if "message" not in inputs:
            return MCPResult(
                success=False,
                error="Input must contain a 'message' field for AI Assistant.",
            )

        try:
            return self.client.execute_server(self.id, inputs)
        except Exception as e:
            # Consider logging here as well, or let client handle all logging
            return MCPResult(success=False, error=str(e))
