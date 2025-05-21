from typing import Dict, Any
import os
from .base import BaseMCP
from ..core.types import PythonScriptConfig, MCPResult
from ..api.client import MCPClient
from ..core.config import config

class PythonScriptMCP(BaseMCP):
    """Python Script MCP implementation."""
    
    def __init__(self, config: PythonScriptConfig, client: MCPClient):
        super().__init__(config, client)
        self.config: PythonScriptConfig = config
    
    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the Python Script MCP."""
        if not self.id:
            return MCPResult(success=False, error="MCP not created or ID not set for execution")
        
        try:
            return self.client.execute_server(self.id, inputs)
        except Exception as e:
            return MCPResult(success=False, error=str(e))
    
    def create_script(self, name: str, content: str) -> bool:
        """Create a new Python script."""
        try:
            script_path = os.path.join(config.scripts_dir, f"{name}.py")
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(content)
            
            self.config.script_path = script_path
            return True
        except Exception as e:
            print(f"Error creating script: {str(e)}")
            return False
    
    def create_requirements_file(self) -> bool:
        """Create requirements.txt file for the script."""
        if not self.config.requirements:
            return True
        
        try:
            requirements_path = os.path.join(
                os.path.dirname(self.config.script_path),
                'requirements.txt'
            )
            
            with open(requirements_path, 'w') as f:
                f.write('\n'.join(self.config.requirements))
            
            return True
        except Exception as e:
            print(f"Error creating requirements file: {str(e)}")
            return False 