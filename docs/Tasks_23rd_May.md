# Tasks for May 23rd (Revised after Status Review)

## Core Module Development (Continuing Phase 4)

1.  **UI - Dashboard Module:**
    *   **Task:** Begin implementation of the "Personalized Feed Screen" focusing on fetching and displaying initial data from the API Gateway. (Ref: `docs/plan` 4.1)
        *   **Status:** COMPLETED - Implemented `PersonalizedFeedScreen` component with:
            *   API integration via `dashboardService`
            *   Loading states and error handling
            *   Responsive grid layout for recommendations, trending components, and team collaborations
            *   Comprehensive unit tests
    *   **Task:** Stub out functions for ML-driven recommendations and real-time system health metrics if backend isn't fully ready.
        *   **Status:** COMPLETED - Implemented service functions in `dashboardService.ts` for:
            *   ML recommendations
            *   Trending components
            *   Team collaborations
            *   All functions are ready to be connected to the backend API

2.  **UI - Component Marketplace:**
    *   **Task:** Start developing the "Faceted Search Screen" UI elements. (Ref: `docs/plan` 4.1)
    *   **Task:** Integrate with a mocked or preliminary version of the Component Registry API for basic search functionality.
    *   **Status:** Not Started (Frontend task). Backend APIs for MCP listing are available; advanced search (pgvector) is pending (see Task 5).

3.  **Backend - API Gateway & Workflow Execution Core Logic (HIGH PRIORITY):**
    *   **Task (Original):** Review existing `/workflows` and `/components/{id}` endpoints for new UI requirements.
        *   **Status:** COMPLETED. `/workflows` endpoints previously reviewed. `/context/*` (MCP/component) endpoints reviewed, and their tests (`tests/api/test_context_api.py`) have been refactored to use a DB-backed test environment with comprehensive checks for CRUD operations, validation, and authentication.
    *   **Focus Task:** **Fully implement dynamic MCP loading and instantiation within the `WorkflowEngine` and `execute_workflow` endpoint.** (Corresponds to original Task 10)
        *   **Sub-task:** Modify `WorkflowEngine` (`mcp/core/workflow_engine.py`) to fetch MCP definitions (ID, type, versioned config) from the DB using `mcp/core/registry.py` service calls for each step in a workflow.
        *   **Status (Sub-task):** COMPLETED - `WorkflowEngine` now accepts a DB session. `run_workflow` calls `registry.get_mcp_instance_from_db` using `step.mcp_id` and `step.mcp_version_id`. `mcp/schemas/workflow.py` updated with `mcp_version_id` in `WorkflowStep`. `mcp/core/registry.py` has `get_mcp_instance_from_db`. `mcp/api/routers/workflows.py` passes DB session to `WorkflowEngine`.
        *   **Sub-task:** Dynamically instantiate the correct `BaseMCPServer` subclass (e.g., `LLMPromptMCP`, `PythonScriptMCP`) within the `WorkflowEngine` using the fetched type and config.
        *   **Status (Sub-task):** COMPLETED - This is handled by `get_mcp_instance_from_db` in `mcp/core/registry.py` which is called by `WorkflowEngine`.
        *   **Sub-task:** Ensure the `execute_workflow` endpoint in `mcp/api/routers/workflows.py` correctly utilizes this refactored `WorkflowEngine` to run workflows with MCPs defined in the database. Address placeholder `current_mcp_registry_for_engine = {}`.
        *   **Status (Sub-task):** COMPLETED - Placeholder removed and `WorkflowEngine` is instantiated with the DB session in `execute_workflow`.
        *   **Status:** Foundational `/execute` endpoint structure exists. `WorkflowRun` DB record creation is in place. **Dynamic loading/instantiation by `WorkflowEngine` is the critical missing piece.**
        *   **Overall Focus Task Status:** COMPLETED - Core dynamic loading logic implemented. Unit tests for `WorkflowEngine` and integration tests for `/execute_workflow` (covering DB-backed MCPs, success, and various failure scenarios) have been added.

4.  **Backend - Workflow Engine (Supporting Logic):**
    *   **Task:** Focus on the `Workflow Parser` and `Schema Validator` components. Ensure it can correctly parse and validate basic workflow definitions received from the API gateway.
    *   **Status:** COMPLETED. Pydantic schemas (`mcp/schemas/workflow.py`) handle structural validation and parsing. The `_resolve_step_inputs` method in `WorkflowEngine` correctly handles input mapping from various sources. Unit tests in `tests/core/test_workflow_engine.py` cover these aspects.

