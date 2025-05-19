# Model Context Protocol (MCP)

## Overview
MCP is a modular framework for managing, executing, and monitoring AI model contexts, including LLM prompts, Jupyter notebooks, and Python scripts. It provides a FastAPI backend and a Streamlit dashboard frontend.

## Features
- Register and manage different types of MCPs (LLM prompts, notebooks, scripts)
- Execute MCPs and view results in a web UI
- Monitor server health and statistics
- Extensible for new MCP types

## Setup

### Prerequisites
- Python 3.9+
- (Recommended) Create and activate a virtual environment

### Install dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
- Set `MCP_API_KEY` for API authentication (optional, defaults provided)
- For LLMs, set `ANTHROPIC_API_KEY` if using Claude

### Start the backend
```bash
uvicorn mcp.api.main:app --reload
```

### Start the frontend
```bash
streamlit run mcp/ui/app.py
```

## Usage
- Access the dashboard at [http://localhost:8501](http://localhost:8501)
- Create, manage, and test MCPs from the UI
- Monitor health and stats from the sidebar

## Adding New MCPs
- Implement a new MCP class in `mcp/core/`
- Register it in the backend
- Add UI support in `mcp/ui/app.py`

## Running Tests
```bash
pytest
```

## Project Structure
- `mcp/api/` - FastAPI backend
- `mcp/ui/` - Streamlit frontend
- `mcp/core/` - Core MCP types and logic
- `tests/` - Test suite

## License
MIT

## API Documentation

Once the server is running, you can access:
- API documentation: http://localhost:8000/docs
- Prometheus metrics: http://localhost:8000/metrics
- Health check: http://localhost:8000/health
- Statistics: http://localhost:8000/stats

## Security

- API key authentication is required for all endpoints
- Rate limiting is enabled by default
- CORS is configured to allow only specific origins
- All sensitive configuration is managed through environment variables

## Monitoring

The server includes:
- Prometheus metrics for request counts, latencies, and server executions
- Structured JSON logging
- Health check endpoint
- Server statistics endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Additional Dependencies for Notebook and LLM Integration

This project now requires the following additional Python packages:

- pandas
- numpy
- matplotlib
- papermill
- nbformat
- jupyter
- anthropic

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## Using the Notebook MCP to Call an LLM (Claude)

The example notebook (`mcp/notebooks/example.ipynb`) demonstrates:
- Data analysis and plotting
- Calling the Claude LLM via the `anthropic` Python package

To use the LLM cell, ensure you have set your `ANTHROPIC_API_KEY` in your environment or `.env` file.

The notebook cell for LLM looks like this:

```python
import os
import anthropic

api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError('ANTHROPIC_API_KEY not set in environment!')

client = anthropic.Anthropic(api_key=api_key)
response = client.messages.create(
    model='claude-3-sonnet-20240229',
    max_tokens=256,
    temperature=0.7,
    messages=[
        {'role': 'user', 'content': 'Tell me a joke about data science.'}
    ]
)
print('Claude says:', response.content[0].text)
``` 