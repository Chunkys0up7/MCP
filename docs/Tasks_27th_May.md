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
- [x] Standardize and enhance loading, empty, and error states across all major screens (Workflow Builder, Dashboard, Marketplace, Execution Monitor)
  - All major screens now use MUI CircularProgress, Alert, and consistent empty state messaging.
  - Next: Add quick access toolbar and system health widget to dashboard.
- [x] Ensure all cards, tables, and detail views use shared components and theme
- [x] Add quick access toolbar and system health widget to dashboard
  - Toolbar and widget are now present, accessible, and styled with the shared design system.
  - Next: Proceed to Execution Monitor improvements (real-time UI, WebSocket, feedback states).

### 4. **Execution Monitor Improvements**
- [x] Polish table, filters, and run detail views with new design system
- [ ] Add real-time Gantt/progress, logs, metrics, resource adjuster, and time travel debugger UI
- [ ] Ensure WebSocket integration for live updates
- [ ] Add error/empty/loading states

### 5. **General UI/UX Enhancements**
- [x] Global feedback: Toast notifications system is scaffolded using notistack and NotificationContext. Next: standardize usage and add inline errors/tooltips where missing.
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

**Check-in (29 May):**
- Global notification/toast system is available via notistack and NotificationContext. Will standardize usage and add inline feedback next.

- [~] Global feedback: Toast notifications are scaffolded and used in several places, but usage is not yet fully standardized across all screens and actions. Tooltips are present on most actionable icons/buttons in panels and toolbars, but should be reviewed for completeness and consistency. Inline errors and alerts are present in most major screens and panels, but some custom panels (e.g., ExecutionMonitor, NodeConfigPanel) use custom error boxes instead of standardized Alert components. Responsiveness: Some layouts use useMediaQuery and breakpoints, but not all screens are fully responsive yet.

**Check-in (29 May):**
- Reviewed global feedback mechanisms: toasts, tooltips, and inline errors/alerts. Toasts and tooltips are present but need standardization. Inline errors are mostly present but not always using the shared Alert component. Responsiveness is partial; some screens use breakpoints, others need improvement.
- Next: Standardize toast usage for all major actions, ensure all actionable icons/buttons have tooltips, refactor all inline error/warning/info states to use the shared Alert component, and audit/improve responsiveness for all major screens and panels.

- [~] Workflow Builder: Save, Validate, and Run actions now use standardized toast notifications (success/info/error) via NotificationContext.

**Check-in (29 May):**
- Workflow Builder now provides user feedback for Save, Validate, and Run actions using toasts. Next: cover node/edge add/delete/update and error cases, then move to other screens.

- [x] Workflow Builder: Canvas feedback (toasts for node/edge add, delete, update, undo/redo) is complete.

**Workflow Builder Feedback Milestone Check-in (29 May):**
- All major user actions in Workflow Builder Canvas now provide clear toast feedback. Next: review PropertiesPanel and other panels, then move to Dashboard, Marketplace, and Execution Monitor for feedback standardization.

- [x] Ensure all cards, tables, and detail views use shared components and theme
  - Marketplace: All cards and detail views now use shared Card component and MUI theme.
  - Next: Audit and refactor Dashboard cards/tables for consistency.

**Check-in (29 May):**
- Marketplace refactor complete: all cards and detail views use shared Card and theme. Proceeding to Dashboard audit/refactor next.

- [x] Dashboard: All cards now use shared Card component and MUI theme.
  - Next: Audit for any remaining custom tables or detail views, then proceed to next UI/UX tasks.

**Check-in (29 May):**
- Dashboard refactor complete: all cards use shared Card and theme. Proceeding to table/detail view audit and next UI/UX tasks.

**Check-in (29 May):**
- Loading, empty, and error states are now standardized across Dashboard, Marketplace, and Execution Monitor. Proceeding to dashboard toolbar and system health widget next.

**Check-in (29 May):**
- Dashboard now includes a quick access toolbar and a system health widget. Proceeding to Execution Monitor improvements next.

---

**Notes:**
- Reference `docs/UI Next Steps` for detailed wireframes, data structures, and interaction guidelines.
- Check in code and update documentation after each major step for visibility and collaboration.
- Prioritize Workflow Builder and design system for immediate visible improvement.
- All code should be accessible, responsive, and visually consistent.
- Recent: All major screens now use MUI for layout, cards, and feedback states. Current focus: standardize and enhance loading, empty, and error states across all major screens. Regular check-ins and documentation updates ongoing. 