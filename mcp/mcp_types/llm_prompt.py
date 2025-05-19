from typing import Dict, Any
from .base import BaseMCP
from ..core.types import LLMPromptConfig, MCPResult
from ..api.client import client

class LLMPromptMCP(BaseMCP):
    """LLM Prompt MCP implementation."""
    
    def __init__(self, config: LLMPromptConfig):
        super().__init__(config)
        self.config: LLMPromptConfig = config
    
    def validate_config(self) -> bool:
        """Validate the LLM Prompt configuration."""
        try:
            # Check required fields
            if not self.config.template:
                print("Template is required")
                return False
            
            if not self.config.model_name:
                print("Model name is required")
                return False
            
            # Validate temperature
            if not 0 <= self.config.temperature <= 1:
                print("Temperature must be between 0 and 1")
                return False
            
            # Validate max tokens
            if self.config.max_tokens < 1:
                print("Max tokens must be greater than 0")
                return False
            
            return True
        except Exception as e:
            print(f"Error validating config: {str(e)}")
            return False
    
    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the LLM Prompt MCP."""
        if not self.id:
            return MCPResult(success=False, error="MCP not created")
        
        try:
            return client.execute_server(self.id, inputs)
        except Exception as e:
            return MCPResult(success=False, error=str(e)) 