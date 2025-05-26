# Tasks - 27th May (Updated: UI Next Steps)

## High Priority: Usable, Modern UI Foundation

### 1. **Design System & Shared Components**
- [x] Implement theme file (colors, spacing, typography) based on `docs/UI Next Steps`
- [x] Create shared UI components: Button, Card, Input, Modal
- [x] Apply theme to Workflow Builder
- [x] Apply design system to Dashboard, Marketplace, Execution Monitor
- [x] Add accessibility features: keyboard navigation, focus indicators, ARIA attributes, semantic HTML (All major panels: Palette, Canvas, PropertiesPanel, Toolbar, ErrorPanel, ValidationPanel are accessible)

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

### Accessibility Improvements (29 May)
- Palette now supports keyboard navigation (arrow keys, tab, Enter), visible focus indicator, and ARIA roles/labels for all components.
- ListItems in Palette are focusable, navigable, and accessible for screen readers.

- [~] Canvas: Now focusable with tab, has ARIA role/label, visible focus indicator. Future: add custom keyboard navigation for node/edge selection.
- [~] PropertiesPanel: Now focusable with tab, has ARIA role/label, visible focus indicator, and screen reader instructions for navigation.

**Check-in (29 May):**
- PropertiesPanel is now focusable, with ARIA role/label, visible focus indicator, and screen reader instructions.
- Palette, Canvas, and PropertiesPanel are all accessible regions with keyboard/tab focus, ARIA, and clear navigation cues.
- Next: Review Toolbar, ErrorPanel, and ValidationPanel for accessibility improvements.

- [~] Toolbar: Now focusable, with ARIA role/label, visible focus indicator, all buttons labeled for screen readers, and screen reader instructions for navigation.
- [~] ErrorPanel: Now focusable, with ARIA role/label, visible focus indicator, aria-live error list, all buttons labeled for screen readers, and screen reader instructions for navigation.

**Check-in (29 May):**
- ErrorPanel is now accessible: focusable, ARIA role/label, visible focus indicator, aria-live error list, all buttons labeled, and screen reader instructions.
- Next: Review ValidationPanel for accessibility improvements.

- [~] ValidationPanel: Now focusable, with ARIA role/label, visible focus indicator, aria-live validation list, all buttons labeled for screen readers, and screen reader instructions for navigation.

**Check-in (29 May):**
- ValidationPanel is now accessible: focusable, ARIA role/label, visible focus indicator, aria-live validation list, all buttons labeled, and screen reader instructions.
- All major panels (Palette, Canvas, PropertiesPanel, Toolbar, ErrorPanel, ValidationPanel) are now accessible and keyboard navigable.

**Accessibility Milestone Check-in (29 May):**
- All major workflow panels are now accessible: focusable, keyboard navigable, ARIA roles/labels, visible focus indicators, aria-live regions, and screen reader instructions.
- The UI is now much more usable for keyboard and assistive technology users.
- Next: Focus on global feedback (toasts, tooltips, inline errors) and responsiveness.

---

**Notes:**
- Reference `docs/UI Next Steps` for detailed wireframes, data structures, and interaction guidelines.
- Check in code and update documentation after each major step for visibility and collaboration.
- Prioritize Workflow Builder and design system for immediate visible improvement.
- All code should be accessible, responsive, and visually consistent.
- Recent: All major screens now use MUI for layout, cards, and feedback states. Current focus: standardize and enhance loading, empty, and error states across all major screens. Regular check-ins and documentation updates ongoing. 