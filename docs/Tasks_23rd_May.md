# Tasks for May 23rd

## Core Module Development (Continuing Phase 4)

1.  **UI - Dashboard Module:**
    *   Begin implementation of the "Personalized Feed Screen" focusing on fetching and displaying initial data from the API Gateway. (Ref: `docs/plan` 4.1)
    *   Stub out functions for ML-driven recommendations and real-time system health metrics if backend isn't fully ready.

2.  **UI - Component Marketplace:**
    *   Start developing the "Faceted Search Screen" UI elements. (Ref: `docs/plan` 4.1)
    *   Integrate with a mocked or preliminary version of the Component Registry API for basic search functionality.

3.  **Backend - API Gateway:** (Ref: `docs/plan` 4.2 & `docs/System Overview - Full Functional Map` 2.1)
    *   Review existing `/workflows` and `/components/{id}` endpoints for any new requirements identified during UI development.
    *   Begin implementing the `/execute` endpoint structure, connecting to a stubbed Workflow Engine if the full engine is not yet ready for integration.

4.  **Backend - Workflow Engine:** (Ref: `docs/plan` & `docs/System Overview - Full Functional Map` 4)
    *   Focus on the `Workflow Parser` and `Schema Validator` components. (Ref: `docs/System Overview - Full Functional Map` 4.1)
    *   Ensure it can correctly parse and validate basic workflow definitions received from the API gateway (even if execution is not fully implemented).

5.  **Backend - Component Registry:** (Ref: `docs/plan` & `docs/System Overview - Full Functional Map` 3)
    *   Refine `Schema Validation` (AJV) for component definitions. (Ref: `docs/System Overview - Full Functional Map` 3.1)
    *   Ensure `Semantic Search` (pgvector) is functional for basic natural language queries.

## Integration & Testing Preparation (Moving towards Phase 5)

6.  **MCD System - Initial Integration Points:** (Ref: `docs/System Overview - Full Functional Map` 7.2)
    *   Define and document the precise data format for "Architectural constraints" that the Workflow Engine will consume from the MCD System.
    *   Create mock data or a stub service for the MCD system to allow the Workflow Engine to test this handoff.

7.  **Security Subsystem - JWT & RBAC Review:** (Ref: `docs/System Overview - Full Functional Map` 8.1)
    *   Review JWT issuance/validation flow between AuthN service, API Gateway, and UI.
    *   Document initial RBAC permission checks required for early versions of Marketplace and Workflow Builder.

8.  **Testing - Unit Tests for Core Logic:** (Ref: `docs/remaining_tasks_22nd_May.md` 5)
    *   Write/update unit tests for any new or significantly modified logic in `mcp/core/registry.py` and `mcp/api/main.py` related to MCP CRUD.
    *   Write initial unit tests for the Workflow Engine's parser and schema validator.

9.  **Documentation - API Endpoint Updates:**
    *   Update `docs/api_reference.md` (or equivalent) with any changes or additions to the `/context/*` and `/workflows/*` endpoints.
    *   Document the expected request/response for the new `/execute` endpoint (even if preliminary).

10. **Planning - Detailed Plan for Workflow Execution:**
    *   Outline the remaining steps and dependencies for fully implementing the `execute_workflow` endpoint in `mcp/api/routers/workflows.py`. (Ref: `mcp/api/routers/workflows.py` comments around line 260+).
    *   Specifically address how the `WorkflowEngine` will dynamically load and instantiate MCPs from the database. 