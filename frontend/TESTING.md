# MCP Testing Strategy

## Overview
This document describes the testing approach for the MCP project, covering both the React frontend and FastAPI backend.

---

## Frontend (React)

### Tools
- **Vitest** (or Jest): Unit/integration tests
- **Testing Library**: Component testing
- **Cypress/Playwright**: E2E (if set up)

### Test Types
- **Unit Tests**: Components, Zustand store, API client, services
- **Integration Tests**: User flows (node creation, chain execution, error handling)
- **E2E Tests**: Full user journeys (optional)

### Example Test Files
- `src/__tests__/Toolbar.test.tsx`
- `src/__tests__/ChainCanvas.test.tsx`
- `src/__tests__/PropertiesPanel.test.tsx`
- `src/__tests__/ExecutionConsole.test.tsx`
- `src/__tests__/store.test.ts`
- `src/__tests__/apiClient.test.ts`
- `src/__tests__/chainService.test.ts`

### How to Run
- Lint: `npm run lint`
- Unit/Integration: `npm run test`
- E2E: `npx cypress open` (if set up)

---

## Backend (FastAPI)

### Tools
- **pytest**: Unit/integration tests
- **httpx**: API testing
- **pytest-asyncio**: Async tests

### Test Types
- **Unit Tests**: Endpoints, models, services, error handling
- **Integration Tests**: DB/Redis, chain execution, status polling
- **Contract Tests**: OpenAPI schema, response types

### Example Test Files
- `tests/test_api_chains.py`
- `tests/test_api_execution.py`
- `tests/test_models.py`
- `tests/test_services.py`

### How to Run
- `pytest`

---

## Coverage
- Aim for >90% coverage on core logic and API
- Use `pytest-cov` and `vitest --coverage` (or `jest --coverage`)

---

## Adding Tests
- Place frontend tests in `src/__tests__/`
- Place backend tests in `tests/`
- Use clear, descriptive test names and cover all edge cases

---

_Last updated: [auto-generated]_ 