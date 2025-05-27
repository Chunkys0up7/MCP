import os
import tempfile
import sys
import logging
from typing import Any, Dict, Optional

import nbformat
import papermill as pm

from mcp.core.types import JupyterNotebookConfig
from .sandbox import run_sandboxed_subprocess

from .base import BaseMCPServer


class JupyterNotebookMCP(BaseMCPServer):
    """MCP for executing Jupyter notebooks.
    Uses JupyterNotebookConfig from mcp.core.types.
    Name and description properties are inherited from BaseMCPServer.
    """

    def __init__(self, config: JupyterNotebookConfig):
        """Initialize the Jupyter Notebook MCP.

        Args:
            config (JupyterNotebookConfig): The configuration for this MCP from mcp.core.types.

        Raises:
            ValueError: If the notebook file is not found.
        """
        super().__init__(config)
        self.config: JupyterNotebookConfig = config  # Ensure type for self.config
        if not os.path.exists(self.config.notebook_path):
            raise ValueError(f"Notebook not found: {self.config.notebook_path}")

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jupyter notebook with given inputs in a sandboxed subprocess.

        This method builds a papermill CLI command and uses run_sandboxed_subprocess
        to enforce resource and environment limits. Returns a result dict with output,
        results, execution_time, success, and error.
        """
        with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as temp:
            output_path = temp.name

        try:
            # --- SANDBOXED EXECUTION ---
            # Build papermill CLI command with parameters
            import json
            import shlex
            param_str = " ".join([
                f"-p {shlex.quote(str(k))} {shlex.quote(json.dumps(v))}" for k, v in inputs.items()
            ]) if inputs else ""
            command = [
                sys.executable, "-m", "papermill",
                self.config.notebook_path,
                output_path,
            ]
            if param_str:
                command += shlex.split(param_str)
            if hasattr(self.config, 'timeout'):
                command += ["--execution-timeout", str(self.config.timeout)]

            logger = logging.getLogger(__name__)
            logger.debug(f"Executing JupyterNotebookMCP with sandboxed papermill: {command}")

            # Use run_sandboxed_subprocess to enforce resource limits and isolation
            returncode, stdout, stderr = run_sandboxed_subprocess(
                command,
                timeout=self.config.timeout if hasattr(self.config, 'timeout') else 600,
                memory_limit_mb=1024,  # Notebooks may need more memory
                cpu_time_limit_sec=120,  # Notebooks may run longer
            )
            # --- END SANDBOXED EXECUTION ---

            if returncode != 0:
                return {
                    "output": None,
                    "results": None,
                    "execution_time": None,
                    "success": False,
                    "error": f"Notebook execution failed (rc={returncode}): {stderr}",
                }

            # Parse the output notebook for results
            with open(output_path, "r") as f:
                nb = nbformat.read(f, as_version=4)

            results = self._extract_results(nb)

            combined_output = []
            for cell_result in results.values():
                for output_data in cell_result.get("outputs", []):
                    if isinstance(output_data, str):
                        combined_output.append(output_data)

            return {
                "output": "\n".join(combined_output),
                "results": results,
                "execution_time": self._get_execution_time(nb),
                "success": True,
                "error": None,
            }

        except Exception as e:
            import traceback

            error_msg = f"Notebook execution failed: {str(e)}\n{traceback.format_exc()}"
            return {
                "output": None,
                "results": None,
                "execution_time": None,
                "success": False,
                "error": error_msg,
            }

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def _extract_results(self, nb: nbformat.NotebookNode) -> Dict[str, Any]:
        results = {}

        for i, cell in enumerate(nb.cells):
            if cell.cell_type == "code" and cell.outputs:
                cell_outputs = []
                for output in cell.outputs:
                    if output.output_type == "execute_result":
                        if "data" in output and "text/plain" in output.data:
                            cell_outputs.append(output.data["text/plain"])
                    elif output.output_type == "stream":
                        cell_outputs.append(output.text)
                    elif output.output_type == "error":
                        cell_outputs.append(
                            f"ErrorInCell: {output.ename}: {output.evalue}"
                        )
                results[
                    f"cell_{i+1}_{cell.execution_count if cell.execution_count else 'nc'}"
                ] = {
                    "outputs": cell_outputs,
                    "execution_count": cell.execution_count,
                    "source": cell.source,
                }
        return results

    def _get_execution_time(self, nb: nbformat.NotebookNode) -> Optional[float]:
        if hasattr(nb.metadata, "papermill") and hasattr(
            nb.metadata.papermill, "duration"
        ):
            return nb.metadata.papermill.duration

        total_time = 0.0
        executed_cell_found = False
        for cell in nb.cells:
            if (
                cell.cell_type == "code"
                and hasattr(cell.metadata, "papermill")
                and hasattr(cell.metadata.papermill, "execution_duration")
            ):
                if cell.metadata.papermill.execution_duration is not None:
                    total_time += cell.metadata.papermill.execution_duration
                    executed_cell_found = True
            elif hasattr(cell.metadata, "execution") and cell.metadata.execution.get(
                "iopub.execute_input"
            ):
                pass

        return total_time if executed_cell_found else None
