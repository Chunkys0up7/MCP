# Next Steps: Phase 1 - Database Integration Plan (for Tomorrow)

This document details the immediate action items for tomorrow, focusing on the initial tasks of Phase 1 from the `implementation_plan_system_overview.md`: integrating PostgreSQL and Redis.

## Primary Goal for Tomorrow:

Transition MCP and Workflow persistence from JSON files to PostgreSQL, and establish a Redis connection for future caching/state management. Ensure core functionalities (MCP & Workflow CRUD, Workflow Execution) are working with the new database backend.

## Detailed Next Steps:

1.  **Environment Setup (Local User Task):**
    *   **Action (User):** Install and run PostgreSQL and Redis locally.
    *   **Action (User):** Prepare connection details (host, port, user, password, DB name for PostgreSQL; host, port for Redis).
    *   **Action (AI/User):** Update/create `.env` with these credentials. Example:
        ```env
        POSTGRES_HOST=localhost
        POSTGRES_PORT=5432
        POSTGRES_USER=mcp_user
        POSTGRES_PASSWORD=mcp_password
        POSTGRES_DB=mcp_db
        REDIS_HOST=localhost
        REDIS_PORT=6379
        ```

2.  **Database Integration - Backend Code:**
    *   **SQLAlchemy Setup (`mcp/db/`):
        *   **AI Task:** Create `mcp/db/database.py` (SQLAlchemy engine, `SessionLocal`, `Base`, `create_all_tables` function, `get_db` dependency).
        *   **AI Task:** Create `mcp/db/models.py` with SQLAlchemy models:
            *   `MCPDefinition` (for MCP configurations, including versioning fields).
            *   `WorkflowDefinition` (for workflow structures).
            *   `WorkflowRun` (for storing execution results and history).
        *   **AI Task:** Call `create_all_tables` on application startup in `mcp/api/main.py`.
    *   **Redis Setup (`mcp/cache/` or `mcp/db/`):
        *   **AI Task:** Create `mcp/cache/redis_manager.py` (or similar) for Redis connection management using `.env` credentials.
        *   **(Optional for tomorrow, if time permits):** Define basic caching utility functions.

3.  **Refactor MCP Registry & Persistence (`mcp/core/registry.py`, `mcp/api/main.py`):
    *   **AI Task:** Remove JSON load/save functions from `mcp/core/registry.py`.
    *   **AI Task:** Implement DB-interactions in `mcp/core/registry.py`:
        *   `load_mcp_server(db: Session, mcp_id: str) -> Optional[MCPDefinition]`
        *   `load_all_mcp_servers(db: Session) -> List[MCPDefinition]`
        *   `save_mcp_server(db: Session, mcp_config: AllMCPConfigUnion) -> MCPDefinition`
    *   **AI Task:** Update MCP/Context API routes in `mcp/api/main.py` to use `Depends(get_db)` and the new registry functions. Adapt how the global `mcp_server_registry` (for MCP instances) is populated using DB data.

4.  **Refactor Workflow Persistence (`mcp/api/routers/workflows.py`):
    *   **AI Task:** Remove JSON load/save functions.
    *   **AI Task:** Update all workflow API routes to use `Depends(get_db)`.
    *   **AI Task:** Implement DB operations for Workflow CRUD, storing/fetching `WorkflowDefinition` objects.
    *   **AI Task:** In the `execute_workflow` endpoint, after `WorkflowEngine` execution, save the `WorkflowExecutionResult` as a `WorkflowRun` record in PostgreSQL.

5.  **Full System Test Plan (Adaptation & Execution):
    *   **Goal:** Verify MCP & Workflow CRUD and Workflow Execution with PostgreSQL.
    *   **Test Scenarios:**
        1.  Full lifecycle for an MCP (Create, List, Get, Update, Delete) -> check API responses, infer DB state.
        2.  Full lifecycle for a Workflow (Create, List, Get, Update, Delete), including execution of a simple workflow using a DB-stored MCP -> check API responses for workflow and execution results, inferring DB state for `workflow_definitions` and `workflow_runs`.
    *   **AI/User Task:** Review and adapt `tests/test_workflow_execution.py`. While tests primarily target the API, the underlying data source change might require adjustments in setup or assertions if they indirectly relied on file system state or specific error messages from the old system. Ensure tests cover persistence of workflow execution runs.

## Key Considerations for Tomorrow:

*   **SQLAlchemy Model Details:** Pay close attention to JSONB field definitions and relationships if any.
*   **DB Session Management:** Ensure `get_db` dependency correctly provides and closes sessions.
*   **Error Handling:** Implement basic error handling for DB operations.
*   **Test Adaptation:** This is crucial. Existing tests need to pass against the DB-backed system.

Success tomorrow means the application will be operating on a scalable and robust data foundation. 