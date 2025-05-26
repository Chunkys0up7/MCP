# Tasks - 27th May

## High Priority Tasks (System & UI Integration)

### 1. Implement and Integrate the Component Marketplace UI
- **Scaffold Marketplace Page Structure** ✅
    - MarketplacePage, FilterPanel, ComponentCard, and ComponentDetailView created and integrated.
- **Implement Faceted Search Filters** ✅
    - Type, compliance, cost, and search input working; state managed.
- **Build Component Card/Grid/List** ✅
    - Cards display name, version, type, description, tags, and rating; click to open detail view.
- **Component Detail View with Tabs** ✅
    - Tabs for Overview, Dependencies, Sandbox, Versions, Reviews; detail view opens as side panel.
- **Dependency Visualizer** ✅
    - SVG-based graph visualizer in Dependencies tab, using robust mock data for nodes/edges.
    - Ready for future integration with React Flow or Vis.js.
- **API Integration** ✅
    - searchComponents and getComponentDetails wired up; mock API for now.
- **Action Buttons** (Next)
    - Implement "Add to Workflow" and "Test in Sandbox" buttons in the detail view.
    - Reference code patterns and UI/UX from docs/UI_overview (see conceptual code for action handling).
    - Ensure buttons trigger correct UI flows and (mock) API calls.
- **Testing and Polish** (Next)
    - Write unit and integration tests for Marketplace UI and API integration.
    - Ensure accessibility, responsiveness, and polish (loading spinners, empty/edge states, error messages).

- **Check docs/UI_overview for code examples and patterns as you implement each subtask.**
- **Check in and push code after each subtask.**

### 2. Enhance Workflow Builder: Properties Panel & AI Co-Pilot
- Expand the properties panel to support:
    - Advanced node configuration (input mapping, version selection, kernel, timeout, etc.)
    - Edge configuration (data transformation options)
    - Canvas-level metadata (workflow name, description, global vars)
- Scaffold the AI Co-Pilot UI:
    - Suggestion pop-ups for schema mismatches, optimal component choices, auto-connecting nodes
    - Optional chat interface for workflow help
- Ensure all changes update workflow state and persist via API (save, validate, run)
- Reference: UI_overview (Section 3), System Overview (Workflow Builder, Workflow Engine)

### 3. Execution Monitor: Real-Time Gantt Chart and Logs
- Implement the Execution Monitor page with:
    - Table of workflow runs (name, run ID, status, start time, duration, cost, initiator)
    - Filters for status, date range, workflow name
    - Run detail view with:
        - Summary tab (inputs, outputs, status)
        - Real-time Gantt chart/progress view (task timeline, status, dependencies)
        - Logs tab (aggregated, filterable logs)
        - Metrics tab (CPU, memory, custom metrics)
        - Resource allocation adjuster (if live)
        - Time travel debugger (step through states, replay execution)
    - Integrate WebSocket for live updates (metrics, logs)
- Reference: UI_overview (Section 4), System Overview (Execution Monitor, Execution Runtime)

### 4. System Health Monitor Widget (Dashboard)
- Add a mini system health monitor to the dashboard:
    - Show API Gateway, DB, Execution Runtime status (mini-charts or status indicators)
    - Fetch real-time metrics (WebSocket or polling)
    - Link to a detailed system status page for full metrics
- Integrate with backend monitoring endpoints
- Reference: UI_overview (Dashboard), System Overview (System Health Monitor, Monitoring)

### 5. RBAC & Auth Integration in UI
- Ensure all UI routes and actions are protected by authentication and RBAC checks
    - Implement login/logout flow, user profile, and permission-based UI rendering
    - Hide/disable UI elements based on user roles/permissions
- Integrate AuthContext (or similar) for global auth state
- Ensure API calls include JWT or API key as required
- Reference: UI_overview (Top Bar, AuthContext), System Overview (Security Subsystem, API Gateway)

---

**Notes:**
- Each task references both system and UI documentation for deeper context.
- Break down each task into subtasks as you implement.
- This list is designed to drive both visible UI progress and robust system integration for the next development cycle. 