# Frontend API Service (`flowApi.ts`)

This document describes the frontend API service module, `frontend/src/services/flowApi.ts`, which is responsible for all communication with the backend `/api/flow` endpoints.

## Overview

The `flowApi.ts` service uses the `axios` library to make HTTP requests. It encapsulates the logic for fetching workflow data, saving workflows, and triggering workflow executions.

All functions in this service are asynchronous and return Promises.

## API Base URL

-   `API_BASE = '/api/flow'`

## Functions

### 1. `loadWorkflow(id: string): Promise<{ nodes: Node[]; edges: Edge[] }>`

-   **Purpose:** Fetches an existing workflow from the backend.
-   **Method:** `GET`
-   **Endpoint:** `${API_BASE}/${id}` (e.g., `/api/flow/demo_workflow`)
-   **Parameters:**
    -   `id: string`: The unique identifier of the workflow to load.
-   **Response (on success - status 200 OK):**
    -   An object containing:
        -   `nodes: Node[]`: An array of React Flow `Node` objects.
        -   `edges: Edge[]`: An array of React Flow `Edge` objects.
-   **Error Handling:** If the request fails (e.g., network error, server error like 404 Not Found or 500 Internal Server Error), `axios` will throw an error which is then caught by the calling action in `flowStore.ts`.

### 2. `saveWorkflow(id: string, nodes: Node[], edges: Edge[]): Promise<void>`

-   **Purpose:** Saves the current state of a workflow (its nodes and edges) to the backend.
-   **Method:** `POST`
-   **Endpoint:** `${API_BASE}/${id}` (e.g., `/api/flow/demo_workflow`)
-   **Parameters:**
    -   `id: string`: The unique identifier of the workflow to save.
    -   `nodes: Node[]`: An array of current React Flow `Node` objects.
    -   `edges: Edge[]`: An array of current React Flow `Edge` objects.
-   **Request Body:**
    ```json
    {
      "nodes": [/* ...array of Node objects... */],
      "edges": [/* ...array of Edge objects... */]
    }
    ```
-   **Response (on success - status 200 OK or 201 Created):**
    -   Typically no explicit body content is expected by the frontend for this operation, but the backend should confirm success.
-   **Error Handling:** `axios` errors are caught by the calling action in `flowStore.ts`.

### 3. `executeWorkflow(id: string): Promise<{ logs: string[]; result: any }>`

-   **Purpose:** Triggers the execution of a specified workflow on the backend.
-   **Method:** `POST`
-   **Endpoint:** `${API_BASE}/${id}/execute` (e.g., `/api/flow/demo_workflow/execute`)
-   **Parameters:**
    -   `id: string`: The unique identifier of the workflow to execute.
-   **Request Body:**
    -   No body is sent by the frontend for this request currently.
-   **Response (on success - status 200 OK):**
    -   An object containing:
        -   `logs: string[]`: An array of strings representing execution logs.
        -   `result: any`: The result of the workflow execution (the structure of `result` is defined by the backend and currently not deeply inspected or used by the frontend beyond being available).
-   **Error Handling:** `axios` errors are caught by the calling action in `flowStore.ts`.

## Usage

These API service functions are not called directly by React components. Instead, they are invoked by the asynchronous actions within the Zustand store (`frontend/src/store/flowStore.ts`):

-   `loadWorkflowFromApi` calls `loadWorkflow`.
-   `saveWorkflowToApi` calls `saveWorkflow`.
-   `executeWorkflowFromApi` calls `executeWorkflow`.

This separation ensures that API interaction logic is centralized and components remain decoupled from the specifics of backend communication, relying on the store to manage these operations and their resulting states (loading, error, data). 