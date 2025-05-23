# Tasks for May 23rd (Revised after Status Review)

## Core Module Development (Continuing Phase 4)

1.  **UI - Dashboard Module:**
    *   **Task:** Begin implementation of the "Personalized Feed Screen" focusing on fetching and displaying initial data from the API Gateway. (Ref: `docs/plan` 4.1)
    *   **Task:** Stub out functions for ML-driven recommendations and real-time system health metrics if backend isn't fully ready.
    *   **Status:** Not Started (Frontend task). Backend APIs for MCP listing are available.

2.  **UI - Component Marketplace:**
    *   **Task:** Start developing the "Faceted Search Screen" UI elements. (Ref: `docs/plan` 4.1)
    *   **Task:** Integrate with a mocked or preliminary version of the Component Registry API for basic search functionality.
    *   **Status:** Not Started (Frontend task). Backend APIs for MCP listing are available; advanced search (pgvector) is pending (see Task 5).

3.  **Backend - API Gateway & Workflow Execution Core Logic (HIGH PRIORITY):**
    *   **Task (Original):** Review existing `/workflows` and `/components/{id}` endpoints for new UI requirements.
        *   **Status:** Ongoing. Core CRUD for these definitions is implemented and DB-integrated. Review as UI progresses.
    *   **Focus Task:** **Fully implement dynamic MCP loading and instantiation within the `WorkflowEngine` and `execute_workflow` endpoint.** (Corresponds to original Task 10)
        *   **Sub-task:** Modify `WorkflowEngine` (`mcp/core/workflow_engine.py`) to fetch MCP definitions (ID, type, versioned config) from the DB using `mcp/core/registry.py` service calls for each step in a workflow.
        *   **Status (Sub-task):** COMPLETED - `WorkflowEngine` now accepts a DB session. `run_workflow` calls `registry.get_mcp_instance_from_db` using `step.mcp_id` and `step.mcp_version_id`. `mcp/schemas/workflow.py` updated with `mcp_version_id` in `WorkflowStep`. `mcp/core/registry.py` has `get_mcp_instance_from_db`. `mcp/api/routers/workflows.py` passes DB session to `WorkflowEngine`.
        *   **Sub-task:** Dynamically instantiate the correct `BaseMCPServer` subclass (e.g., `LLMPromptMCP`, `PythonScriptMCP`) within the `WorkflowEngine` using the fetched type and config.
        *   **Status (Sub-task):** COMPLETED - This is handled by `get_mcp_instance_from_db` in `mcp/core/registry.py` which is called by `WorkflowEngine`.
        *   **Sub-task:** Ensure the `execute_workflow` endpoint in `mcp/api/routers/workflows.py` correctly utilizes this refactored `WorkflowEngine` to run workflows with MCPs defined in the database. Address placeholder `current_mcp_registry_for_engine = {}`.
        *   **Status (Sub-task):** COMPLETED - Placeholder removed and `WorkflowEngine` is instantiated with the DB session in `execute_workflow`.
        *   **Status:** Foundational `/execute` endpoint structure exists. `WorkflowRun` DB record creation is in place. **Dynamic loading/instantiation by `WorkflowEngine` is the critical missing piece.**
        *   **Overall Focus Task Status:** Partially Complete. Core dynamic loading logic is implemented. Further testing and integration needed.

4.  **Backend - Workflow Engine (Supporting Logic):**
    *   **Task:** Focus on the `Workflow Parser` and `Schema Validator` components. Ensure it can correctly parse and validate basic workflow definitions received from the API gateway.
    *   **Status:** Largely implemented via Pydantic schemas (`mcp/schemas/workflow.py`) for structural validation and parsing. `_resolve_step_inputs` in `WorkflowEngine` handles input mapping. Further semantic validation (e.g., step dependencies for future parallel execution) could be a future enhancement.

5.  **Backend - Component Registry (Features & Enhancements):**
    *   **Task:** Refine `Schema Validation` for component definitions.
        *   **Sub-task:** Implement type-specific schema validation (e.g., using AJV as mentioned in `docs/System Overview - Full Functional Map`) for the `initial_config: Dict[str, Any]` field in `MCPCreate` based on `MCPType`. This should occur within `save_mcp_definition_to_db` in `mcp/core/registry.py` or a related service.
        *   **Status:** Currently, only Pydantic validation on `MCPCreate` schema exists. Type-specific config validation is not yet implemented.
    *   **Task:** Ensure `Semantic Search` (pgvector) is functional for basic natural language queries.
        *   **Sub-task:** Implement `pgvector` indexing on relevant MCP fields in the database model (`mcp/db/models/mcp.py`).
        *   **Sub-task:** Create service functions in `mcp/core/registry.py` to perform semantic search queries.
        *   **Sub-task:** Expose semantic search capability via a new or modified API endpoint in `mcp/api/main.py`.
        *   **Status:** Mentioned in planning docs, but no visible implementation in models, registry, or API layers yet.

## Integration & Testing Preparation (Moving towards Phase 5)

6.  **MCD System - Initial Integration Points:**
    *   **Task:** Define and document the precise data format for "Architectural constraints" that the Workflow Engine will consume from the MCD System.
    *   **Task:** Create mock data or a stub service for the MCD system to allow the Workflow Engine to test this handoff.
    *   **Status:** Not Started. (Ref: `docs/System Overview - Full Functional Map` 7.2)

7.  **Security Subsystem - JWT & RBAC Review:**
    *   **Task:** Review JWT issuance/validation flow. Document initial RBAC permission checks for Marketplace/Workflow Builder.
    *   **Status:** JWT validation is active. Auth router exists. Detailed RBAC permission logic for specific features is pending documentation and implementation.

8.  **Testing - Unit & Integration Tests (HIGH PRIORITY post-execution logic):**
    *   **Task:** Write/update comprehensive unit tests for MCP CRUD operations (`mcp/core/registry.py`, `mcp/api/main.py`).
        *   **Status:** Verify recently added test files (e.g., `tests/api/test_context_api.py`). Augment as needed.
    *   **Task:** Write initial unit tests for the `WorkflowEngine`, focusing on the new dynamic MCP loading logic, input resolution (`_resolve_step_inputs`), and step execution orchestration.
        *   **Status (Sub-task):** COMPLETED - Created `tests/core/test_workflow_engine.py` with tests for engine instantiation, successful execution, step failure, MCP instantiation failure, input resolution for various sources, and a two-step data passing scenario. Mocking is used for DB interactions (`get_mcp_instance_from_db`).
    *   **Task:** Write integration tests for the `execute_workflow` endpoint, covering various success and failure scenarios with DB-backed MCPs.
        *   **Status:** Verify recently added test files (e.g., `tests/api/test_workflow_api.py`). Augment for new engine logic and DB interactions.

9.  **Documentation - API Endpoint Updates:**
    *   **Task:** Update/create `docs/api_reference.md` with detailed explanations for all `/context/*` and `/workflows/*` endpoints, including the refactored `/execute` endpoint behavior.
    *   **Status:** FastAPI auto-generated docs exist. Dedicated markdown reference needs attention.

10. **(Absorbed into Task 3) Planning - Detailed Plan for Workflow Execution:**
    *   **Status:** This task is now the core of the revised **Task 3**. The critical path (dynamic MCP loading by `WorkflowEngine`) has been identified and detailed there. 