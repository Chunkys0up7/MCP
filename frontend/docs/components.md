# Component Documentation

This document provides an overview of the key React components used in the MCP Frontend application.

## Table of Components

-   [`App.tsx`](#apptsx)
-   [`WorkflowBuilder.tsx`](#workflowbuildertsx)
-   [`MCPLibrary.tsx`](#mcplibrarytsx)
-   [`PropertiesPanel.tsx`](#propertiespaneltsx)
-   [`ExecutionConsole.tsx`](#executionconsoletsx)

---

## `App.tsx`

-   **File:** `frontend/src/App.tsx`
-   **Purpose:** The root component of the application. It sets up the main layout, theme, and orchestrates the major UI sections (Top Bar, Sidebar, Canvas, Properties Panel, Execution Console).

### Responsibilities

-   Initializes the Material UI `ThemeProvider` and `CssBaseline`.
-   Defines the overall page structure using MUI `Box` components for layout.
-   Connects to the `useFlowStore` to access global state and actions.
-   Renders the top bar containing the application title, workflow ID input, and Load/Save/Execute buttons.
-   Renders the `MCPLibrary`, `WorkflowBuilder`, `PropertiesPanel`, and `ExecutionConsole` components.
-   Manages the `workflowId` local state for the input field.
-   Provides callback functions (e.g., `handleLabelChange`, `handleDescriptionChange`) to `PropertiesPanel` which in turn call `useFlowStore` actions to update node/edge data.
-   Maps `selectedNode` and `selectedEdge` from the store to a simplified structure (`panelNode`, `panelEdge`) for `PropertiesPanel`.
-   (Previously) Contained a `useEffect` to set initial test nodes/edges (this logic might evolve for production scenarios).

### Key Props Received

-   None (it's the root component).

### Key State/Store Usage

-   Uses `useFlowStore` for:
    -   `nodes`, `edges`: To potentially pass to children or for direct manipulation (though `WorkflowBuilder` also accesses these directly).
    -   `selectedNode`, `selectedEdge`: To determine what to show in `PropertiesPanel`.
    -   `updateNodeData`, `updateEdgeLabel`: Used by its internal handlers that are passed to `PropertiesPanel`.
    -   `loading`, `error`, `logs`: Passed to `ExecutionConsole` and used for disabling top bar buttons.
    -   `loadWorkflowFromApi`, `saveWorkflowToApi`, `executeWorkflowFromApi`: Called by top bar buttons.
-   Local React State:
    -   `workflowId: string`: Stores the current value of the workflow ID text field.

### Core Functions/Event Handlers

-   `handleLabelChange`, `handleDescriptionChange`, `handleModelChange`, `handlePathChange`, `handleSourceChange`: These functions are passed to `PropertiesPanel` and are called when a node's property is changed. They invoke `updateNodeData` from the store.
-   `handleEdgeLabelChange`: Passed to `PropertiesPanel` for edge label changes, invoking `updateEdgeLabel` from the store.
-   Top bar button `onClick` handlers: Directly call `loadWorkflowFromApi`, `saveWorkflowToApi`, or `executeWorkflowFromApi` with the current `workflowId`.

---

## `WorkflowBuilder.tsx`

-   **File:** `frontend/src/presentation/features/chain-builder/WorkflowBuilder.tsx`
-   **Purpose:** Renders the main interactive canvas where users build their workflows using ReactFlow.

### Responsibilities

-   Initializes and configures the ReactFlow instance.
-   Displays nodes and edges based on the data from `useFlowStore`.
-   Defines custom node appearances (e.g., for `llm`, `notebook`, `data` types).
-   Handles drag-and-drop of new nodes from `MCPLibrary` onto the canvas.
-   Manages node/edge selection, deletion, and connection.
-   Includes ReactFlow UI elements like `Background`, `Controls`, and `MiniMap`.

### Key Props Received

-   None (it consumes state directly from `useFlowStore`).

### Key State/Store Usage

-   Uses `useFlowStore` for:
    -   `nodes`, `edges`: To render the flow.
    -   `setNodes`, `setEdges`: To update the flow based on user interactions (drag, connect, delete, drop).
    -   `setSelectedNode`, `setSelectedEdge`: To update the selection state when nodes/edges/pane are clicked.
-   Local React State:
    -   `reactFlowInstance: ReactFlowInstance | null`: Stores the ReactFlow instance, used for projecting coordinates during drag-and-drop.

### Core Functions/Event Handlers

-   `onNodesChange(changes: NodeChange[])`: Handles node changes (position, removal). Calls `setNodes` via `applyNodeChanges`.
-   `onEdgesChange(changes: EdgeChange[])`: Handles edge changes (removal). Calls `setEdges` via `applyEdgeChanges`.
-   `onConnect(connection: Connection)`: Handles new edge creation. Calls `setEdges` via `addEdge`.
-   `onDragOver(event: React.DragEvent)`: Prevents default behavior to allow dropping.
-   `onDrop(event: React.DragEvent)`: Handles dropping a new node from `MCPLibrary`. Calculates position, creates a new node object, and calls `setNodes` (via `applyNodeChanges`) to add it to the store.
-   `onNodeClick(_: any, node: Node)`: Calls `setSelectedNode` and clears `selectedEdge`.
-   `onEdgeClick(event: React.MouseEvent, edge: Edge)`: Calls `setSelectedEdge` and clears `selectedNode`.
-   `onPaneClick()`: Clears both `selectedNode` and `selectedEdge`.
-   `onInit(instance: ReactFlowInstance)`: Sets the `reactFlowInstance` state.
-   `nodeTypes`: An object mapping node type strings to custom React components for rendering them.

---

## `MCPLibrary.tsx`

-   **File:** `frontend/src/presentation/features/chain-builder/MCPLibrary.tsx`
-   **Purpose:** Displays a sidebar with available node types that can be dragged onto the `WorkflowBuilder` canvas.

### Responsibilities

-   Defines the list of available MCP node types (`MCP_TYPES`), including their labels, icons, descriptions, and colors.
-   Renders each node type as a draggable `ListItemButton`.
-   Initiates the drag operation with necessary data for `WorkflowBuilder`.

### Key Props Received

-   None.

### Key State/Store Usage

-   None.

### Core Functions/Event Handlers

-   `handleDragStart(event: React.DragEvent, type: string)`: Called when a node type item drag begins.
    -   Sets `event.dataTransfer.setData('application/reactflow', type)` to make the node `type` available on drop.
    -   Sets `event.dataTransfer.effectAllowed = 'move'`.

---

## `PropertiesPanel.tsx`

-   **File:** `frontend/src/presentation/features/chain-builder/PropertiesPanel.tsx`
-   **Purpose:** Displays and allows editing of properties for the currently selected node or edge.

### Responsibilities

-   Conditionally renders content based on whether a node, an edge, or nothing is selected.
-   If an edge is selected: Displays Edge ID, Source, Target, and a `TextField` for its label.
-   If a node is selected: Displays Node ID, Type, and `TextField`s for Label and Description.
    -   Renders additional type-specific fields (e.g., Model `Select` for 'llm', Notebook Path `TextField` for 'notebook', Data Source `TextField` for 'data').
-   If nothing is selected: Displays a placeholder message.

### Key Props Received

-   `selectedNode: { id, type, data: { label, description?, model?, path?, source? } } | null`: The currently selected node's data (or null).
-   `selectedEdge: { id, source, target, label } | null`: The currently selected edge's data (or null).
-   `onLabelChange?: (label: string) => void`: Callback when node label changes.
-   `onDescriptionChange?: (description: string) => void`: Callback when node description changes.
-   `onModelChange?: (model: string) => void`: Callback when LLM node model changes.
-   `onPathChange?: (path: string) => void`: Callback when Notebook node path changes.
-   `onSourceChange?: (source: string) => void`: Callback when Data node source changes.
-   `onEdgeLabelChange?: (label: string) => void`: Callback when edge label changes.

### Key State/Store Usage

-   None directly. It operates purely on props.

### Core Functions/Event Handlers

-   Input field `onChange` handlers: These directly call the corresponding prop functions (e.g., `onLabelChange(e.target.value)`), which are wired in `App.tsx` to update the Zustand store.

---

## `ExecutionConsole.tsx`

-   **File:** `frontend/src/presentation/features/chain-builder/ExecutionConsole.tsx`
-   **Purpose:** Displays feedback from backend operations, such as loading indicators, error messages, and execution logs.

### Responsibilities

-   Displays a title "Execution Console".
-   Shows a `CircularProgress` spinner if the `loading` prop is true.
-   Displays an `Alert` with an error message if the `error` prop is set.
-   Renders a list of log messages from the `logs` prop.
    -   Normalizes string logs into `LogEntry` objects with type 'info'.
    -   Styles log messages based on their type (error, success, info).
    -   Provides a scrollable area for logs.
    -   Shows "No logs yet." if there are no logs, not loading, and no error.

### Key Props Received

-   `loading?: boolean`: Indicates if a backend operation is in progress.
-   `error?: string | null`: Error message from a failed operation.
-   `logs?: (LogEntry | string)[]`: Array of log entries or raw strings.

### Key State/Store Usage

-   None directly. It operates purely on props.

### Core Functions/Event Handlers

-   Log normalization logic: Converts string entries in the `logs` prop to `LogEntry` objects. 