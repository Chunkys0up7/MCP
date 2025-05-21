# MCP User Guide

This guide provides information for users of the MCP system.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)
7. [Caching Guide](#caching-guide)

## Getting Started

### Installation

1. Install MCP:
```bash
pip install mcp
```

2. Set up environment variables:
```bash
export MCP_API_KEY=your_api_key
export MCP_DEBUG=true
```

3. Create configuration file:
```bash
cp config.yaml.example config.yaml
```

### Quick Start

1. Create a new MCP project:
```bash
mcp init my_project
cd my_project
```

2. Run the application:
```bash
mcp run
```

## Basic Usage

### LLM Prompts

1. Create a prompt configuration:
```python
from mcp.core.types import LLMPromptConfig

config = LLMPromptConfig(
    type="llm_prompt",
    template="Hello, {name}!",
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=100
)
```

2. Execute the prompt:
```python
from mcp.api.client import MCPClient

client = MCPClient()
response = await client.execute_llm_prompt(config, {"name": "World"})
```

### Jupyter Notebooks

1. Create a notebook configuration:
```python
from mcp.core.types import JupyterNotebookConfig

config = JupyterNotebookConfig(
    type="jupyter_notebook",
    notebook_path="notebooks/example.ipynb",
    execute_all=True,
    timeout=600
)
```

2. Execute the notebook:
```python
response = await client.execute_notebook(config)
```

### Python Scripts

1. Create a script configuration:
```python
from mcp.core.types import PythonScriptConfig

config = PythonScriptConfig(
    type="python_script",
    script_path="scripts/example.py",
    requirements=["requests"],
    virtual_env=True,
    timeout=300
)
```

2. Execute the script:
```python
response = await client.execute_script(config)
```

### AI Assistant

1. Create an assistant configuration:
```python
from mcp.core.types import AIAssistantConfig

config = AIAssistantConfig(
    type="ai_assistant",
    model_name="gpt-4",
    system_prompt="You are a helpful assistant.",
    temperature=0.7,
    max_tokens=1000,
    tools=["search", "calculator"]
)
```

2. Execute the assistant:
```python
response = await client.execute_assistant(config)
```

## Advanced Features

### Caching

1. Enable caching:
```yaml
cache:
  enabled: true
  max_size: 1000
  ttl: 3600
```

2. Use cache in code:
```python
from mcp.utils.cache import get_cache

cache = get_cache()
await cache.set("key", value)
value = await cache.get("key")
```

### Concurrency

1. Configure concurrency:
```yaml
execution:
  max_concurrent: 5
  pool_size: 10
```

2. Use async execution:
```python
async def execute_tasks():
    tasks = [
        client.execute_llm_prompt(config1),
        client.execute_notebook(config2)
    ]
    results = await asyncio.gather(*tasks)
```

### Error Handling

1. Handle errors:
```python
try:
    response = await client.execute_llm_prompt(config)
except MCPError as e:
    logger.error(f"Error: {e}")
    # Handle error
```

2. Retry on failure:
```python
from mcp.utils.retry import retry

@retry(max_retries=3, delay=5)
async def execute_with_retry():
    return await client.execute_llm_prompt(config)
```

## Configuration

### Environment Variables

- `MCP_API_KEY`: Your API key
- `MCP_DEBUG`: Enable debug mode
- `MCP_NOTEBOOKS_DIR`: Notebooks directory
- `MCP_SCRIPTS_DIR`: Scripts directory
- `MCP_LOGS_DIR`: Logs directory
- `MCP_CACHE_DIR`: Cache directory

### Configuration File

```yaml
# API Configuration
api:
  key: ${MCP_API_KEY}
  timeout: 600
  max_retries: 3

# Debug Settings
debug: false

# Directory Configuration
directories:
  notebooks: notebooks
  scripts: scripts
  logs: logs
  cache: cache

# Execution Settings
execution:
  default_timeout: 600
  max_concurrent: 5
  virtual_env: true

# Logging Configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/mcp.log

# Cache Configuration
cache:
  enabled: true
  max_size: 1000
  ttl: 3600
```

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Check API key validity
   - Verify environment variable
   - Check API key permissions

2. **Timeout Issues**
   - Increase timeout value
   - Check resource usage
   - Monitor execution time

3. **Cache Issues**
   - Clear cache
   - Check cache permissions
   - Verify cache configuration

4. **Memory Issues**
   - Monitor memory usage
   - Reduce batch size
   - Use streaming

### Debug Mode

1. Enable debug mode:
```bash
export MCP_DEBUG=true
```

2. Check logs:
```bash
tail -f logs/mcp.log
```

## Best Practices

### Performance

1. **Caching**
   - Use appropriate cache
   - Set proper TTL
   - Monitor cache usage

2. **Concurrency**
   - Use async/await
   - Manage resources
   - Handle timeouts

3. **Resource Management**
   - Clean up resources
   - Monitor usage
   - Handle errors

### Security

1. **API Keys**
   - Keep keys secure
   - Rotate regularly
   - Use restrictions

2. **Data Handling**
   - Validate input
   - Sanitize output
   - Encrypt sensitive data

3. **Access Control**
   - Use proper auth
   - Implement rate limiting
   - Monitor access

## Caching Guide

### Cache Types

1. **File Cache**
   - Persistent storage
   - Disk-based
   - Good for large data

2. **Memory Cache**
   - Fast access
   - Limited size
   - Good for small data

3. **Redis Cache**
   - Distributed
   - Scalable
   - Good for production

### Configuring Cache Backends

MCP supports different caching backends. You can configure the desired cache type and its specific settings in your `config.yaml` file. The `get_cache()` utility will then use the backend specified in your configuration.

**1. Memory Cache**

Ideal for small datasets and fastest access. Data is lost when the application restarts.

```yaml
cache:
  enabled: true
  backend: memory # Specify memory cache
  max_size: 500    # Max number of items
  ttl: 1800        # Default TTL in seconds (e.g., 30 minutes)
```

**2. File Cache**

Persistent disk-based cache. Good for larger datasets or when data needs to survive restarts. The cache directory can be configured using the `MCP_CACHE_DIR` environment variable or directly in the YAML.

```yaml
cache:
  enabled: true
  backend: file      # Specify file cache
  directory: ${MCP_CACHE_DIR:-cache_data} # Path to cache directory
  max_size: 2000   # Max number of items (or consider defining units like MB)
  ttl: 3600        # Default TTL in seconds (e.g., 1 hour)
```

**3. Redis Cache**

A distributed cache, suitable for production and multi-instance deployments. Requires a running Redis server.

```yaml
cache:
  enabled: true
  backend: redis     # Specify Redis cache
  host: localhost
  port: 6379
  db: 0
  password: ${REDIS_PASSWORD:-} # Optional: use environment variable for password
  ttl: 7200        # Default TTL in seconds (e.g., 2 hours)
  # Example Redis-specific settings (e.g., connection pool)
  # max_connections: 10
```

### Cache Usage

1. **Basic Operations**
```python
# Set cache
await cache.set("key", value)

# Get cache
value = await cache.get("key")

# Delete cache
await cache.delete("key")
```

2. **Advanced Operations**
```python
# Set with TTL
await cache.set("key", value, ttl=3600)

# Get with default
value = await cache.get("key", default=None)

# Clear cache
await cache.clear()
```

### Cache Best Practices

1. **Key Design**
   - Use meaningful keys
   - Include version
   - Consider namespace

2. **TTL Management**
   - Set appropriate TTL
   - Handle expiration
   - Update on change

3. **Error Handling**
   - Handle cache misses
   - Handle cache errors
   - Implement fallback

4. **Performance**
   - Use compression
   - Batch operations
   - Monitor usage
``` 