# MCP Configuration Guide

This guide explains how to configure MCP for your specific needs.

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Configuration File](#configuration-file)
3. [Directory Structure](#directory-structure)
4. [Security Settings](#security-settings)
5. [Performance Tuning](#performance-tuning)
6. [Caching Configuration](#caching-configuration)

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

- `MCP_CACHE_DIR`: Custom cache directory
  ```bash
  export MCP_CACHE_DIR=/path/to/cache
  ```

- `MCP_TIMEOUT`: Default timeout in seconds
  ```bash
  export MCP_TIMEOUT=600
  ```

- `MCP_MAX_RETRIES`: Maximum number of retries
  ```bash
  export MCP_MAX_RETRIES=3
  ```

- `MCP_RETRY_DELAY`: Delay between retries in seconds
  ```bash
  export MCP_RETRY_DELAY=5
  ```

## Configuration File

MCP can also be configured using a configuration file. Create a `config.yaml` file in your project root:

```yaml
# API Configuration
api:
  key: ${MCP_API_KEY}
  timeout: 600
  max_retries: 3
  retry_delay: 5

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
  python_version: "3.9"
  working_dir: "."

# Logging Configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/mcp.log
  max_size: 10485760  # 10MB
  backup_count: 5
  structured: true

# Security Settings
security:
  rate_limit: 100
  rate_limit_period: 3600
  allowed_origins: ["*"]
  allowed_methods: ["GET", "POST"]
  auth_required: true
  auth_type: "api_key"

# Cache Configuration
cache:
  enabled: true
  max_size: 1000
  ttl: 3600
  storage: "file"
  compression: true
```

## Directory Structure

MCP uses the following directory structure:

```
mcp/
├── notebooks/          # Jupyter notebooks
├── scripts/           # Python scripts
├── logs/             # Log files
├── cache/            # Cache files
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
export MCP_CACHE_DIR=/custom/cache
```

2. Using configuration file:
```yaml
directories:
  notebooks: /custom/notebooks
  scripts: /custom/scripts
  logs: /custom/logs
  cache: /custom/cache
```

## Security Settings

### API Key Security

1. Never commit API keys to version control
2. Use environment variables for API keys
3. Rotate API keys regularly
4. Use API key restrictions when possible
5. Implement API key validation

### Rate Limiting

Configure rate limiting in `config.yaml`:

```yaml
security:
  rate_limit: 100  # Maximum requests per period
  rate_limit_period: 3600  # Period in seconds
  rate_limit_by_ip: true  # Enable per-IP rate limiting
```

### Access Control

Configure access control in `config.yaml`:

```yaml
security:
  allowed_origins: ["https://your-domain.com"]
  allowed_methods: ["GET", "POST"]
  auth_required: true
  auth_type: "api_key"
  cors_enabled: true
```

## Performance Tuning

### Timeout Settings

Configure timeouts in `config.yaml`:

```yaml
execution:
  default_timeout: 600  # Default timeout in seconds
  notebook_timeout: 1800  # Notebook-specific timeout
  script_timeout: 300  # Script-specific timeout
  assistant_timeout: 1200  # Assistant-specific timeout
```

### Concurrent Execution

Configure concurrent execution in `config.yaml`:

```yaml
execution:
  max_concurrent: 5  # Maximum concurrent executions
  pool_size: 10  # Thread pool size
  queue_size: 100  # Maximum queue size
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
  structured: true  # Enable structured logging
  json_format: false  # Use JSON format for logs
```

## Caching Configuration

### Cache Settings

Configure caching in `config.yaml`:

```yaml
cache:
  enabled: true  # Enable caching
  max_size: 1000  # Maximum number of cache entries
  ttl: 3600  # Time-to-live in seconds
  storage: "file"  # Storage type (file, memory, redis)
  compression: true  # Enable compression
  cleanup_interval: 3600  # Cleanup interval in seconds
```

### Cache Types

1. File Cache:
```yaml
cache:
  storage: "file"
  directory: "cache"
  file_extension: ".cache"
```

2. Memory Cache:
```yaml
cache:
  storage: "memory"
  max_size: 1000
```

3. Redis Cache:
```yaml
cache:
  storage: "redis"
  host: "localhost"
  port: 6379
  db: 0
```

## Best Practices

1. **Configuration Management**
   - Use environment variables for sensitive data
   - Use configuration file for non-sensitive settings
   - Document all configuration options
   - Validate configuration on startup
   - Implement configuration versioning

2. **Security**
   - Keep API keys secure
   - Implement rate limiting
   - Use proper access control
   - Monitor resource usage
   - Implement audit logging
   - Use secure defaults

3. **Performance**
   - Set appropriate timeouts
   - Configure concurrent execution
   - Monitor resource usage
   - Use caching when appropriate
   - Implement request queuing
   - Use connection pooling

4. **Logging**
   - Use appropriate log levels
   - Configure log rotation
   - Monitor log files
   - Don't log sensitive information
   - Implement structured logging
   - Use log aggregation

5. **Caching**
   - Configure appropriate TTL
   - Implement cache invalidation
   - Monitor cache usage
   - Use compression when needed
   - Implement cache fallback
   - Use distributed caching when needed 