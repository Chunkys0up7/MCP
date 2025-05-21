# Guides

This document provides guides for testing, extending, and debugging the MCP Frontend application.

## Table of Contents

-   [1. Testing Guide](#1-testing-guide)
    -   [Unit Tests](#unit-tests)
    -   [Integration Tests](#integration-tests)
    -   [End-to-End (E2E) Tests](#end-to-end-e2e-tests)
    -   [Manual Testing Checklist](#manual-testing-checklist)
-   [2. Extensibility Guide](#2-extensibility-guide)
    -   [Adding New Node Types](#adding-new-node-types)
    -   [Adding New Properties to Existing Nodes](#adding-new-properties-to-existing-nodes)
    -   [Adding New API Interactions](#adding-new-api-interactions)
-   [3. Debugging Guide](#3-debugging-guide)
    -   [Browser Developer Tools](#browser-developer-tools)
    -   [React Developer Tools](#react-developer-tools)
    -   [Zustand Developer Tools](#zustand-developer-tools)
    -   [Common Issues](#common-issues)

---

## 1. Testing Guide

Currently, the project has configuration files for Jest (`jest.config.js`) and Vitest (`vitest.config.ts`), and a `setupTests.ts`. However, specific unit or integration tests for components and store logic may not be fully implemented. A `TESTING.md` file also exists which might contain further details.

### Unit Tests

-   **Focus:** Individual functions, components in isolation, store actions (non-API ones).
-   **Tools:** Jest or Vitest.
-   **Examples:**
    -   Test utility functions.
    -   Test reducers/actions in `flowStore.ts` (e.g., `updateNodeData`, `setSelectedNode`) by providing mock state and asserting the new state.
    -   Test React components with mocked props and asserting their rendering output (e.g., using `@testing-library/react`).

### Integration Tests

-   **Focus:** Interactions between components, or components with the store.
-   **Tools:** Jest/Vitest with `@testing-library/react`.
-   **Examples:**
    -   Test if clicking a node in `WorkflowBuilder` updates the `selectedNode` in the store and causes `PropertiesPanel` to display correctly.
    -   Test if dragging a node from `MCPLibrary` and dropping it onto `WorkflowBuilder` adds a node to the store.

### End-to-End (E2E) Tests

-   **Focus:** User flows through the entire application, including API interactions (potentially with a mock backend).
-   **Tools:** Cypress (a `cypress/` directory exists, suggesting its setup).
-   **Examples:**
    -   Full workflow: User loads the app, drags nodes, connects them, edits properties, saves the workflow, executes it, and sees logs.

### Manual Testing Checklist (Core Functionality)

Before any major release or after significant changes, manually test the following:

1.  **Application Load:** Does the app load correctly without console errors?
2.  **Node Drag & Drop (Library to Canvas):**
    -   Can all node types (LLM, Notebook, Data) be dragged from `MCPLibrary` to `WorkflowBuilder`?
    -   Is a new node created with a default label and correct type?
3.  **Node Interaction (Canvas):**
    -   Can nodes be selected by clicking?
    -   Can selected nodes be dragged to new positions?
    -   Can selected nodes be deleted using 'Backspace' or 'Delete' keys?
4.  **Edge Interaction (Canvas):**
    -   Can edges be created by dragging from one node's handle to another?
    -   Can edges be selected by clicking?
    -   Can selected edges be deleted using 'Backspace' or 'Delete' keys?
5.  **Properties Panel (Nodes):**
    -   Does selecting a node display its ID, Type, Label, and Description in the panel?
    -   Can the Label and Description be edited, and do changes reflect on the canvas (label) and in the store?
    -   For LLM nodes: Can the model be selected from the dropdown? Does it update in the store?
    -   For Notebook nodes: Can the Notebook Path be edited? Does it update in the store?
    -   For Data nodes: Can the Data Source be edited? Does it update in the store?
6.  **Properties Panel (Edges):**
    -   Does selecting an edge display its ID, Source, Target, and Label in the panel?
    -   Can the Label be edited, and does it reflect on the canvas and in the store?
7.  **Top Bar Actions (Workflow ID: `demo` or a test ID):
    -   **Save:** Does clicking "Save" trigger a (mocked) API call? Is the `loading` state handled (buttons disabled)?
    -   **Load:** Does clicking "Load" trigger a (mocked) API call and update the canvas with new nodes/edges? Is `loading` handled?
    -   **Execute:** Does clicking "Execute" trigger a (mocked) API call? Is `loading` handled? Are logs displayed in the console?
8.  **Execution Console:**
    -   Does it show loading indicators during API calls?
    -   Does it display error messages from API failures?
    -   Does it display logs from workflow execution?
9.  **Deselection:** Clicking the canvas pane deselects any selected node/edge, and the Properties Panel updates.

---

## 2. Extensibility Guide

### Adding New Node Types

1.  **`MCPLibrary.tsx` (`frontend/src/presentation/features/chain-builder/MCPLibrary.tsx`):**
    -   Add a new entry to the `MCP_TYPES` array. Define its `type` (unique string), `label`, `icon` (choose/create an MUI icon), `description`, and `color`.
    ```javascript
    {
      type: 'new-custom-node',
      label: 'New Custom Node',
      icon: <NewCustomIcon sx={{ color: '#FF5733' }} />,
      description: 'Description for the new node',
      color: '#FF5733',
    }
    ```

2.  **`WorkflowBuilder.tsx` (`frontend/src/presentation/features/chain-builder/WorkflowBuilder.tsx`):**
    -   Add a custom renderer for your new node type to the `nodeTypes` object.
    ```javascript
    const nodeTypes = {
      // ... existing node types
      'new-custom-node': ({ data }) => (
        <div style={{ padding: 10, background: '#ffe0b2', border: '2px solid #FF5733', borderRadius: 5 }}>
          {data.label}
          {/* Add any other custom rendering for this node type */}
        </div>
      ),
    };
    ```
    -   When this new node is dropped, its `data` will initially only contain `{ label: "New Custom Node" }` (or similar, based on `MCPLibrary`).

3.  **`PropertiesPanel.tsx` (`frontend/src/presentation/features/chain-builder/PropertiesPanel.tsx`):**
    -   Add a new conditional block to render specific input fields for your node type's unique properties.
    ```javascript
    // Inside the return statement, after other node type checks
    {selectedNode.type === 'new-custom-node' && (
      <>
        <TextField
          label="Custom Property A"
          value={selectedNode.data.customPropertyA || ''}
          onChange={e => onCustomPropertyAChange && onCustomPropertyAChange(e.target.value)} // You'll need to define onCustomPropertyAChange
          fullWidth
          sx={{ mb: 2 }}
        />
        {/* Add other fields for 'new-custom-node' */}
      </>
    )}
    ```
    -   Update `PropertiesPanelProps` to include any new callback functions (e.g., `onCustomPropertyAChange`).

4.  **`App.tsx` (`frontend/src/App.tsx`):**
    -   If you added new callbacks to `PropertiesPanelProps` (like `onCustomPropertyAChange`), define handler functions in `App.tsx` that call `updateNodeData` from the store with the new property.
    ```javascript
    const handleCustomPropertyAChange = (value: string) => {
      if (selectedNode) updateNodeData(selectedNode.id, { customPropertyA: value });
    };
    // Pass this to PropertiesPanel: onCustomPropertyAChange={handleCustomPropertyAChange}
    ```

5.  **`flowStore.ts` (`frontend/src/store/flowStore.ts`):**
    -   No changes are usually needed here for new node data fields, as `updateNodeData` merges partial data. Ensure your backend can handle these new properties when saving/loading workflows.

6.  **Backend:**
    -   The backend API (`/api/flow`) must be updated to recognize and store any new properties associated with this node type.

### Adding New Properties to Existing Nodes

1.  **`PropertiesPanel.tsx`:** Add the new input field for the existing node type.
2.  **`PropertiesPanelProps`:** Add a new callback prop for the new property.
3.  **`App.tsx`:** Define the handler for the new callback, calling `updateNodeData`.
4.  **Backend:** Ensure the backend can store and retrieve this new property.

### Adding New API Interactions

1.  **`flowApi.ts` (`frontend/src/services/flowApi.ts`):**
    -   Define a new async function for the new API endpoint (e.g., `getWorkflowStatus(id: string)`).
2.  **`flowStore.ts` (`frontend/src/store/flowStore.ts`):**
    -   Add new state variables if needed (e.g., `workflowStatus: string | null`).
    -   Create a new async action (e.g., `fetchWorkflowStatusFromApi`) that calls your new function in `flowApi.ts` and updates the relevant state (loading, error, new state variables).
3.  **Components:** Call the new store action from relevant components and display the new state.

---

## 3. Debugging Guide

### Browser Developer Tools

-   **Console:** Check for JavaScript errors, `console.log` outputs, network request statuses.
-   **Network Tab:** Inspect API requests (`/api/flow/...`) and their responses. Verify payloads, headers, and status codes.
-   **Elements Tab:** Inspect the DOM structure and MUI component styles.

### React Developer Tools (Browser Extension)

-   **Components Tree:** Inspect the props and state of your React components.
-   **Profiler:** Identify performance bottlenecks in rendering.

### Zustand Developer Tools (Middleware/Extension)

-   While Zustand is simple, for complex state changes, you can use `redux-devtools-extension` with Zustand via middleware like `zustand/middleware/devtools`. This allows you to inspect state changes and action history, similar to Redux.
    ```javascript
    // In flowStore.ts
    import { devtools } from 'zustand/middleware'

    export const useFlowStore = create<FlowState>()(devtools((set, get) => ({
      // ... your store definition
    }), { name: "FlowStore" }));
    ```

### Common Issues

1.  **Blank UI / Vite Errors:**
    -   Check the browser console and Vite terminal output for errors.
    -   Ensure `npm install` was successful and dependencies are correct.
    -   Verify `main.tsx` correctly renders `App` into the root DOM element.
2.  **API Calls Failing (404, 500, CORS):**
    -   Check the Network tab in browser dev tools.
    -   Verify the backend server (`run_server.py` or equivalent) is running and accessible at the expected address/port.
    -   Ensure API endpoints in `flowApi.ts` match backend routes.
    -   For CORS errors, ensure the backend server is configured to allow requests from the frontend's origin (e.g., `http://localhost:5173`).
3.  **State Not Updating / UI Not Reflecting Changes:**
    -   Use React DevTools to check component props and state.
    -   Use Zustand DevTools (if integrated) or `console.log` in store actions to trace state changes.
    -   Ensure correct immutability when updating state in Zustand (spread operators `...` are crucial).
    -   Verify that components consuming store state are correctly subscribed and re-rendering.
4.  **ReactFlow Issues (Nodes/Edges not appearing, interactions failing):**
    -   Double-check the `nodes` and `edges` arrays passed to `<ReactFlow>`. They must conform to React Flow's expected structure.
    -   Ensure `onNodesChange`, `onEdgesChange`, `onConnect` are correctly wired to update the store.
    -   Check for errors in custom node components.
5.  **MUI Styling Issues:**
    -   Use the Elements tab to inspect styles. Ensure MUI theme is correctly applied.
    -   Verify `sx` props or `styled` components are correctly implemented. 