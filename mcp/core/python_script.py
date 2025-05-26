"""
A simple hello world example that demonstrates:
1. Using input variables
2. Using external packages (requests)
3. Basic error handling
"""

import asyncio
import atexit
import json
import logging
import os
import subprocess
import sys
import tempfile
import traceback
from typing import Any, Dict, Optional

from mcp.core.types import PythonScriptConfig

from .base import BaseMCPServer

logger = logging.getLogger(__name__)

# Store paths of temporary files created for script_content
_temporary_script_files = set()


def _cleanup_temporary_files():
    """Remove any temporary script files created during the session."""
    for temp_file_path in list(_temporary_script_files):
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            _temporary_script_files.remove(temp_file_path)
            logger.info(f"Cleaned up temporary script file: {temp_file_path}")
        except OSError as e:
            logger.error(
                f"Error cleaning up temporary script file {temp_file_path}: {e}"
            )
        except KeyError:
            pass  # Already removed by another thread/process, perhaps


# Register cleanup function to be called on Python interpreter exit
atexit.register(_cleanup_temporary_files)


class PythonScriptMCP(BaseMCPServer):
    """MCP for executing Python scripts, potentially in isolated environments."""

    def __init__(self, config: PythonScriptConfig):
        """Initialize the Python Script MCP.

        Args:
            config (PythonScriptConfig): The configuration for this MCP from mcp.core.types.

        Raises:
            ValueError: If the script file is not found.
        """
        super().__init__(config)
        self.config: PythonScriptConfig = config  # Ensure type for self.config
        self._script_path_to_execute: Optional[str] = None

        if self.config.script_content:
            # If script_content is provided, write it to a temporary file
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, encoding="utf-8"
                ) as tmp_script:
                    tmp_script.write(self.config.script_content)
                    self._script_path_to_execute = tmp_script.name
                _temporary_script_files.add(self._script_path_to_execute)
                logger.info(
                    f"Created temporary script file for execution: {self._script_path_to_execute} from script_content of MCP '{self.config.name}'"
                )
            except Exception as e:
                logger.error(
                    f"Failed to create temporary script file from script_content for MCP '{self.config.name}': {e}"
                )
                # Potentially raise an error or fall back if script_path is also an option
                # For now, if temp file creation fails, it might try to use self.config.script_path if set.
                # If neither results in a valid path, execute will fail.

        if not self._script_path_to_execute and self.config.script_path:
            self._script_path_to_execute = self.config.script_path

        if not self._script_path_to_execute:
            # This case should ideally be caught by PythonScriptConfig's validator,
            # but as a safeguard in the MCP itself:
            raise ValueError(
                f"PythonScriptMCP '{self.config.name}' initialized without a valid script_path or usable script_content."
            )
        elif not os.path.exists(self._script_path_to_execute):
            # This check is important if _script_path_to_execute came from self.config.script_path
            raise FileNotFoundError(
                f"Script path '{self._script_path_to_execute}' for MCP '{self.config.name}' does not exist."
            )

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the Python script with the given inputs."""
        if not self._script_path_to_execute or not os.path.exists(
            self._script_path_to_execute
        ):
            logger.error(
                f"Cannot execute PythonScriptMCP '{self.config.name}': Effective script path '{self._script_path_to_execute}' is invalid or missing."
            )
            return {
                "success": False,
                "result": None,
                "error": "Script path misconfigured or temporary script creation failed.",
            }

        # This will run in a separate thread via asyncio.to_thread
        def _run_script_sync():
            python_exe = sys.executable or "python"
            script_to_run_str = str(self._script_path_to_execute)

            tmp_input_file_path = None
            tmp_output_file_path = None
            stdout_str = ""
            stderr_str = ""
            process_return_code = -1  # Default error code

            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False, encoding="utf-8"
                ) as tmp_input_f_obj:
                    json.dump(inputs, tmp_input_f_obj)
                    tmp_input_file_path = tmp_input_f_obj.name

                with tempfile.NamedTemporaryFile(
                    mode="r", suffix=".json", delete=False, encoding="utf-8"
                ) as tmp_output_f_obj:
                    tmp_output_file_path = tmp_output_f_obj.name
                _temporary_script_files.add(
                    tmp_output_file_path
                )  # Ensure cleanup even if script fails before writing

                command = [
                    python_exe,
                    script_to_run_str,
                    tmp_input_file_path,
                    tmp_output_file_path,
                ]
                logger.debug(f"Executing PythonScriptMCP sync command: {command}")

                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",  # Ensure consistent encoding
                    check=False,  # We check returncode manually
                )
                stdout_str = process.stdout.strip()
                stderr_str = process.stderr.strip()
                process_return_code = process.returncode

                if stdout_str:
                    logger.info(
                        f"Script stdout for '{self.config.name}':\n{stdout_str}"
                    )
                if stderr_str:
                    logger.warning(
                        f"Script stderr for '{self.config.name}':\n{stderr_str}"
                    )

                if process_return_code == 0:
                    if os.path.exists(tmp_output_file_path):
                        with open(tmp_output_file_path, "r", encoding="utf-8") as f_out:
                            script_output_data = json.load(f_out)
                        return {
                            "success": script_output_data.get("success", False),
                            "result": script_output_data.get("result"),
                            "error": script_output_data.get("error"),
                            "stdout": stdout_str,
                            "stderr": stderr_str,
                        }
                    else:
                        logger.error(
                            f"Script for '{self.config.name}' executed successfully (rc=0) but output file '{tmp_output_file_path}' was not found."
                        )
                        return {
                            "success": False,
                            "result": None,
                            "error": "Script executed (rc=0) but output file missing.",
                            "stdout": stdout_str,
                            "stderr": stderr_str,
                        }
                else:
                    logger.error(
                        f"Script execution for '{self.config.name}' failed with return code {process_return_code}."
                    )
                    return {
                        "success": False,
                        "result": None,
                        "error": f"Script execution failed with code {process_return_code}. Stderr: {stderr_str}",
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                    }

            except json.JSONDecodeError as je:
                logger.error(
                    f"JSONDecodeError processing script output for '{self.config.name}': {je}"
                )
                return {
                    "success": False,
                    "result": None,
                    "error": f"Failed to decode JSON output from script: {je}",
                }
            except Exception as e:
                logger.error(
                    f"Exception during Python script sync execution for '{self.config.name}': {e}\n{traceback.format_exc()}"
                )
                return {
                    "success": False,
                    "result": None,
                    "error": f"An unexpected error occurred in sync runner: {str(e)}",
                }
            finally:
                if tmp_input_file_path and os.path.exists(tmp_input_file_path):
                    try:
                        os.remove(tmp_input_file_path)
                    except OSError as e_remove:
                        logger.warning(
                            f"Could not remove temporary input file {tmp_input_file_path}: {e_remove}"
                        )
                # tmp_output_file_path is handled by atexit via _temporary_script_files

        # Run the synchronous script execution function in a separate thread
        try:
            return await asyncio.to_thread(_run_script_sync)
        except Exception as e_thread:  # Catch errors from to_thread itself, if any
            logger.error(
                f"Error invoking asyncio.to_thread for '{self.config.name}': {e_thread}\n{traceback.format_exc()}"
            )
            return {
                "success": False,
                "result": None,
                "error": f"Failed to execute script due to threading error: {str(e_thread)}",
            }

    def __del__(self):
        """
        Custom destructor to attempt cleanup of the temporary script file created from script_content
        if this specific MCP instance is deleted and it had created such a file.
        This is a fallback to the atexit handler, especially useful for long-running apps
        where instances might be deleted before app exit.
        """
        if (
            hasattr(self, "_script_path_to_execute")
            and self._script_path_to_execute
            and self.config.script_content
            and self._script_path_to_execute in _temporary_script_files
        ):
            try:
                if os.path.exists(self._script_path_to_execute):
                    os.remove(self._script_path_to_execute)
                _temporary_script_files.remove(self._script_path_to_execute)
                logger.info(
                    f"Cleaned up temporary script file on MCP instance deletion: {self._script_path_to_execute}"
                )
            except Exception as e:
                logger.error(
                    f"Error cleaning up temporary script {self._script_path_to_execute} during MCP instance __del__: {e}"
                )
            pass  # Ensure no errors from __del__

    def _prepare_script(self, inputs: Dict[str, Any]) -> str:
        """Prepare the script content by injecting input parameters at the beginning."""
        with open(self.config.script_path, "r", encoding="utf-8") as f:
            original_script_content = f.read()

        input_assignments = []
        for key, value in inputs.items():
            input_assignments.append(f"{key} = {repr(value)}")

        injected_code = "\n".join(input_assignments)

        return f"# MCP Injected Inputs:\n{injected_code}\n# End MCP Injected Inputs\n\n{original_script_content}"
