# Data Flow and State Management

This document details how data flows through the MCP Frontend application, with a primary focus on the Zustand store (`frontend/src/store/flowStore.ts`) and its interactions with components and backend services.

## 1. Zustand Store (`flowStore.ts`)

The global application state is centralized in a Zustand store. This store is the single source of truth for workflow data, UI selections, and backend interaction states.

### State Variables

The store maintains the following state variables:

-   `nodes: Node[]`: An array of React Flow `Node` objects representing the elements on the workflow canvas.
-   `edges: Edge[]`: An array of React Flow `Edge` objects representing the connections between nodes.
-   `selectedNode: Node | null`: The currently selected node on the canvas. Null if no node is selected.
-   `selectedEdge: Edge | null`: The currently selected edge on the canvas. Null if no edge is selected.
-   `loading: boolean`: A boolean flag indicating if a backend operation (load, save, execute) is currently in progress. Used to disable UI elements and show loading indicators.
-   `error: string | null`: Stores an error message string if a backend operation fails. Null otherwise.
-   `logs: string[] | LogEntry[]`: An array of strings or `LogEntry` objects representing logs from workflow execution or other operations. Displayed in the Execution Console.

### Core Actions (Setters & Updaters)

These functions are used to modify the state. Many are directly called by components or other actions.

