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
from typing import List, Optional, Dict, Any

class BaseMCPConfig(BaseModel):
    type: MCPType
    input_variables: List[str]
    metadata: Optional[Dict[str, Any]] = None
```

### LLMPromptConfig

```python
class LLMPromptConfig(BaseMCPConfig):
    template: str
    system_prompt: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    stop_sequences: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
```

### JupyterNotebookConfig

```python
class JupyterNotebookConfig(BaseMCPConfig):
    notebook_path: str
    execute_all: bool
    cells_to_execute: Optional[List[int]]
    timeout: int
    kernel_name: Optional[str] = None
    allow_errors: bool = False
```

### PythonScriptConfig

```python
class PythonScriptConfig(BaseMCPConfig):
    script_path: str
    requirements: List[str]
    virtual_env: bool
    timeout: int
    python_version: Optional[str] = None
    working_dir: Optional[str] = None
```

### AssistantConfig

```python
class AssistantConfig(BaseMCPConfig):
    model_name: str
    system_prompt: str
    temperature: float
    max_tokens: int
    tools: List[str]
    memory_enabled: bool = True
    memory_limit: Optional[int] = None
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
    cache_dir: str = "cache"
    max_retries: int = 3
    retry_delay: int = 5
```

### Environment Variables

- `MCP_API_KEY`: Your API key
- `MCP_DEBUG`: Enable debug mode (true/false)
- `MCP_NOTEBOOKS_DIR`: Custom notebooks directory
- `MCP_SCRIPTS_DIR`: Custom scripts directory
- `MCP_LOGS_DIR`: Custom logs directory
- `MCP_CACHE_DIR`: Custom cache directory
- `MCP_MAX_RETRIES`: Maximum number of retries
- `MCP_RETRY_DELAY`: Delay between retries in seconds

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

### Assistant Configuration Widget

```python
def build_assistant_config() -> AssistantConfig:
    """Build AI Assistant configuration through UI."""
    # Implementation details...
```

## API Client

### MCPClient

```python
class MCPClient:
    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logging()
        self.cache = setup_cache()

    async def execute_llm_prompt(self, config: LLMPromptConfig) -> str:
        """Execute an LLM prompt."""
        # Implementation details...

    async def execute_notebook(self, config: JupyterNotebookConfig) -> Dict[str, Any]:
        """Execute a Jupyter notebook."""
        # Implementation details...

    async def execute_script(self, config: PythonScriptConfig) -> Dict[str, Any]:
        """Execute a Python script."""
        # Implementation details...

    async def execute_assistant(self, config: AssistantConfig) -> Dict[str, Any]:
        """Execute an AI assistant task."""
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

### Caching

```python
def setup_cache(
    cache_dir: Optional[str] = None,
    max_size: int = 1000,
    ttl: int = 3600
) -> Cache:
    """Set up caching for the application."""
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

class CacheError(MCPError):
    """Cache-related errors."""
    pass
```

## Type Definitions

### Common Types

```python
from typing import Dict, Any, List, Optional, Union

# Common type aliases
JSON = Dict[str, Any]
VariableMap = Dict[str, Any]
CacheKey = str
CacheValue = Any
```

## Best Practices

### Error Handling

1. Always use custom exceptions for MCP-specific errors
2. Include detailed error messages
3. Log errors appropriately
4. Handle cleanup in finally blocks
5. Implement retry mechanisms for transient errors

### Configuration

1. Use environment variables for sensitive data
2. Validate configuration on startup
3. Use type hints for configuration objects
4. Document all configuration options
5. Implement configuration caching

### Logging

1. Use appropriate log levels
2. Include context in log messages
3. Rotate log files
4. Don't log sensitive information
5. Implement structured logging

### Security

1. Validate all input
2. Use secure defaults
3. Implement rate limiting
4. Monitor resource usage
5. Implement proper authentication and authorization

# API Reference

This document provides a reference for the main API endpoints of the MCP Server.
For interactive documentation and detailed schema information, please refer to the auto-generated OpenAPI docs available at `/docs` when the server is running.

## Authentication

Most endpoints are protected and require a JWT Bearer token in the `Authorization` header.
Tokens can be obtained via:
- `POST /auth/issue-dev-token` (using `X-API-Key` for development)
- `POST /auth/token` (OAuth2 password flow)

