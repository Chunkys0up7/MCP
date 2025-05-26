from typing import Any, Dict

from ..api.client import MCPClient
from ..core.types import LLMPromptConfig, MCPResult
from .base import BaseMCP


class LLMPromptMCP(BaseMCP):
    """LLM Prompt MCP implementation."""

    def __init__(self, config: LLMPromptConfig, client: MCPClient):
        super().__init__(config, client)
        self.config: LLMPromptConfig = config

    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the LLM Prompt MCP."""
        if not self.id:
            return MCPResult(
                success=False, error="MCP not created or ID not set for execution"
            )

        try:
            return self.client.execute_server(self.id, inputs)
        except Exception as e:
            return MCPResult(success=False, error=str(e))
