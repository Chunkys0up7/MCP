import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config import config


def setup_logging(
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Set up logging for the application.

    Args:
        log_file: Optional path to log file. If None, logs to stdout.
        level: Logging level (default: INFO)
        format_str: Log message format string

    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger("mcp")
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(format_str)

    # Create handlers
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Create global logger instance
logger = setup_logging(
    log_file="logs/mcp.log" if getattr(config, "debug", False) else None,
    level=logging.DEBUG if getattr(config, "debug", False) else logging.INFO,
)


def log_execution(config_obj: Any, result: Any):
    """Log execution event as structured JSON."""
    log_data = {
        "type": "execution",
        "config": config_obj,
        "result": result,
        "timestamp": datetime.now().isoformat(),
    }
    logger.info(json.dumps(log_data, default=str))


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log error event as structured JSON."""
    log_data = {
        "type": "error",
        "error": str(error),
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }
    logger.error(json.dumps(log_data, default=str))


def get_execution_logs(log_file: str = "logs/mcp.log"):
    """Retrieve execution logs from the log file."""
    logs = []
    if not Path(log_file).exists():
        return logs
    with open(log_file, "r") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("type") == "execution":
                    logs.append(data)
            except Exception:
                continue
    return logs


def get_error_logs(log_file: str = "logs/mcp.log"):
    """Retrieve error logs from the log file."""
    logs = []
    if not Path(log_file).exists():
        return logs
    with open(log_file, "r") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("type") == "error":
                    logs.append(data)
            except Exception:
                continue
    return logs
