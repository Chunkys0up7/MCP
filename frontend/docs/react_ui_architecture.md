# MCP React UI Architecture (Updated)

## Overview
This document describes the architecture and structure of the MCP Chain Builder React UI, including recent enhancements for enterprise usability, error handling, and a design system.

## Project Structure

- `src/`
  - `application/` — Business logic
  - `infrastructure/` — API clients, state management
  - `presentation/`
    - `features/` — Feature-based UI modules
      - `chain-builder/` — Main workspace, canvas, toolbar
      - `node-config/` — Node property panel
      - `execution-monitor/` — Execution console
    - `design-system/` — Shared UI components (e.g., Notification)
  - `services/` — Service layer for business logic

## Key Components

- **Toolbar**: Save, Load, Export, Undo, Redo actions for chain management.
- **ChainCanvas**: Visual node/edge editor using React Flow.
- **PropertiesPanel**: Node configuration with validation and notifications.
- **ExecutionConsole**: Real-time execution monitoring, error display.
- **Notification**: Snackbar-based feedback for user actions and errors.

## State Management
- Zustand store for nodes, edges, execution state, undo/redo.

## API Layer
- Axios-based client for FastAPI backend.

## Error Handling & Validation
- Form validation in PropertiesPanel.
- Error boundaries and notifications for user feedback.

## Design System
- Shared components (e.g., Notification) in `presentation/design-system/`.
- Consistent MUI theming and layout.

## Usage
- Use the Toolbar for chain actions.
- Configure nodes in the PropertiesPanel; errors and saves trigger notifications.
- Monitor execution in the ExecutionConsole.

## Extensibility
- Add new node types or UI features by extending the relevant feature or design-system directories.

## Testing

See [TESTING.md](../TESTING.md) for the full test plan and coverage.

- Unit tests for all components, state, and services
- Integration tests for user flows (node creation, execution, error handling)
- E2E tests for full user journeys (if Cypress/Playwright is set up)

Run tests with `npm run test` (frontend) or `pytest` (backend).

---

_Last updated: [auto-generated]_ 