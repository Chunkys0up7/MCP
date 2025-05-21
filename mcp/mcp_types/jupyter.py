from typing import Dict, Any
import os
from .base import BaseMCP
from ..core.types import JupyterNotebookConfig, MCPResult
from ..api.client import MCPClient
from ..core.config import config

class JupyterNotebookMCP(BaseMCP):
    """Jupyter Notebook MCP implementation."""
    
    def __init__(self, config: JupyterNotebookConfig, client: MCPClient):
        super().__init__(config, client)
        self.config: JupyterNotebookConfig = config
    
    def execute(self, inputs: Dict[str, Any]) -> MCPResult:
        """Execute the Jupyter Notebook MCP."""
        if not self.id:
            return MCPResult(success=False, error="MCP not created or ID not set for execution")
        
        try:
            return self.client.execute_server(self.id, inputs)
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