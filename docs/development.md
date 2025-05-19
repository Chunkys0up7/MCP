# MCP Development Guide

This guide provides information for developers who want to contribute to MCP.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Adding New Features](#adding-new-features)
4. [Testing](#testing)
5. [Code Style](#code-style)
6. [Documentation](#documentation)
7. [Release Process](#release-process)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- virtualenv or conda
- Git

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp.git
cd mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Project Structure

```
mcp/
├── mcp/
│   ├── core/           # Core functionality
│   ├── ui/             # UI components
│   ├── api/            # API client
│   ├── utils/          # Utilities
│   └── __init__.py
├── tests/              # Test files
├── docs/               # Documentation
├── examples/           # Example code
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
└── setup.py           # Package configuration
```

## Adding New Features

### 1. Create a New MCP Type

1. Define the configuration class in `core/types.py`:
```python
class NewMCPConfig(BaseMCPConfig):
    type: MCPType = MCPType.NEW_TYPE
    # Add your configuration fields
```

2. Add the type to `MCPType` enum:
```python
class MCPType(Enum):
    NEW_TYPE = "new_type"
    # ... existing types ...
```

3. Create UI component in `ui/widgets/`:
```python
def build_new_type_config() -> NewMCPConfig:
    """Build new type configuration through UI."""
    # Implementation
```

4. Add execution logic in `api/client.py`:
```python
async def execute_new_type(self, config: NewMCPConfig) -> Dict[str, Any]:
    """Execute new type."""
    # Implementation
```

### 2. Adding New UI Features

1. Create new UI component in `ui/widgets/`
2. Add component to main UI in `ui/app.py`
3. Update documentation
4. Add tests

### 3. Adding New API Features

1. Add new method to `MCPClient`
2. Implement error handling
3. Add logging
4. Add tests
5. Update documentation

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific.py

# Run with coverage
pytest --cov=mcp
```

### Writing Tests

1. Create test file in `tests/`
2. Use pytest fixtures
3. Mock external dependencies
4. Test edge cases
5. Test error conditions

Example test:
```python
def test_new_feature():
    # Arrange
    config = NewMCPConfig(...)
    
    # Act
    result = execute_new_feature(config)
    
    # Assert
    assert result == expected
```

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small
- Use meaningful names

### Pre-commit Hooks

The project uses pre-commit hooks for:
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)

### Running Linters

```bash
# Run all linters
pre-commit run --all-files

# Run specific linter
pre-commit run black --all-files
```

## Documentation

### Writing Documentation

1. Update relevant docstrings
2. Update README.md
3. Update user guide
4. Update API reference
5. Add examples

### Building Documentation

```bash
# Build documentation
cd docs
make html

# Serve documentation
python -m http.server -d _build/html
```

## Release Process

### 1. Version Bumping

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create version tag

### 2. Testing

1. Run all tests
2. Run linters
3. Build documentation
4. Test installation

### 3. Release

1. Create GitHub release
2. Upload to PyPI
3. Update documentation
4. Announce release

### 4. Post-release

1. Update development version
2. Create new development branch
3. Update documentation

## Contributing Guidelines

### Pull Request Process

1. Create feature branch
2. Write tests
3. Update documentation
4. Run linters
5. Submit PR

### Code Review

1. All PRs require review
2. All tests must pass
3. Documentation must be updated
4. Code must be linted

### Commit Messages

Follow conventional commits:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Testing
- chore: Maintenance

## Best Practices

### Code Quality

1. Write clean, maintainable code
2. Use type hints
3. Write tests
4. Document code
5. Follow style guide

### Performance

1. Profile code
2. Optimize bottlenecks
3. Use caching
4. Monitor resources

### Security

1. Validate input
2. Handle errors
3. Secure sensitive data
4. Follow security best practices

### Testing

1. Write unit tests
2. Write integration tests
3. Test edge cases
4. Test error conditions
5. Maintain test coverage 