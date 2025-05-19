from typing import Dict, Any
import os
from .base import BaseMCP
from ..core.types import JupyterNotebookConfig, MCPResult
from ..api.client import client
from ..core.config import config

class JupyterNotebookMCP(BaseMCP):
    """Jupyter Notebook MCP implementation."""
    
    def __init__(self, config: JupyterNotebookConfig):
        super().__init__(config)
        self.config: JupyterNotebookConfig = config
    
    def validate_config(self) -> bool:
        """Validate the Jupyter Notebook configuration."""
        try:
            # Check if notebook exists
            if not os.path.exists(self.config.notebook_path):
                print(f"Notebook not found: {self.config.notebook_path}")
                return False
            
            # Validate timeout
            if self.config.timeout < 60:
                print("Timeout must be at least 60 seconds")
                return False
            
            # Validate cells to execute if specified
            if not self.config.execute_all and not self.config.cells_to_execute:
                print("Either execute_all must be True or cells_to_execute must be specified")
                return False
            
            return True
        except Exception as e:
            print(f"Error validating config: {str(e)}")
            return False
    
    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the Jupyter Notebook MCP."""
        if not self.id:
            return MCPResult(success=False, error="MCP not created")
        
        try:
            return client.execute_server(self.id, inputs)
        except Exception as e:
            return MCPResult(success=False, error=str(e))
    
    def create_notebook(self, name: str, content: Dict[str, Any]) -> bool:
        """Create a new Jupyter notebook."""
        try:
            notebook_path = os.path.join(config.notebooks_dir, f"{name}.ipynb")
            os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
            
            with open(notebook_path, 'w') as f:
                import json
                json.dump(content, f, indent=2)
            
            self.config.notebook_path = notebook_path
            return True
        except Exception as e:
            print(f"Error creating notebook: {str(e)}")
            return False 