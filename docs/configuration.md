# MCP Configuration Guide

This guide explains how to configure MCP for your specific needs.

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Configuration File](#configuration-file)
3. [Directory Structure](#directory-structure)
4. [Security Settings](#security-settings)
5. [Performance Tuning](#performance-tuning)

## Environment Variables

MCP uses environment variables for configuration. Here are all available options:

### Required Variables

- `MCP_API_KEY`: Your API key for the LLM service
  ```bash
  export MCP_API_KEY=your_api_key_here
  ```

### Optional Variables

- `MCP_DEBUG`: Enable debug mode (true/false)
  ```bash
  export MCP_DEBUG=true
  ```

- `MCP_NOTEBOOKS_DIR`: Custom notebooks directory
  ```bash
  export MCP_NOTEBOOKS_DIR=/path/to/notebooks
  ```

- `MCP_SCRIPTS_DIR`: Custom scripts directory
  ```bash
  export MCP_SCRIPTS_DIR=/path/to/scripts
  ```

- `MCP_LOGS_DIR`: Custom logs directory
  ```bash
  export MCP_LOGS_DIR=/path/to/logs
  ```

- `MCP_TIMEOUT`: Default timeout in seconds
  ```bash
  export MCP_TIMEOUT=600
  ```

## Configuration File

MCP can also be configured using a configuration file. Create a `config.yaml` file in your project root:

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
  max_size: 10485760  # 10MB
  backup_count: 5

# Security Settings
security:
  rate_limit: 100
  rate_limit_period: 3600
  allowed_origins: ["*"]
  allowed_methods: ["GET", "POST"]
```

## Directory Structure

MCP uses the following directory structure:

```
mcp/
├── notebooks/          # Jupyter notebooks
├── scripts/           # Python scripts
├── logs/             # Log files
├── config.yaml       # Configuration file
└── .env             # Environment variables
```

### Custom Directory Structure

You can customize the directory structure by:

1. Setting environment variables:
```bash
export MCP_NOTEBOOKS_DIR=/custom/notebooks
export MCP_SCRIPTS_DIR=/custom/scripts
export MCP_LOGS_DIR=/custom/logs
```

2. Using configuration file:
```yaml
directories:
  notebooks: /custom/notebooks
  scripts: /custom/scripts
  logs: /custom/logs
```

## Security Settings

### API Key Security

1. Never commit API keys to version control
2. Use environment variables for API keys
3. Rotate API keys regularly
4. Use API key restrictions when possible

### Rate Limiting

Configure rate limiting in `config.yaml`:

```yaml
security:
  rate_limit: 100  # Maximum requests per period
  rate_limit_period: 3600  # Period in seconds
```

### Access Control

Configure access control in `config.yaml`:

```yaml
security:
  allowed_origins: ["https://your-domain.com"]
  allowed_methods: ["GET", "POST"]
```

## Performance Tuning

### Timeout Settings

Configure timeouts in `config.yaml`:

```yaml
execution:
  default_timeout: 600  # Default timeout in seconds
  notebook_timeout: 1800  # Notebook-specific timeout
  script_timeout: 300  # Script-specific timeout
```

### Concurrent Execution

Configure concurrent execution in `config.yaml`:

```yaml
execution:
  max_concurrent: 5  # Maximum concurrent executions
  pool_size: 10  # Thread pool size
```

### Logging Configuration

Configure logging in `config.yaml`:

```yaml
logging:
  level: INFO  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/mcp.log
  max_size: 10485760  # Maximum log file size (10MB)
  backup_count: 5  # Number of backup files
```

## Best Practices

1. **Configuration Management**
   - Use environment variables for sensitive data
   - Use configuration file for non-sensitive settings
   - Document all configuration options
   - Validate configuration on startup

2. **Security**
   - Keep API keys secure
   - Implement rate limiting
   - Use proper access control
   - Monitor resource usage

3. **Performance**
   - Set appropriate timeouts
   - Configure concurrent execution
   - Monitor resource usage
   - Use caching when appropriate

4. **Logging**
   - Use appropriate log levels
   - Configure log rotation
   - Monitor log files
   - Don't log sensitive information 