## Context API (`/context` - MCP Definitions)

Manages MCP (Model Component Package) definitions, which represent reusable components like LLM Prompts, Python Scripts, etc.

### 1. List MCP Definitions
- **Endpoint:** `GET /context`
- **Description:** Retrieves a list of all available MCP definitions.
- **Auth:** JWT Required.
- **Query Parameters:**
    - `skip` (int, optional): Number of records to skip (for pagination).
    - `limit` (int, optional): Maximum number of records to return (for pagination).
- **Response:** `200 OK` - A list of `MCPListItem` objects.
    - `MCPListItem` includes `id`, `name`, `type`, `description`, `tags`, `latest_version_str`, `updated_at`.

### 2. Create MCP Definition
- **Endpoint:** `POST /context`
- **Description:** Creates a new MCP definition along with its initial version.
- **Auth:** JWT Required. (RBAC: Typically `developer` or `admin` roles - see `docs/security_rbac.md`)
- **Request Body:** `MCPCreate` schema.
    - `name` (str, required): Name of the MCP.
    - `type` (MCPType enum, required): Type of the MCP (e.g., `python_script`, `llm_prompt`).
    - `description` (str, optional): Description.
    - `tags` (List[str], optional): Tags for categorization.
    - `initial_version_str` (str, required): Version string for the first version (e.g., "1.0.0").
    - `initial_version_description` (str, optional): Description for the initial version.
    - `initial_config` (dict, required): Configuration specific to the MCP type. This config is validated against the schema for the given `type`.
- **Response:** `201 Created` - An `MCPRead` object representing the created MCP definition.
    - `MCPRead` includes `id`, `name`, `type`, `description`, `tags`, `created_at`, `updated_at`.
- **Error Responses:**
    - `400 Bad Request`: If `initial_config` is invalid for the specified `MCPType` or other validation errors.
    - `422 Unprocessable Entity`: If basic request payload validation fails.

### 3. Get MCP Definition Details
- **Endpoint:** `GET /context/{mcp_id}`
- **Description:** Retrieves detailed information about a specific MCP definition, including its latest version details.
- **Auth:** JWT Required.
- **Path Parameters:**
    - `mcp_id` (UUID, required): The ID of the MCP definition.
- **Response:** `200 OK` - An `MCPDetail` object.
    - `MCPDetail` includes all fields from `MCPRead` plus `latest_version_str` and `latest_version_config`.
- **Error Responses:** `404 Not Found` if MCP ID does not exist.

### 4. Update MCP Definition
- **Endpoint:** `PUT /context/{mcp_id}`
- **Description:** Updates the core attributes (name, description, tags) of an MCP definition.
    - Note: To update the configuration or create a new version, a separate versioning API would typically be used (not yet fully specified beyond initial creation).
- **Auth:** JWT Required. (RBAC: Typically owner or `admin` - see `docs/security_rbac.md`)
- **Path Parameters:**
    - `mcp_id` (UUID, required): The ID of the MCP definition to update.
- **Request Body:** `MCPUpdate` schema.
    - `name` (str, optional)
    - `description` (str, optional)
    - `tags` (List[str], optional)
- **Response:** `200 OK` - An `MCPRead` object representing the updated MCP definition.
- **Error Responses:** `404 Not Found`, `422 Unprocessable Entity`.

### 5. Delete MCP Definition
- **Endpoint:** `DELETE /context/{mcp_id}`
- **Description:** Deletes an MCP definition and all its associated versions.
- **Auth:** JWT Required. (RBAC: Typically owner or `admin` - see `docs/security_rbac.md`)
- **Path Parameters:**
    - `mcp_id` (UUID, required): The ID of the MCP definition to delete.
- **Response:** `204 No Content`.
- **Error Responses:** `404 Not Found`.

### 6. Search MCP Definitions
- **Endpoint:** `GET /context/search`
- **Description:** Performs a semantic search for MCP definitions based on a query string. Results are ordered by relevance.
- **Auth:** JWT Required.
- **Query Parameters:**
    - `query` (str, required): The text to search for.
    - `limit` (int, optional, default: 10): Maximum number of results to return.
- **Response:** `200 OK` - A list of `MCPListItem` objects.
- **Error Responses:** `400 Bad Request` if query is empty.

