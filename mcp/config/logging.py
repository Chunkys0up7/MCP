import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from .settings import settings

def setup_logging(
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """Set up logging configuration."""
    # Use settings if not provided
    log_file = log_file or settings.logging.file
    log_level = log_level or settings.logging.level
    log_format = log_format or settings.logging.format

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set logging levels for specific modules
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

# Create a default logger for the application
logger = get_logger("mcp") 