-   `setNodes(nodes: Updater<Node[]>)`: Updates the `nodes` array. It can accept a new array or an updater function (e.g., used by React Flow's `applyNodeChanges`).
-   `setEdges(edges: Updater<Edge[]>)`: Updates the `edges` array. Similar to `setNodes`, it accepts a new array or an updater function (e.g., used by React Flow's `applyEdgeChanges` and `addEdge`).
-   `setSelectedNode(node: Node | null)`: Sets the `selectedNode`. When a node is selected, `selectedEdge` is automatically set to `null` to ensure mutual exclusivity.
-   `setSelectedEdge(edge: Edge | null)`: Sets the `selectedEdge`. When an edge is selected, `selectedNode` is automatically set to `null`.
-   `updateNodeData(nodeId: string, data: Partial<Node['data']>)`: Updates the `data` object of a specific node by its ID. It merges the provided partial data with the existing data. If the updated node is currently selected, `selectedNode` is also updated to reflect the changes immediately.
-   `updateEdgeLabel(edgeId: string, label: string)`: Updates the `label` of a specific edge by its ID. If the updated edge is currently selected, `selectedEdge` is also updated.

### Backend Integration Actions

These asynchronous actions interact with the backend API (`frontend/src/services/flowApi.ts`) and manage the `loading`, `error`, and `logs` state variables accordingly.

-   `loadWorkflowFromApi(id: string): Promise<void>`:
    1.  Sets `loading` to `true`, clears `error`.
    2.  Calls `flowApi.loadWorkflow(id)`.
    3.  On success: Updates `nodes` and `edges` with the fetched data, sets `loading` to `false`.
    4.  On error: Sets the `error` message, sets `loading` to `false`.
-   `saveWorkflowToApi(id: string): Promise<void>`:
    1.  Sets `loading` to `true`, clears `error`.
    2.  Retrieves current `nodes` and `edges` from the store using `get()`.
    3.  Calls `flowApi.saveWorkflow(id, nodes, edges)`.
    4.  On success: Sets `loading` to `false`.
    5.  On error: Sets the `error` message, sets `loading` to `false`.
-   `executeWorkflowFromApi(id: string): Promise<void>`:
    1.  Sets `loading` to `true`, clears `error` and existing `logs`.
    2.  Calls `flowApi.executeWorkflow(id)`.
    3.  On success: Updates `logs` with the logs received from the API, sets `loading` to `false`. (The `result` field from the API is currently not stored).
    4.  On error: Sets the `error` message, sets `loading` to `false`.

## 2. Data Flow in Components

### `App.tsx` (Orchestrator)

-   **Consumes Store:** `App.tsx` connects to the `useFlowStore` to get most of the global state (`nodes`, `edges`, `selectedNode`, `selectedEdge`, `loading`, `error`, `logs`) and actions (`loadWorkflowFromApi`, `saveWorkflowToApi`, `executeWorkflowFromApi`, `updateNodeData`, `updateEdgeLabel`).
-   **Props Drilling:** It passes relevant pieces of state and callback handlers to its child components:
    -   To `WorkflowBuilder`: indirectly, as `WorkflowBuilder` also uses the store.
    -   To `PropertiesPanel`: `selectedNode` (mapped to `panelNode`), `selectedEdge` (mapped to `panelEdge`), and change handlers (`handleLabelChange`, etc.) which directly call store updaters.
    -   To `ExecutionConsole`: `loading`, `error`, `logs`.
-   **Top Bar Interaction:** The Workflow ID `TextField` and Load/Save/Execute `Button`s in `App.tsx` directly trigger the corresponding backend integration actions from the store.

### `WorkflowBuilder.tsx` (Canvas)

-   **Consumes Store:** Directly uses `useFlowStore` to get `nodes`, `edges`, `setNodes`, `setEdges`, `setSelectedNode`, `setSelectedEdge`.
-   **React Flow Interaction:**
    -   **Node/Edge Rendering:** Passes `nodes` and `edges` from the store to the `<ReactFlow>` component.
    -   **Changes (Drag, Delete):** `onNodesChange` and `onEdgesChange` handlers receive change events from React Flow. They use `applyNodeChanges` and `applyEdgeChanges` utilities to compute the new state and then call `setNodes` and `setEdges` (from the store) to update the global state.
    -   **Connections:** `onConnect` handler receives connection events from React Flow. It uses the `addEdge` utility to create a new edge object and calls `setEdges` (from the store).
    -   **Selection:** `onNodeClick`, `onEdgeClick`, `onPaneClick` handlers call `setSelectedNode` and `setSelectedEdge` from the store to update selection state.
    -   **Drag and Drop (New Node):** The `onDrop` handler (when a node is dragged from `MCPLibrary`) creates a new node object and adds it to the store using `setNodes` (via `applyNodeChanges`).

### `MCPLibrary.tsx` (Sidebar)

-   **No Direct Store Interaction (for data flow):** Its primary role is to initiate a drag operation.
-   **`onDragStart`:** Sets drag data (`application/reactflow` with the node `type`) which is then picked up by `WorkflowBuilder`'s `onDrop` handler.

### `PropertiesPanel.tsx`

-   **Receives Props:** Gets `selectedNode` and `selectedEdge` data (already processed in `App.tsx`) and change handler functions (`onLabelChange`, `onDescriptionChange`, etc.) as props.
-   **Data Display:** Renders UI elements based on the `selectedNode` or `selectedEdge` data.
-   **Data Modification:** When a user edits a field (e.g., a node's label in a `TextField`), the corresponding `onChange` prop is called. This prop (e.g., `onLabelChange`) is a function passed down from `App.tsx` that directly invokes a store update action (e.g., `updateNodeData`).

### `ExecutionConsole.tsx`

-   **Receives Props:** Gets `loading`, `error`, and `logs` as props from `App.tsx`.
-   **Data Display:** Renders these states accordingly (spinner for loading, alert for error, list of logs).

## 3. Backend API Interaction (`flowApi.ts`)

-   All direct backend communication is encapsulated in `frontend/src/services/flowApi.ts`.
-   It uses `axios` for making HTTP requests to `/api/flow` endpoints.
-   **`loadWorkflow(id)`:** `GET /api/flow/{id}`
-   **`saveWorkflow(id, nodes, edges)`:** `POST /api/flow/{id}` with `{ nodes, edges }` in the body.
-   **`executeWorkflow(id)`:** `POST /api/flow/{id}/execute`.
-   These API functions are called exclusively by the Zustand store actions (`loadWorkflowFromApi`, `saveWorkflowToApi`, `executeWorkflowFromApi`). The components themselves do not call these API functions directly, promoting a clear separation of concerns.

This centralized state management approach with Zustand, combined with clear action dispatching and service encapsulation, helps maintain a predictable and manageable data flow throughout the application. 