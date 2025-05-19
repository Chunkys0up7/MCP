"""
A simple hello world example that demonstrates:
1. Using input variables
2. Using external packages (requests)
3. Basic error handling
"""

import os
import tempfile
import subprocess
import venv
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from .base import BaseMCPServer, MCPConfig

class PythonScriptConfig(MCPConfig):
    """Configuration for Python Script MCP.
    
    This class defines the configuration structure for Python script-based MCPs,
    specifying how scripts should be executed and what parameters to use.
    
    Attributes:
        script_path (str): Path to the Python script file.
        requirements (List[str]): List of Python package requirements.
        input_variables (List[str]): List of required input variables.
        timeout (int): Maximum execution time in seconds. Defaults to 600.
        virtual_env (bool): Whether to use a virtual environment. Defaults to True.
    """
    script_path: str
    requirements: List[str] = []
    input_variables: List[str] = []
    timeout: int = 600  # seconds
    virtual_env: bool = True

class PythonScriptMCP(BaseMCPServer):
    """MCP for executing Python scripts.
    
    This class implements the MCP interface for executing Python scripts,
    providing features like virtual environment management, requirement installation,
    and script execution with input parameters.
    
    Attributes:
        config (PythonScriptConfig): The configuration for this script MCP.
    """
    
    def __init__(self, config: PythonScriptConfig):
        """Initialize the Python Script MCP.
        
        Args:
            config (PythonScriptConfig): The configuration for this MCP.
            
        Raises:
            ValueError: If the script file is not found.
        """
        super().__init__(config)
        if not os.path.exists(config.script_path):
            raise ValueError(f"Script not found: {config.script_path}")
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Python script with given inputs.
        
        This method executes the script in a virtual environment (if enabled),
        installing any required packages and passing input parameters.
        
        Args:
            inputs (Dict[str, Any]): Dictionary of input parameters for the script.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - output: Script output (parsed JSON if available)
                - stdout: Raw stdout output
                - stderr: Raw stderr output
                - success: Whether execution was successful
                - error: Error message if execution failed
        """
        # Create temporary directory for virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = os.path.join(temp_dir, "venv")
            
            try:
                # Create and activate virtual environment if enabled
                if self.config.virtual_env:
                    venv.create(venv_path, with_pip=True)
                    python_path = os.path.join(venv_path, "Scripts" if os.name == "nt" else "bin", "python")
                    pip_path = os.path.join(venv_path, "Scripts" if os.name == "nt" else "bin", "pip")
                    
                    # Install requirements
                    if self.config.requirements:
                        subprocess.run([pip_path, "install"] + self.config.requirements, check=True)
                else:
                    python_path = "python"
                
                # Create temporary script with input parameters
                script_content = self._prepare_script(inputs)
                script_path = os.path.join(temp_dir, "script.py")
                with open(script_path, "w") as f:
                    f.write(script_content)
                
                # Execute the script
                result = subprocess.run(
                    [python_path, script_path],
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout
                )
                
                # Try to parse the output as JSON
                try:
                    # Find the last line that contains valid JSON
                    output_lines = result.stdout.strip().split('\n')
                    json_output = None
                    for line in reversed(output_lines):
                        try:
                            json_output = json.loads(line)
                            if isinstance(json_output, dict):  # Only accept dictionary JSON
                                break
                        except json.JSONDecodeError:
                            continue
                    
                    if json_output:
                        return {
                            "output": json_output,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "success": result.returncode == 0
                        }
                except json.JSONDecodeError:
                    pass
                
                # If no valid JSON found, return the raw output
                return {
                    "output": result.stdout.strip(),
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "error": f"Script execution timed out after {self.config.timeout} seconds",
                    "success": False
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "success": False
                }
    
    def _prepare_script(self, inputs: Dict[str, Any]) -> str:
        """Prepare the script with input parameters.
        
        This method reads the original script and injects input parameters
        at the beginning of the script.
        
        Args:
            inputs (Dict[str, Any]): Input parameters to inject.
            
        Returns:
            str: The prepared script content.
        """
        with open(self.config.script_path, "r") as f:
            script_content = f.read()
        
        # Add input parameters at the beginning of the script
        input_code = "\n".join([
            f"{key} = {repr(value)}" for key, value in inputs.items()
        ])
        
        return f"{input_code}\n\n{script_content}" 