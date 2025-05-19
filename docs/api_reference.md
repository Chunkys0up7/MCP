# MCP API Reference

This document provides detailed information about the MCP API, including classes, methods, and configuration options.

## Table of Contents

1. [Core Types](#core-types)
2. [Configuration](#configuration)
3. [UI Components](#ui-components)
4. [API Client](#api-client)
5. [Utilities](#utilities)

## Core Types

### MCPType

```python
from enum import Enum

class MCPType(Enum):
    LLM_PROMPT = "llm_prompt"
    JUPYTER_NOTEBOOK = "jupyter_notebook"
    PYTHON_SCRIPT = "python_script"
    AI_ASSISTANT = "ai_assistant"
```

### BaseMCPConfig

```python
from pydantic import BaseModel
from typing import List, Optional

class BaseMCPConfig(BaseModel):
    type: MCPType
    input_variables: List[str]
```

### LLMPromptConfig

```python
class LLMPromptConfig(BaseMCPConfig):
    template: str
    system_prompt: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
```

### JupyterNotebookConfig

```python
class JupyterNotebookConfig(BaseMCPConfig):
    notebook_path: str
    execute_all: bool
    cells_to_execute: Optional[List[int]]
    timeout: int
```

### PythonScriptConfig

```python
class PythonScriptConfig(BaseMCPConfig):
    script_path: str
    requirements: List[str]
    virtual_env: bool
    timeout: int
```

## Configuration

### Config

```python
class Config(BaseModel):
    api_key: str
    debug: bool = False
    notebooks_dir: str = "notebooks"
    scripts_dir: str = "scripts"
    logs_dir: str = "logs"
```

### Environment Variables

- `MCP_API_KEY`: Your API key
- `MCP_DEBUG`: Enable debug mode (true/false)
- `MCP_NOTEBOOKS_DIR`: Custom notebooks directory
- `MCP_SCRIPTS_DIR`: Custom scripts directory
- `MCP_LOGS_DIR`: Custom logs directory

## UI Components

### LLM Configuration Widget

```python
def build_llm_config() -> LLMPromptConfig:
    """Build LLM configuration through UI."""
    # Implementation details...
```

### Notebook Configuration Widget

```python
def build_notebook_config() -> JupyterNotebookConfig:
    """Build Jupyter Notebook configuration through UI."""
    # Implementation details...
```

### Script Configuration Widget

```python
def build_script_config() -> PythonScriptConfig:
    """Build Python Script configuration through UI."""
    # Implementation details...
```

## API Client

### MCPClient

```python
class MCPClient:
    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logging()

    async def execute_llm_prompt(self, config: LLMPromptConfig) -> str:
        """Execute an LLM prompt."""
        # Implementation details...

    async def execute_notebook(self, config: JupyterNotebookConfig) -> Dict[str, Any]:
        """Execute a Jupyter notebook."""
        # Implementation details...

    async def execute_script(self, config: PythonScriptConfig) -> Dict[str, Any]:
        """Execute a Python script."""
        # Implementation details...
```

## Utilities

### Logging

```python
def setup_logging(
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """Set up logging for the application."""
    # Implementation details...
```

### Error Handling

```python
class MCPError(Exception):
    """Base exception for MCP errors."""
    pass

class ConfigurationError(MCPError):
    """Configuration-related errors."""
    pass

class ExecutionError(MCPError):
    """Execution-related errors."""
    pass
```

## Type Definitions

### Common Types

```python
from typing import Dict, Any, List, Optional, Union

# Common type aliases
JSON = Dict[str, Any]
VariableMap = Dict[str, Any]
```

## Best Practices

### Error Handling

1. Always use custom exceptions for MCP-specific errors
2. Include detailed error messages
3. Log errors appropriately
4. Handle cleanup in finally blocks

### Configuration

1. Use environment variables for sensitive data
2. Validate configuration on startup
3. Use type hints for configuration objects
4. Document all configuration options

### Logging

1. Use appropriate log levels
2. Include context in log messages
3. Rotate log files
4. Don't log sensitive information

### Security

1. Validate all input
2. Use secure defaults
3. Implement rate limiting
4. Monitor resource usage 