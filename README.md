# Model Context Protocol (MCP)

## Overview
MCP is a modular framework for managing, executing, and monitoring AI model contexts, including LLM prompts, Jupyter notebooks, and Python scripts. It provides a FastAPI backend and a Streamlit dashboard frontend.

## Features
- Register and manage different types of MCPs (LLM prompts, notebooks, scripts)
- Execute MCPs and view results in a web UI
- Monitor server health and statistics
- Extensible for new MCP types
- High-performance database operations with connection pooling
- Query caching with Redis
- PostgreSQL index optimization
- System monitoring and metrics collection
- AI Co-Pilot for workflow optimization
- Dependency visualization and analysis

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- (Recommended) Create and activate a virtual environment

### Install dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
- Set `MCP_API_KEY` for API authentication (optional, defaults provided)
- For LLMs, set `ANTHROPIC_API_KEY` if using Claude
- Set `DATABASE_URL` for PostgreSQL connection
- Set `REDIS_URL` for Redis connection

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
- Use the AI Co-Pilot for workflow optimization
- Visualize component dependencies
- Monitor system performance

## Components

### Database Management
- Connection pooling for efficient database access
- Query caching with Redis for improved performance
- PostgreSQL index optimization for faster queries
- Database monitoring and statistics

### System Monitoring
- Real-time system health monitoring
- Performance metrics collection
- Alerting system with severity levels
- Prometheus metrics integration

### AI Co-Pilot
- Workflow optimization suggestions
- Error resolution assistance
- Best practice recommendations
- Performance improvements

### Dependency Visualizer
- Component relationship visualization
- Dependency conflict detection
- Version compatibility checking
- Visual dependency mapping

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
- `mcp/db/` - Database management and optimization
- `mcp/monitoring/` - System monitoring and metrics
- `mcp/components/` - AI Co-Pilot and Dependency Visualizer
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
- Database connection pooling with health checks
- Redis connection security

## Monitoring

The server includes:
- Prometheus metrics for request counts, latencies, and server executions
- Structured JSON logging
- Health check endpoint
- Server statistics endpoint
- System resource monitoring
- Database performance metrics
- Cache statistics
- Alert management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Additional Dependencies

This project requires the following additional Python packages:

### Core Dependencies
- pandas
- numpy
- matplotlib
- papermill
- nbformat
- jupyter
- anthropic

### Database Dependencies
- sqlalchemy
- psycopg2-binary
- redis
- alembic

### Monitoring Dependencies
- prometheus-client
- psutil
- networkx
- graphviz

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

## API Key Management and Authentication

### Creating and Managing API Keys
- Use the `/api/apikeys/` endpoint to create a new API key (admin or self-service).
- List your API keys with `GET /api/apikeys/`.
- Revoke an API key with `POST /api/apikeys/revoke`.

### Authenticating with API Keys
- Pass your API key in the `X-API-KEY` header for any authenticated endpoint.
- Alternatively, you can use a Bearer JWT in the `Authorization` header.
- All endpoints that require authentication now support both methods.

**Example:**
```
GET /api/apikeys/
X-API-KEY: <your-api-key>
```

## Execution Monitor Enhancements (UI)

The Execution Monitor now includes the following panels (with mock data, ready for backend integration):

- **Resource Usage Panel:** View CPU and memory usage per workflow step.
- **Time-Travel Debugging Panel:** Select a step to view its state at execution time.
- **Performance Suggestions Panel:** See optimization and bottleneck suggestions.
- **Real-Time Metrics Dashboard:** Monitor live metrics (CPU, memory, throughput, etc.).

These panels are integrated into the workflow Execution Monitor and will display real data once backend support is available. 