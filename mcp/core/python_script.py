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

from .base import BaseMCPServer
from mcp.core.types import PythonScriptConfig

class PythonScriptMCP(BaseMCPServer):
    """MCP for executing Python scripts.
    Uses PythonScriptConfig from mcp.core.types.
    Name and description properties are inherited from BaseMCPServer.
    """
    
    def __init__(self, config: PythonScriptConfig):
        """Initialize the Python Script MCP.
        
        Args:
            config (PythonScriptConfig): The configuration for this MCP from mcp.core.types.
            
        Raises:
            ValueError: If the script file is not found.
        """
        super().__init__(config)
        if not os.path.exists(self.config.script_path):
            raise ValueError(f"Script not found: {self.config.script_path}")
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Python script with given inputs.
        
        Uses self.config fields (virtual_env, requirements, timeout) from types.PythonScriptConfig.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = os.path.join(temp_dir, "venv")
            python_executable = "python"
            pip_executable = "pip"
            
            try:
                if self.config.virtual_env:
                    print(f"Creating virtual environment in: {venv_path}")
                    venv.create(venv_path, with_pip=True)
                    if os.name == "nt":
                        python_executable = os.path.join(venv_path, "Scripts", "python.exe")
                        pip_executable = os.path.join(venv_path, "Scripts", "pip.exe")
                    else:
                        python_executable = os.path.join(venv_path, "bin", "python")
                        pip_executable = os.path.join(venv_path, "bin", "pip")
                    
                    if self.config.requirements:
                        print(f"Installing requirements: {self.config.requirements} using {pip_executable}")
                        req_process = subprocess.run(
                            [pip_executable, "install"] + self.config.requirements,
                            capture_output=True, text=True, check=False
                        )
                        if req_process.returncode != 0:
                            print(f"Error installing requirements.\nStdout: {req_process.stdout}\nStderr: {req_process.stderr}")
                            raise Exception(f"Failed to install requirements: {req_process.stderr}")
                        print("Requirements installed successfully.")
                
                script_content = self._prepare_script(inputs)
                temp_script_path = os.path.join(temp_dir, "_mcp_temp_script.py")
                with open(temp_script_path, "w", encoding='utf-8') as f:
                    f.write(script_content)
                
                print(f"Executing script: {temp_script_path} with python: {python_executable}")
                result = subprocess.run(
                    [python_executable, temp_script_path],
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout,
                    check=False
                )
                
                stdout = result.stdout
                stderr = result.stderr
                success = result.returncode == 0
                output_json = None

                if stdout:
                    try:
                        output_lines = stdout.strip().split('\n')
                        for line in reversed(output_lines):
                            try:
                                parsed_line = json.loads(line)
                                if isinstance(parsed_line, dict):
                                    output_json = parsed_line
                                    break
                            except json.JSONDecodeError:
                                continue 
                    except Exception as json_e:
                        print(f"Could not parse stdout as JSON: {json_e}")
                
                final_output = output_json if output_json else (stdout.strip() if stdout else None)
                error_message = None if success else (stderr.strip() if stderr else "Script execution failed with no stderr.")

                if not success and not error_message and stdout:
                     error_message = f"Script failed. Stdout: {stdout.strip()}"

                return {
                    "output": final_output,
                    "stdout": stdout,
                    "stderr": stderr,
                    "success": success,
                    "error": error_message
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "output": None,
                    "stdout": None,
                    "stderr": f"Script execution timed out after {self.config.timeout} seconds",
                    "success": False,
                    "error": f"Script execution timed out after {self.config.timeout} seconds"
                }
            except Exception as e:
                import traceback
                return {
                    "output": None,
                    "stdout": None,
                    "stderr": str(e),
                    "success": False,
                    "error": f"Script execution failed: {str(e)}\n{traceback.format_exc()}"
                }
    
    def _prepare_script(self, inputs: Dict[str, Any]) -> str:
        """Prepare the script content by injecting input parameters at the beginning."""
        with open(self.config.script_path, "r", encoding='utf-8') as f:
            original_script_content = f.read()
        
        input_assignments = []
        for key, value in inputs.items():
            input_assignments.append(f"{key} = {repr(value)}")
        
        injected_code = "\n".join(input_assignments)
        
        return f"# MCP Injected Inputs:\n{injected_code}\n# End MCP Injected Inputs\n\n{original_script_content}" 