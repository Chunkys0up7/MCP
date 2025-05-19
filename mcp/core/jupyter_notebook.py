import os
import tempfile
import subprocess
import venv
import json
from typing import Any, Dict, List, Optional
import papermill as pm
import nbformat
from pathlib import Path

from .base import BaseMCPServer, MCPConfig

class JupyterNotebookConfig(MCPConfig):
    """Configuration for Jupyter Notebook MCP.
    
    This class defines the configuration structure for Jupyter notebook-based MCPs,
    specifying how notebooks should be executed and what parameters to use.
    
    Attributes:
        notebook_path (str): Path to the Jupyter notebook file.
        execute_all (bool): Whether to execute all cells. Defaults to True.
        cells_to_execute (Optional[List[int]]): List of specific cell indices to execute.
        timeout (int): Maximum execution time in seconds. Defaults to 600.
    """
    notebook_path: str
    execute_all: bool = True
    cells_to_execute: Optional[List[int]] = None
    timeout: int = 600  # seconds

class JupyterNotebookMCP(BaseMCPServer):
    """MCP for executing Jupyter notebooks.
    
    This class implements the MCP interface for executing Jupyter notebooks,
    providing features like parameter injection, cell execution control,
    and result extraction.
    
    Attributes:
        config (JupyterNotebookConfig): The configuration for this notebook MCP.
    """
    
    def __init__(self, config: JupyterNotebookConfig):
        """Initialize the Jupyter Notebook MCP.
        
        Args:
            config (JupyterNotebookConfig): The configuration for this MCP.
            
        Raises:
            ValueError: If the notebook file is not found.
        """
        super().__init__(config)
        if not os.path.exists(config.notebook_path):
            raise ValueError(f"Notebook not found: {config.notebook_path}")
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jupyter notebook with given inputs.
        
        This method executes the notebook using papermill, injecting the input
        parameters and collecting the results from executed cells.
        
        Args:
            inputs (Dict[str, Any]): Dictionary of input parameters for the notebook.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - output: Combined output from all cells
                - results: Detailed cell outputs
                - execution_time: Total execution time
                - success: Whether execution was successful
                - error: Error message if execution failed
                
        Raises:
            Exception: If notebook execution fails.
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
            
            # Combine all outputs into a single string
            combined_output = []
            for cell_result in results.values():
                for output in cell_result.get('outputs', []):
                    if isinstance(output, str):
                        combined_output.append(output)
            
            return {
                "output": "\n".join(combined_output),
                "results": results,
                "execution_time": self._get_execution_time(nb),
                "success": True
            }
            
        except Exception as e:
            import traceback
            error_msg = f"Notebook execution failed: {str(e)}\n{traceback.format_exc()}"
            return {
                "error": error_msg,
                "success": False,
                "output": None,
                "results": None
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def _extract_results(self, nb: nbformat.NotebookNode) -> Dict[str, Any]:
        """Extract results from executed notebook cells.
        
        This method processes the notebook after execution to extract outputs
        from each executed cell.
        
        Args:
            nb (nbformat.NotebookNode): The executed notebook.
            
        Returns:
            Dict[str, Any]: Dictionary mapping cell numbers to their outputs and
                           execution metadata.
        """
        results = {}
        
        for cell in nb.cells:
            if cell.cell_type == 'code' and cell.execution_count is not None:
                # Get cell outputs
                outputs = []
                for output in cell.outputs:
                    if output.output_type == 'execute_result':
                        # Handle different output types
                        if 'text/plain' in output.data:
                            outputs.append(output.data['text/plain'])
                        elif 'text/html' in output.data:
                            outputs.append(output.data['text/html'])
                        elif 'image/png' in output.data:
                            outputs.append("[Image output]")
                        elif 'application/json' in output.data:
                            outputs.append(output.data['application/json'])
                    elif output.output_type == 'stream':
                        outputs.append(output.text)
                    elif output.output_type == 'error':
                        outputs.append(f"Error: {output.ename}: {output.evalue}")
                
                results[f"cell_{cell.execution_count}"] = {
                    "outputs": outputs,
                    "execution_count": cell.execution_count,
                    "source": cell.source
                }
        
        return results
    
    def _get_execution_time(self, nb: nbformat.NotebookNode) -> float:
        """Calculate total execution time from notebook metadata.
        
        This method sums up the execution duration of all cells from the
        notebook's metadata.
        
        Args:
            nb (nbformat.NotebookNode): The executed notebook.
            
        Returns:
            float: Total execution time in seconds.
        """
        total_time = 0.0
        
        for cell in nb.cells:
            if hasattr(cell.metadata, 'execution'):
                if 'duration' in cell.metadata.execution:
                    total_time += cell.metadata.execution.duration
        
        return total_time 