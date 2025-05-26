# Tasks - 27th May (Updated: UI Next Steps)

## High Priority: Usable, Modern UI Foundation

### 1. **Design System & Shared Components**
- [x] Implement theme file (colors, spacing, typography) based on `docs/UI Next Steps`
- [x] Create shared UI components: Button, Card, Input, Modal
- [x] Apply theme to Workflow Builder
- [x] Apply design system to Dashboard, Marketplace, Execution Monitor
- [ ] Add accessibility features: keyboard navigation, focus indicators, ARIA attributes, semantic HTML

### 2. **Workflow Builder Redesign (Main Focus)**
- [x] Scaffold new layout: Palette (left), Canvas (center), Toolbar (top), Properties Panel (right)
- [x] Implement Palette: search, collapsible categories
- [x] Implement Canvas: React Flow with sample workflow (nodes/edges)
- [x] Enable drag-and-drop from Palette to Canvas (add new nodes)
- [x] Node/edge selection and Properties Panel (view details)
- [x] Editable node/edge properties in Properties Panel
- [~] Implement Toolbar actions: Save, Validate, Run, Zoom, Undo/Redo (UI scaffolded, wiring up actions next)
- [x] Wire up toolbar actions to Canvas (zoom, undo/redo) and workflow logic (save, validate, run)
- [x] Implement Properties Panel logic: context-aware editing for node, edge, canvas
- [x] Add error/empty/validation states and onboarding/empty state content
- [ ] Ensure all elements are keyboard accessible

### 3. **Dashboard & Marketplace Polish**
- [x] Apply design system (colors, spacing, typography) to Dashboard (now uses MUI for all layout, cards, and feedback states)
- [x] Apply design system to Marketplace and Execution Monitor screens (all major screens now use MUI for layout, cards, and feedback states)
- [~] Standardize and enhance loading, empty, and error states across all major screens (Workflow Builder, Dashboard, Marketplace, Execution Monitor) [IN PROGRESS]
- [ ] Ensure all cards, tables, and detail views use shared components and theme
- [ ] Add quick access toolbar and system health widget to dashboard

### 4. **Execution Monitor Improvements**
- [x] Polish table, filters, and run detail views with new design system
- [ ] Add real-time Gantt/progress, logs, metrics, resource adjuster, and time travel debugger UI
- [ ] Ensure WebSocket integration for live updates
- [ ] Add error/empty/loading states

### 5. **General UI/UX Enhancements**
- [ ] Add global feedback: toast notifications, inline errors, tooltips
- [ ] Ensure responsiveness (breakpoints, mobile/desktop layouts)
- [ ] Add onboarding/empty state content to all major screens
- [ ] Review and improve accessibility across the app

## [x] Execution Monitor: Accessible Feedback States (29 May)
- Added ARIA roles to loading, error, and empty states for accessibility.
- Used MUI CircularProgress for loading, Alert for error, and consistent empty state messaging.
- All feedback states are now visually and semantically consistent with Dashboard and Marketplace.
- Code is future-proofed for async data loading and error handling.

**Check-in:**
- ExecutionMonitorScreen.tsx updated for accessibility and UI/UX consistency.
- All major screens now have standardized feedback states.

---

**Notes:**
- Reference `docs/UI Next Steps` for detailed wireframes, data structures, and interaction guidelines.
- Check in code and update documentation after each major step for visibility and collaboration.
- Prioritize Workflow Builder and design system for immediate visible improvement.
- All code should be accessible, responsive, and visually consistent.
- Recent: All major screens now use MUI for layout, cards, and feedback states. Current focus: standardize and enhance loading, empty, and error states across all major screens. Regular check-ins and documentation updates ongoing. 