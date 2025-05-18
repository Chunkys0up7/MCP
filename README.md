# Microservice Control Panel (MCP)

A modular, configurable system for building and orchestrating AI applications through microservices.

## Features

- Prompt execution MCP for LLM interactions
- Jupyter notebook execution MCP
- Visual workflow builder
- Chain execution capabilities
- Enterprise-grade execution environment

## Project Structure

```
mcp/
├── api/                 # FastAPI backend
├── ui/                  # Streamlit frontend
├── core/               # Core MCP functionality
├── notebooks/          # Example notebooks
└── tests/              # Test suite
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
# Start the API server
uvicorn api.main:app --reload

# In another terminal, start the UI
streamlit run ui/app.py
```

## Development

- API documentation available at `/docs` when running the server
- UI development guide in `ui/README.md`
- MCP development guide in `core/README.md`

## License

MIT License 