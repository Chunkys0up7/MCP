# Tasks - 25th May

## High Priority Tasks

### 1. Implement DAG Workflow Execution ✅
- [x] Create DAG workflow engine
- [x] Implement DAG validation and cycle detection
- [x] Support parallel step execution
- [x] Add DAG visualization component
- [x] Update workflow monitor for DAGs
- [x] Add tests for DAG engine and visualizer

### 2. Enhance Component Marketplace (Next)
- [x] Implement faceted search for components (backend /api/components/search endpoint implemented and integrated with frontend)
- [x] Add component preview and metadata display
- [x] Integrate ratings and reviews (backend API endpoints, DB model, schemas, and frontend UI in Marketplace modal)
- [x] Support version compatibility and dependency resolution (backend search endpoint supports compatibility/dependency filters and returns version/dependency info)
- [x] Add advanced filtering and sorting (backend search endpoint supports sorting and advanced filters: author, cost, compliance, etc.)

### 3. Implement Advanced Security Features
- [x] Role-based access control (RBAC) (all routers audited and patched for RBAC enforcement; reviews creation/deletion now role-restricted)
- [x] Secrets management (all secrets/config loaded from env vars or .env; .env.example provided; Vault integration planned)
- [x] Audit logging (audit logs now written for MCP create/update actions; more endpoints to be covered)
- [ ] User management (User model created, pending migration and API implementation; PostgreSQL setup required)
- [x] API key management (APIKey model, endpoints for create/list/revoke, unified JWT/API key authentication dependency, docs updated)

### 4. Develop Execution Monitor Enhancements
- [x] Gantt chart visualization for workflow runs (backend API and frontend UI with mock data complete)
- [x] Resource usage monitoring (frontend UI with mock data complete; backend blocked by DB migration)
- [x] Time-travel debugging for workflow steps (frontend UI with mock data complete; backend blocked)
- [x] Performance suggestions and bottleneck detection (frontend UI with mock data complete; backend blocked)
- [x] Real-time metrics dashboard (frontend UI with mock data complete; backend blocked)

### 5. Container Orchestration Setup
- [ ] Kubernetes deployment scripts
- [ ] Autoscaling and resource management
- [ ] Service mesh configuration
- [ ] Monitoring with ELK stack
- [ ] Deployment documentation

---

**Notes:**
- All DAG workflow execution features are now complete and tested.
- Component preview and metadata display modal is implemented in FacetedSearchScreen.
- Next up: Integrate ratings and reviews (Task 2.3).
- Continue to maintain test coverage, update documentation, and ensure backward compatibility.
- See [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) for a full project summary.
- Endpoints now support authentication via either Bearer JWT or X-API-KEY header (API key).

## Dependencies
- PostgreSQL 12+
- Redis 6+
- Kubernetes cluster
- ELK Stack
- HashiCorp Vault 

## Tasks for 26th May
- [ ] Database migration: Switch dev environment to PostgreSQL, run all migrations, and verify schema. (Unblock user management and future migrations)
- [ ] API key management 