5.  **Backend - Component Registry (Features & Enhancements):**
    *   **Task:** Refine `Schema Validation` for component definitions.
        *   **Sub-task:** Implement type-specific schema validation (e.g., using AJV as mentioned in `docs/System Overview - Full Functional Map`) for the `initial_config: Dict[str, Any]` field in `MCPCreate` based on `MCPType`. This should occur within `save_mcp_definition_to_db` in `mcp/core/registry.py` or a related service.
        *   **Status:** COMPLETED. `save_mcp_definition_to_db` in `mcp/core/registry.py` now validates `initial_config` against the specific Pydantic model corresponding to the `MCPType`. Invalid configs raise a `ValueError`, leading to a 400 HTTP response. The validated and structured config is stored in the DB. Tests for this have been added to `tests/api/test_context_api.py`.
    *   **Task:** Ensure `Semantic Search` (pgvector) is functional for basic natural language queries.
        *   **Sub-task:** Implement `pgvector` indexing on relevant MCP fields in the database model (`mcp/db/models/mcp.py`).
        *   **Status (Sub-task):** COMPLETED. Added `embedding: Vector(384)` field to `MCP` model in `mcp/db/models/mcp.py`. Added `pgvector` to `requirements.txt`.
        *   **Sub-task:** Create service functions in `mcp/core/registry.py` to perform semantic search queries.
        *   **Status (Sub-task):** COMPLETED. Added `_generate_mcp_embedding` helper and `search_mcp_definitions_by_text` function in `mcp/core/registry.py`. Embeddings are generated and stored on MCP create/update. `sentence-transformers` added to `requirements.txt` and model initialized.
        *   **Sub-task:** Expose semantic search capability via a new or modified API endpoint in `mcp/api/main.py`.
        *   **Status (Sub-task):** COMPLETED. Added `GET /context/search` endpoint to `mcp/api/main.py`. Tests for embedding generation and (mocked) API search functionality added to `tests/api/test_context_api.py`.
        *   **Status:** COMPLETED. Foundational pgvector setup, embedding generation, service function, and API endpoint are implemented. Full integration testing with a PostgreSQL DB supporting pgvector is recommended as a next step outside of current test environment.

## Integration & Testing Preparation (Moving towards Phase 5)

6.  **MCD System - Initial Integration Points:**
    *   **Task:** Define and document the precise data format for "Architectural constraints" that the Workflow Engine will consume from the MCD System.
    *   **Status:** COMPLETED. A Pydantic model `ArchitecturalConstraints` has been defined in `mcp/schemas/mcd_constraints.py`. This model includes fields for allowed/prohibited MCP types, max steps, and tag-based constraints. This serves as the initial documented format.
    *   **Task:** Create mock data or a stub service for the MCD system to allow the Workflow Engine to test this handoff.
    *   **Status:** COMPLETED. Mock data representing `ArchitecturalConstraints` has been created and saved to `examples/mcd/sample_constraints.json`. This file can be used for testing integration if the WorkflowEngine is updated to consume these constraints.

7.  **Security Subsystem - JWT & RBAC Review:**
    *   **Task:** Review JWT issuance/validation flow. Document initial RBAC permission checks for Marketplace/Workflow Builder.
    *   **Status:** COMPLETED. JWT issuance/validation flow reviewed. Initial RBAC roles (`user`, `developer`, `admin`) and permission checks for MCP (Marketplace) and Workflow operations have been documented in `docs/security_rbac.md`. Actual RBAC implementation is pending.

8.  **Testing - Unit & Integration Tests (HIGH PRIORITY post-execution logic):**
    *   **Task:** Write/update comprehensive unit tests for MCP CRUD operations (`mcp/core/registry.py`, `mcp/api/main.py`).
        *   **Status:** COMPLETED. `tests/api/test_context_api.py` was refactored for DB-backed API CRUD tests. A new file `tests/core/test_registry.py` was created with unit tests for service functions in `mcp/core/registry.py` covering MCP CRUD, embedding generation (mocked), and search (mocked).
    *   **Task:** Write initial unit tests for the `WorkflowEngine`, focusing on the new dynamic MCP loading logic, input resolution (`_resolve_step_inputs`), and step execution orchestration.
        *   **Status (Sub-task):** COMPLETED - Created `tests/core/test_workflow_engine.py` with tests for engine instantiation, successful execution, step failure, MCP instantiation failure, input resolution for various sources, and a two-step data passing scenario. Mocking is used for DB interactions (`get_mcp_instance_from_db`).
    *   **Task:** Write integration tests for the `execute_workflow` endpoint, covering various success and failure scenarios with DB-backed MCPs.
        *   **Status (Sub-task):** COMPLETED - Updated `tests/api/test_workflow_api.py` to use an in-memory SQLite DB for tests. Added `test_db_session` and `override_get_db` fixtures in `tests/conftest.py`. Refactored MCP and Workflow creation fixtures to use the DB. Added new `/execute` tests for: successful DB-backed execution, MCP definition not found, MCP version not found, MCP instantiation failure due to bad config, and step execution failure. CRUD tests adapted to new DB setup.
        *   **Status:** Overall testing status for core backend components (MCP context, Workflow Engine, Workflow Execution API) significantly improved. Key functionalities have unit and/or integration tests.
    *   **Testing:**
        *   Test files (e.g., `tests/api/test_context_api.py`, `tests/api/test_workflow_api.py`) have been updated to use a file-based SQLite database (`./test.db`) to ensure that all connections (including those from the FastAPI app and the test session) share the same database and tables. This resolves the "no such table" errors encountered previously. Comprehensive unit and integration tests are now being verified for MCP/Workflow CRUD and engine components.

9.  **Documentation - API Endpoint Updates:**
    *   **Task:** Update/create `docs/api_reference.md` with detailed explanations for all `/context/*` and `/workflows/*` endpoints, including the refactored `/execute` endpoint behavior.
    *   **Status:** COMPLETED. `docs/api_reference.md` has been created and populated with details for `/context/*` endpoints (including the new `/context/search`) and `/workflows/*` endpoints (including `/execute` with its DB-backed behavior and `WorkflowRun` considerations).

10. **(Absorbed into Task 3) Planning - Detailed Plan for Workflow Execution:**
    *   **Status:** This task is now the core of the revised **Task 3**. The critical path (dynamic MCP loading by `WorkflowEngine`) has been identified and detailed there. 