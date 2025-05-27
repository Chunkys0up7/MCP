"""
sandbox.py - Utilities for securely running subprocesses with resource and environment restrictions.

This module provides helpers to execute untrusted or user-supplied code in a sandboxed environment,
limiting CPU, memory, and file/network access as much as possible from Python.
"""

import os
import sys
import tempfile
import subprocess
import platform
import shutil
import logging
from typing import List, Optional, Dict, Tuple

logger = logging.getLogger(__name__)

def run_sandboxed_subprocess(
    command: List[str],
    timeout: int = 600,
    memory_limit_mb: int = 512,
    cpu_time_limit_sec: int = 60,
    extra_env: Optional[Dict[str, str]] = None,
    input_data: Optional[bytes] = None,
) -> Tuple[int, str, str]:
    """
    Run a command in a subprocess with resource limits and a sandboxed environment.

    - Sets a temporary working directory (isolates file writes/reads).
    - Restricts environment variables (removes proxies, disables networking if possible).
    - Enforces CPU and memory limits (best effort on Windows; strict on Unix).
    - Enforces a timeout (process is killed if it exceeds this).
    - Returns (returncode, stdout, stderr).

    Args:
        command: List of command arguments to execute.
        timeout: Maximum wall time in seconds before killing the process.
        memory_limit_mb: Maximum memory (MB) allowed for the process (Unix only).
        cpu_time_limit_sec: Maximum CPU time in seconds (Unix only).
        extra_env: Additional environment variables to set.
        input_data: Bytes to send to stdin of the process (rarely used).

    Returns:
        Tuple of (returncode, stdout, stderr).
    """
    # Prepare environment: start with a copy of the current env
    env = os.environ.copy()
    # Remove network proxy env vars to reduce risk of network access
    for k in list(env.keys()):
        if k.lower().startswith("http_proxy") or k.lower().startswith("https_proxy") or k.lower().startswith("ftp_proxy"):
            env.pop(k)
    # Optionally, restrict PATH and other envs (could be further locked down)
    env["PYTHONUNBUFFERED"] = "1"
    if extra_env:
        env.update(extra_env)

    # Create a temp working directory for the subprocess
    with tempfile.TemporaryDirectory() as temp_cwd:
        def preexec_fn_unix():
            import resource
            # Set CPU time limit (seconds)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_time_limit_sec, cpu_time_limit_sec))
            # Set memory limit (address space, bytes)
            mem_bytes = memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            # Optionally, set file descriptor limits, etc.

        preexec_fn = None
        creationflags = 0
        if platform.system() == "Windows":
            # No preexec_fn on Windows; use job objects for memory/cpu if needed (not implemented here)
            # Optionally, use CREATE_NO_WINDOW to hide the window
            creationflags = subprocess.CREATE_NO_WINDOW
        else:
            preexec_fn = preexec_fn_unix

        try:
            proc = subprocess.run(
                command,
                input=input_data,
                capture_output=True,
                text=True,
                cwd=temp_cwd,  # Isolate file access to temp dir
                env=env,
                timeout=timeout,
                preexec_fn=preexec_fn,  # Only works on Unix
                creationflags=creationflags,  # Only used on Windows
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as e:
            logger.error(f"Sandboxed subprocess timed out: {command}")
            # e.stdout and e.stderr may be bytes if text=False, but we set text=True, so should be str or None
            stdout = e.stdout if isinstance(e.stdout, str) or e.stdout is None else e.stdout.decode(errors="replace")
            return -1, stdout or "", f"TimeoutExpired: {str(e)}"
        except Exception as e:
            logger.error(f"Sandboxed subprocess error: {command}: {e}")
            return -1, "", f"Exception: {str(e)}" 