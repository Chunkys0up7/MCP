import pytest
import logging
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from mcp.utils.logging import (
    setup_logging,
    log_execution,
    log_error,
    get_execution_logs,
    get_error_logs
)

@pytest.fixture
def mock_logger():
    """Mock logger."""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger

@pytest.fixture
def mock_file_handler():
    """Mock file handler."""
    with patch('logging.FileHandler') as mock_handler:
        mock_handler.return_value = MagicMock()
        yield mock_handler

def test_setup_logging(mock_logger, mock_file_handler):
    """Test logging setup."""
    setup_logging()
    
    # Verify logger setup
    mock_logger.setLevel.assert_called_once_with(logging.INFO)
    mock_logger.addHandler.assert_called()

def test_log_execution(mock_logger):
    """Test execution logging."""
    # Setup
    config = {
        "type": "llm_prompt",
        "model_name": "claude-3-sonnet-20240229",
        "temperature": 0.7
    }
    result = {"output": "test output"}
    
    # Execute
    log_execution(config, result)
    
    # Verify
    mock_logger.info.assert_called_once()
    log_message = mock_logger.info.call_args[0][0]
    log_data = json.loads(log_message)
    
    assert log_data["type"] == "execution"
    assert log_data["config"] == config
    assert log_data["result"] == result
    assert "timestamp" in log_data

def test_log_error(mock_logger):
    """Test error logging."""
    # Setup
    error = Exception("Test error")
    context = {"config": {"type": "llm_prompt"}}
    
    # Execute
    log_error(error, context)
    
    # Verify
    mock_logger.error.assert_called_once()
    log_message = mock_logger.error.call_args[0][0]
    log_data = json.loads(log_message)
    
    assert log_data["type"] == "error"
    assert log_data["error"] == str(error)
    assert log_data["context"] == context
    assert "timestamp" in log_data

def test_get_execution_logs():
    """Test getting execution logs."""
    # Setup
    mock_logs = [
        json.dumps({
            "type": "execution",
            "config": {"type": "llm_prompt"},
            "result": {"output": "test"},
            "timestamp": datetime.now().isoformat()
        })
    ]
    
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.readlines.return_value = mock_logs
        
        # Execute
        logs = get_execution_logs()
        
        # Verify
        assert len(logs) == 1
        assert logs[0]["type"] == "execution"
        assert logs[0]["config"]["type"] == "llm_prompt"

def test_get_error_logs():
    """Test getting error logs."""
    # Setup
    mock_logs = [
        json.dumps({
            "type": "error",
            "error": "Test error",
            "context": {"config": {"type": "llm_prompt"}},
            "timestamp": datetime.now().isoformat()
        })
    ]
    
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.readlines.return_value = mock_logs
        
        # Execute
        logs = get_error_logs()
        
        # Verify
        assert len(logs) == 1
        assert logs[0]["type"] == "error"
        assert logs[0]["error"] == "Test error"

def test_log_file_rotation():
    """Test log file rotation."""
    with patch('logging.handlers.RotatingFileHandler') as mock_handler:
        setup_logging()
        mock_handler.assert_called_once()
        args = mock_handler.call_args[1]
        assert args["maxBytes"] == 10 * 1024 * 1024  # 10MB
        assert args["backupCount"] == 5

def test_log_formatting():
    """Test log message formatting."""
    # Setup
    config = {"type": "llm_prompt"}
    result = {"output": "test"}
    
    with patch('logging.Formatter') as mock_formatter:
        setup_logging()
        
        # Execute
        log_execution(config, result)
        
        # Verify
        mock_formatter.assert_called_once()
        format_string = mock_formatter.call_args[0][0]
        assert "%(asctime)s" in format_string
        assert "%(levelname)s" in format_string
        assert "%(message)s" in format_string 