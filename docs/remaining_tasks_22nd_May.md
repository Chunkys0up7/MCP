# Remaining Tasks for Database Integration (as of May 22nd)

This list is based on the plan outlined in `docs/up.md` and a review of the current codebase.

## 1. Environment & Configuration
- [x] Implement `.env` file loading for database (PostgreSQL) credentials in `mcp/db/session.py`.
- [x] Implement `.env` file loading for Redis credentials in `mcp/cache/redis_manager.py`.

## 2. Database Models
- [x] Create `WorkflowDefinition` SQLAlchemy model in `mcp/db/models/` (e.g., `mcp/db/models/workflow.py` or a new file).
    - Suggested fields: `workflow_id` (UUID, primary_key), `name` (String), `description` (Text, nullable), `steps` (JSONB), `created_at` (DateTime), `updated_at` (DateTime).
- [x] Create `WorkflowRun` SQLAlchemy model in `mcp/db/models/` (e.g., in the same file as `WorkflowDefinition`).
    - Suggested fields: `run_id` (UUID, primary_key), `workflow_id` (UUID, ForeignKey to `WorkflowDefinition.workflow_id`), `status` (String), `started_at` (DateTime), `finished_at` (DateTime, nullable), `inputs` (JSONB, nullable), `outputs` (JSONB, nullable), `step_results` (JSONB, nullable), `error_message` (Text, nullable).
- [x] Ensure new models (`WorkflowDefinition`, `WorkflowRun`) are included in Alembic migrations and that new migration scripts are generated and applied to create these tables.

## 3. Refactor MCP Registry & Persistence
- **In `mcp/core/registry.py`:**
    - [x] Remove JSON file loading logic (e.g., `load_mcp_servers`, references to `MCP_STORAGE_FILE`).
    - [x] Remove JSON file saving logic (e.g., `save_mcp_servers`).
    - [x] Implement `load_mcp_definition_from_db(db: Session, mcp_id: str) -> Optional[MCP]`. (Uses existing `MCP` model from `mcp.db.models.mcp`).
    - [x] Implement `load_all_mcp_definitions_from_db(db: Session) -> List[MCP]`.
    - [ ] Implement `save_mcp_definition_to_db(db: Session, mcp_data: MCPCreateSchema) -> MCP`. (Define `MCPCreateSchema` Pydantic model if not existing).
    - [ ] Implement `update_mcp_definition_in_db(db: Session, mcp_id: str, mcp_update_data: MCPUpdateSchema) -> Optional[MCP]`. (Define `MCPUpdateSchema`).
    - [ ] Implement `delete_mcp_definition_from_db(db: Session, mcp_id: str) -> bool`.
- **In `mcp/api/main.py` (MCP/Context API Routes):**
    - [ ] Modify `get_all_mcp_servers` (`/context` GET) to use `Depends(get_db)` and `load_all_mcp_definitions_from_db`. Adapt response to `List[MCPDetail]`.
    - [ ] Modify `get_mcp_server_details` (`/context/{server_id}` GET) to use `Depends(get_db)` and `load_mcp_definition_from_db`. Adapt response to `MCPDetail`.
    - [ ] Modify `create_mcp_server` (`/context` POST) to use `Depends(get_db)` and `save_mcp_definition_to_db`.
        - Review how MCP instances (`BaseMCPServer` subclasses) are created and managed if the global `mcp_server_registry` for live instances is still populated from DB data on startup or on demand.
    - [ ] Modify `delete_mcp_server` (`/context/{server_id}` DELETE) to use `Depends(get_db)` and `delete_mcp_definition_from_db`.
    - [ ] Add/Modify an MCP update endpoint (e.g., `/context/{server_id}` PUT) to use `Depends(get_db)` and `update_mcp_definition_in_db`.

## 4. Refactor Workflow Persistence
- **In `mcp/api/routers/workflows.py`:**
    - [ ] Remove JSON file loading logic (e.g., `load_workflows_from_storage`, references to `WORKFLOW_STORAGE_FILE`).
    - [ ] Remove JSON file saving logic (e.g., `save_workflows_to_storage`).
    - [ ] Update `create_workflow` endpoint:
        - Use `Depends(get_db)`.
        - Save the `WorkflowCreate` data as a `WorkflowDefinition` object to PostgreSQL.
    - [ ] Update `list_workflows` endpoint:
        - Use `Depends(get_db)`.
        - Fetch a list of `WorkflowDefinition` objects from PostgreSQL.
    - [ ] Update `get_workflow` endpoint:
        - Use `Depends(get_db)`.
        - Fetch a specific `WorkflowDefinition` object from PostgreSQL.
    - [ ] Update `update_workflow` endpoint:
        - Use `Depends(get_db)`.
        - Update the corresponding `WorkflowDefinition` object in PostgreSQL.
    - [ ] Update `delete_workflow` endpoint:
        - Use `Depends(get_db)`.
        - Delete the `WorkflowDefinition` object from PostgreSQL.
    - [ ] Update `execute_workflow` endpoint:
        - Ensure it uses `Depends(get_db)`.
        - After `WorkflowEngine` execution, create and save a `WorkflowRun` record to PostgreSQL with the execution details (status, inputs, outputs, errors, timings).

## 5. Testing
- [ ] Review and adapt existing tests in `tests/test_workflow_execution.py` to ensure they correctly assert behavior with database persistence for workflows and workflow runs.
- [ ] Review existing tests or create new tests for MCP CRUD operations, ensuring they validate interactions with the database.
- [ ] Execute all relevant tests to confirm that the system functions as expected after the database migration. 