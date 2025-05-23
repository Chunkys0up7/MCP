# Project Status Review - May 22nd

This document outlines the current status of the MCP project based on a review of the codebase against the tasks planned for May 23rd.

## Key Findings:

*   **Core CRUD APIs Largely Complete:**
    *   The API endpoints for managing MCP definitions (`/context/*` routes in `mcp/api/main.py`) and Workflow definitions (`/workflows/*` routes, excluding execution, in `mcp/api/routers/workflows.py`) are implemented.
    *   These endpoints correctly interact with the PostgreSQL database for creating, reading, updating, and deleting these definitions, leveraging `mcp/core/registry.py` for MCPs and SQLAlchemy models directly for workflows.

*   **Workflow Execution is the Primary Gap:**
    *   The `POST /workflows/{workflow_id}/execute` endpoint in `mcp/api/routers/workflows.py` has a foundational structure: it fetches the workflow definition from the DB and creates an initial `WorkflowRun` record.
    *   However, the `WorkflowEngine` (`mcp/core/workflow_engine.py`) is **not yet capable of dynamically loading MCP definitions from the database and instantiating them for execution.**
    *   Currently, the `WorkflowEngine` expects a pre-populated registry of MCP *instances*, which is a major blocker for the `/execute` endpoint to function as intended with DB-stored MCPs. The comments in `mcp/api/routers/workflows.py` (around lines 275+) clearly identify this as a critical area for refactoring.

*   **Component Registry - Advanced Features Pending:**
    *   **Schema Validation (AJV):** While Pydantic validates the overall `MCPCreate` schema, specific JSON schema validation (e.g., using AJV) for the `initial_config` field based on `MCPType` is not yet implemented in `mcp/core/registry.py`. This is a planned feature according to the `System Overview` document.
    *   **Semantic Search (pgvector):** The `System Overview` mentions `pgvector`, but the database models (`mcp/db/models/mcp.py`) and current API query logic do not show an implementation or exposure of semantic search capabilities.

*   **UI Development Tasks:** These are primarily frontend-focused and appear not started from a backend/API perspective, which is expected at this stage. The existing backend APIs provide foundational data for these UI modules.

*   **MCD System Integration:** The handoff of "Architectural constraints" from the MCD System to the Workflow Engine is planned but not yet started.

*   **Security (JWT & RBAC):**
    *   JWT token validation for protecting endpoints is implemented (`get_current_subject` dependency).
    *   An authentication router (`mcp/api/routers/auth.py`) is present, implying token issuance capabilities.
    *   Detailed Role-Based Access Control (RBAC) logic beyond basic user authentication is not yet apparent in the core API endpoints and needs to be defined and implemented as per UI/feature requirements.

*   **Testing:**
    *   Test files (e.g., `tests/api/test_context_api.py`, `tests/api/test_workflow_api.py`) have been updated to use a file-based SQLite database (`./test.db`) to ensure that all connections (including those from the FastAPI app and the test session) share the same database and tables. This resolves the "no such table" errors encountered previously. Comprehensive unit and integration tests are now being verified for MCP/Workflow CRUD and engine components.

*   **Documentation:**
    *   FastAPI provides auto-generated OpenAPI docs. A separate, detailed `api_reference.md` might need updates or creation.
    *   Documentation for the `/execute` endpoint, including its evolving behavior with dynamic MCP loading, will be important.

## Critical Next Steps:

1.  **Refactor `WorkflowEngine` for Dynamic MCP Loading:** This is the highest priority. The engine must be updated to:
    *   Accept MCP IDs within workflow steps.
    *   Load the corresponding `MCP` definition and its versioned `config_snapshot` from the database via `mcp/core/registry.py`.
    *   Dynamically instantiate the correct `BaseMCPServer` subclass (e.g., `LLMPromptMCP`) using the MCP's type and configuration.
    *   Use these dynamic instances for execution.
    This directly impacts the `execute_workflow` endpoint in `mcp/api/routers/workflows.py`.

2.  **Implement Component Registry Enhancements:**
    *   Type-specific schema validation for `MCP.initial_config` (potentially using AJV).
    *   Functional `pgvector` integration for semantic search capabilities on MCPs.

3.  **Develop and Verify Tests:** Write comprehensive unit and integration tests for existing API functionality and the upcoming `WorkflowEngine` changes.

This status review should help in refining the immediate tasks and focusing on the key areas for development. 