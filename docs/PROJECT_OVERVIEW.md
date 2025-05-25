# Model Context Protocol (MCP) - Project Overview

## Purpose
The Model Context Protocol (MCP) is a modular, extensible framework for managing, executing, and monitoring AI model workflows. It enables orchestration of complex, multi-step pipelines involving LLM prompts, Python scripts, Jupyter notebooks, and more, with robust dependency management, monitoring, and extensibility.

## High-Level Architecture
- **API Layer:** FastAPI-based backend for workflow, MCP, and monitoring management.
- **Database Layer:** PostgreSQL (or SQLite for dev) with SQLAlchemy models for MCPs, workflows, runs, and audit logs.
- **Workflow Engine:** Supports sequential and DAG-based execution, with dependency validation and parallelism.
- **Component Registry:** Manages MCP definitions, versions, and metadata.
- **Monitoring & Metrics:** Real-time system and workflow monitoring, Prometheus integration, alerting, and visualization.
- **AI Co-Pilot:** Workflow builder assistant for intelligent suggestions and automation.
- **Frontend (planned):** Streamlit/React UI for workflow design, monitoring, and visualization.

## Key Features & Modules
- **MCP Registry:**
  - Versioned MCP definitions (LLM, script, notebook, etc.)
  - Tagging, metadata, and config management
- **Workflow Engine:**
  - Sequential and DAG (Directed Acyclic Graph) execution
  - Dependency validation, cycle detection, and parallel step execution
  - Error handling strategies (stop, retry, fallback)
- **DAG Engine & Visualizer:**
  - Build and execute workflows as DAGs
  - Visualize execution graph, critical path, and parallelism
- **Database Optimizations:**
  - Indexing, query caching (Redis), connection pooling
- **Monitoring & Metrics:**
  - System health, workflow performance, alerting, Prometheus metrics
- **AI Co-Pilot:**
  - Intelligent workflow builder and suggestions (in progress)
- **Testing:**
  - Pytest-based test suite for engine, visualizer, and API

## Implementation Highlights
- **DAG Workflow Engine:**
  - Fully supports step dependencies, parallel execution, and cycle detection
  - Extensible for custom step types and error strategies
- **DAG Visualizer:**
  - Uses networkx and matplotlib for graph visualization
  - Highlights critical path, parallel groups, and step status
- **Database Layer:**
  - SQLAlchemy 2.0+ models, UUID PKs, robust relationships
  - Optimized for performance and extensibility
- **Monitoring:**
  - Real-time metrics, Prometheus integration, alerting system
- **Caching & Pooling:**
  - Redis-based query caching, connection pooling for DB
- **Test Coverage:**
  - Comprehensive tests for DAG, visualizer, and core logic

## How to Run
1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
2. **Configure environment:**
   - Set `DATABASE_URL`, `REDIS_URL`, and other env vars as needed
3. **Initialize DB:**
   ```
   python -c 'from mcp.db.base_models import init_db; init_db()'
   ```
4. **Run API server:**
   ```
   uvicorn mcp.api.main:app --reload
   ```
5. **Run tests:**
   ```
   pytest
   ```

## Extending the Project
- Add new MCP types by extending the registry and schemas
- Add new workflow step types or error strategies in the engine
- Integrate new monitoring backends or alerting rules
- Contribute frontend components for workflow design and monitoring

## Current Status & Next Steps
- **Core MCP, workflow, and DAG engine implemented and tested**
- **Monitoring, metrics, and alerting system in place**
- **DAG visualizer and test suite complete**
- **Database optimizations (caching, pooling) active**
- **AI Co-Pilot and advanced UI in progress**
- **Next:**
  - Expand frontend UI/UX
  - Add more MCP/component types
  - Enhance security (RBAC, audit)
  - Integrate with external orchestration (K8s, Airflow)

## Contributors & Acknowledgments
- Project lead: @Chunkys0up7
- AI/automation: GPT-4
- Thanks to all testers and contributors!

## References
- [Tasks - 25th May](./Tasks_25th_May.md)
- [Changelog](../CHANGELOG.md)
- [Database Optimizations](../mcp/db/optimizations/README.md)
- [Monitoring System](../mcp/monitoring/README.md)
- [Component Registry](../mcp/components/README.md)

## [25th May]
- Component preview and metadata modal implemented in FacetedSearchScreen (Marketplace UI).
- Backend: Added reviews table, Pydantic schemas, and API endpoints for component ratings and reviews.

---
For more details, see the README.md and module-level docs. 