## Workflows API (`/workflows`)

Manages workflow definitions and their execution.

### 1. List Workflow Definitions
- **Endpoint:** `GET /workflows`
- **Description:** Retrieves a list of all available workflow definitions.
- **Auth:** JWT Required.
- **Query Parameters:** (Pagination likely, e.g., `skip`, `limit` - to be confirmed from implementation)
- **Response:** `200 OK` - A list of `Workflow` (schema) objects.

### 2. Create Workflow Definition
- **Endpoint:** `POST /workflows`
- **Description:** Creates a new workflow definition.
- **Auth:** JWT Required.
- **Request Body:** `WorkflowCreate` schema.
    - `name` (str, required)
    - `description` (str, optional)
    - `steps` (List[`WorkflowStep`], required): Sequence of steps.
        - Each `WorkflowStep` includes `name`, `mcp_id`, `mcp_version_id`, `inputs` (mapping input names to `WorkflowStepInput` which defines source type and value/key).
    - `execution_mode` (ExecutionMode enum, optional, default: `SEQUENTIAL`)
    - `error_handling` (ErrorHandlingConfig schema, optional)
- **Response:** `201 Created` - A `Workflow` (schema) object representing the created workflow.
- **Error Responses:** `404 Not Found` (if an `mcp_id` in a step does not exist), `422 Unprocessable Entity`.

### 3. Get Workflow Definition
- **Endpoint:** `GET /workflows/{workflow_id}`
- **Description:** Retrieves a specific workflow definition.
- **Auth:** JWT Required.
- **Path Parameters:** `workflow_id` (UUID, required).
- **Response:** `200 OK` - A `Workflow` (schema) object.
- **Error Responses:** `404 Not Found`.

### 4. Update Workflow Definition
- **Endpoint:** `PUT /workflows/{workflow_id}`
- **Description:** Updates an existing workflow definition.
- **Auth:** JWT Required.
- **Path Parameters:** `workflow_id` (UUID, required).
- **Request Body:** `WorkflowUpdate` schema (similar to `WorkflowCreate`).
- **Response:** `200 OK` - A `Workflow` (schema) object.
- **Error Responses:** `404 Not Found`, `422 Unprocessable Entity`.

### 5. Delete Workflow Definition
- **Endpoint:** `DELETE /workflows/{workflow_id}`
- **Description:** Deletes a workflow definition.
- **Auth:** JWT Required.
- **Path Parameters:** `workflow_id` (UUID, required).
- **Response:** `204 No Content`.
- **Error Responses:** `404 Not Found`.

### 6. Execute Workflow
- **Endpoint:** `POST /workflows/{workflow_id}/execute`
- **Description:** Executes a defined workflow.
    - The workflow is run by the `WorkflowEngine` which dynamically loads and instantiates the required MCPs (from DB) for each step based on `mcp_id` and `mcp_version_id` specified in the workflow definition.
    - Input resolution for steps is handled by the engine (from static values, workflow inputs, or previous step outputs).
    - Results of the execution, including step-level details and final outputs, are recorded in the `WorkflowRun` database table.
- **Auth:** JWT Required.
- **Path Parameters:** `workflow_id` (UUID, required).
- **Request Body:** A JSON object containing initial inputs for the workflow (keys should match `workflow_input_key` references in the workflow steps).
    - Example: `{"initial_param": "some_value", "another_param": 123}`
- **Response:** `200 OK` - A `WorkflowExecutionResult` object.
    - `workflow_id` (str)
    - `run_id` (str): The ID of the `WorkflowRun` record in the database.
    - `status` (str: `SUCCESS`, `FAILED`, `PENDING`, etc.)
    - `started_at` (datetime)
    - `finished_at` (datetime, optional)
    - `inputs` (dict): The initial inputs provided for the execution.
    - `step_results` (List[dict]): Detailed results from each executed step (status, outputs, errors).
    - `final_outputs` (dict, optional): The final outputs of the workflow (often the outputs of the last step).
    - `error_message` (str, optional): Overall error message if the workflow failed.
- **Error Responses:** 
    - `404 Not Found` (if `workflow_id` does not exist).
    - `200 OK` with `status: FAILED` in response body if the workflow itself fails during execution (e.g., MCP instantiation error, step execution error). 