import os
import tempfile
from typing import Any, Dict, List, Optional
import papermill as pm
import nbformat

from .base import BaseMCP, MCPConfig

class JupyterNotebookConfig(MCPConfig):
    """Configuration for Jupyter Notebook MCP"""
    notebook_path: str
    execute_all: bool = True
    cells_to_execute: Optional[List[int]] = None
    timeout: int = 600  # seconds

class JupyterNotebookMCP(BaseMCP):
    """MCP for executing Jupyter notebooks"""
    
    def __init__(self, config: JupyterNotebookConfig):
        super().__init__(config)
        if not os.path.exists(config.notebook_path):
            raise ValueError(f"Notebook not found: {config.notebook_path}")
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jupyter notebook with given inputs
        
        Args:
            inputs: Dictionary of input parameters for the notebook
            
        Returns:
            Dictionary containing notebook execution results
        """
        # Create temporary output path
        with tempfile.NamedTemporaryFile(suffix='.ipynb', delete=False) as temp:
            output_path = temp.name
        
        try:
            # Execute notebook with parameters
            pm.execute_notebook(
                self.config.notebook_path,
                output_path,
                parameters=inputs,
                timeout=self.config.timeout
            )
            
            # Read and process results
            with open(output_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Extract results from executed cells
            results = self._extract_results(nb)
            
            return {
                "results": results,
                "execution_time": self._get_execution_time(nb),
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def _extract_results(self, nb: nbformat.NotebookNode) -> Dict[str, Any]:
        """Extract results from executed notebook cells"""
        results = {}
        
        for cell in nb.cells:
            if cell.cell_type == 'code' and cell.execution_count is not None:
                # Get cell outputs
                outputs = []
                for output in cell.outputs:
                    if output.output_type == 'execute_result':
                        outputs.append(output.data.get('text/plain', ''))
                    elif output.output_type == 'stream':
                        outputs.append(output.text)
                
                results[f"cell_{cell.execution_count}"] = {
                    "outputs": outputs,
                    "execution_count": cell.execution_count
                }
        
        return results
    
    def _get_execution_time(self, nb: nbformat.NotebookNode) -> float:
        """Calculate total execution time from notebook metadata"""
        total_time = 0.0
        
        for cell in nb.cells:
            if hasattr(cell.metadata, 'execution'):
                if 'duration' in cell.metadata.execution:
                    total_time += cell.metadata.execution.duration
        
        return total_time 