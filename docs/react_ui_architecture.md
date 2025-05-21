# MCP Chain Builder React UI Architecture

## 1. Project Structure

```
src/
  api/                # API clients (axios)
  components/         # UI components (Sidebar, Toolbar, Node, etc.)
  pages/              # Top-level pages (ChainBuilder, Dashboard, etc.)
  state/              # Zustand store or Redux slices
  utils/              # Utility functions (validation, helpers)
  App.tsx             # Main app shell (routing, layout)
  index.tsx           # Entry point
```

## 2. Component Map

- `Sidebar` (navigation, MCP library, quick actions)
- `Toolbar` (undo/redo, zoom, run, minimap)
- `ChainBuilder` (React Flow canvas)
- `PropertiesPanel` (dynamic node/chain config)
- `ExecutionConsole` (real-time status, logs)
- `Node` components (LLMNode, NotebookNode, etc.)

## 3. Data Flow

- MCPs and Chains loaded from backend via REST API (axios)
- State (nodes, edges, selection, undo/redo, etc.) managed globally (Zustand/Redux)
- All configuration, validation, and execution handled in React app, with backend calls for persistence and execution

## 4. API Endpoints

- `GET /api/mcps` - List all MCPs
- `GET /api/chains` - List all chains
- `GET /api/chains/:id` - Get chain details
- `POST /api/chains` - Create chain
- `PUT /api/chains/:id` - Update chain
- `POST /api/chains/:id/execute` - Execute chain
- `GET /api/chains/:id/status` - Get execution status

## 5. State Management

- Use Zustand (or Redux) for global state:
  - `nodes`, `edges`, `selection`, `undoStack`, `redoStack`, `viewport`, `chainConfig`, `executionState`, `logs`

## 6. Accessibility & Responsiveness

- Keyboard navigation, ARIA labels, screen reader support
- Responsive layout using MUI's Grid/Box and CSS breakpoints

## 7. Example Code Snippets

**API Client Example:**
```typescript
import axios from 'axios';
export async function fetchMCPs() {
  const res = await axios.get('/api/mcps');
  return res.data;
}
```

**Component Hierarchy:**
```
<App>
  <Sidebar />
  <Main>
    <Toolbar />
    <ChainBuilder>
      <ReactFlow>
        <MCPNode />
        <Edge />
      </ReactFlow>
    </ChainBuilder>
    <PropertiesPanel />
    <ExecutionConsole />
  </Main>
</App>
```

**State Example (Zustand):**
```typescript
import create from 'zustand';
export const useChainStore = create(set => ({
  nodes: [],
  edges: [],
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  // ...other state and actions
}));
```

**Accessibility Example:**
```jsx
<button aria-label="Add MCP" tabIndex={0} onKeyDown={handleKeyDown}>
  +
</button>
```

---

This document should be updated as the UI evolves. 