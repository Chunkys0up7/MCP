from typing import Dict, Any
import os
from .base import BaseMCP
from ..core.types import PythonScriptConfig, MCPResult
from ..api.client import client
from ..core.config import config

class PythonScriptMCP(BaseMCP):
    """Python Script MCP implementation."""
    
    def __init__(self, config: PythonScriptConfig):
        super().__init__(config)
        self.config: PythonScriptConfig = config
    
    def validate_config(self) -> bool:
        """Validate the Python Script configuration."""
        try:
            # Check if script exists
            if not os.path.exists(self.config.script_path):
                print(f"Script not found: {self.config.script_path}")
                return False
            
            # Validate timeout
            if self.config.timeout < 60:
                print("Timeout must be at least 60 seconds")
                return False
            
            # Validate requirements if virtual environment is enabled
            if self.config.virtual_env and not self.config.requirements:
                print("Requirements must be specified when using virtual environment")
                return False
            
            return True
        except Exception as e:
            print(f"Error validating config: {str(e)}")
            return False
    
    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the Python Script MCP."""
        if not self.id:
            return MCPResult(success=False, error="MCP not created")
        
        try:
            return client.execute_server(self.id, inputs)
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