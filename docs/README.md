# MCP (Model Control Panel)

A powerful and flexible framework for managing and executing various types of model-based tasks, including LLM prompts, Jupyter notebooks, and Python scripts.

## Overview

MCP provides a unified interface for:
- LLM Prompt Management
- Jupyter Notebook Execution
- Python Script Execution
- AI Assistant Integration

## Features

- **Unified Interface**: Manage all your model-based tasks through a single, consistent interface
- **Type Safety**: Built with Pydantic for robust type checking and validation
- **Extensible**: Easy to add new MCP types and functionality
- **User-Friendly UI**: Streamlit-based interface for easy configuration and monitoring
- **Robust Error Handling**: Comprehensive error handling and logging
- **Configuration Management**: Centralized configuration with environment variable support

## Installation

```bash
pip install mcp
```

## Quick Start

1. Set up your environment variables:
```bash
export MCP_API_KEY=your_api_key
export MCP_DEBUG=true  # Optional, for debug mode
```

2. Run the MCP interface:
```bash
mcp
```

## Documentation

- [User Guide](user_guide.md)
- [API Reference](api_reference.md)
- [Configuration](configuration.md)
- [Development Guide](development.md)
- [Architecture](architecture.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to MCP.

## License

MIT License - see [LICENSE](LICENSE) for details. 