# Tasks - 26th May

## High Priority Tasks

### 1. Database Migration and Schema Verification
- [x] Switch development environment to PostgreSQL
    - [x] Update database connection settings in environment/config files
    - [x] Install PostgreSQL locally or ensure access to a PostgreSQL instance
    - [x] Update dependencies (e.g., psycopg2 for Python)
- [x] Run all Alembic migrations from scratch
    - [x] Drop existing database (if needed)
    - [x] Initialize new PostgreSQL database
    - [x] Run `alembic upgrade head`
    - [x] Check for migration errors
- [x] Verify database schema matches models (User, APIKey, Workflow, etc.)
    - [x] Inspect tables and columns in PostgreSQL
    - [x] Compare with ORM models
    - [x] Resolve any discrepancies
    - [x] Added users table migration, aligned mcps.type enum, scaffolded ORM models for workflow/reviews
- [x] Update environment/config files as needed
    - [x] Ensure all DB-related settings are correct
    - [x] Update secrets or credentials if changed
    - [x] .env and docs updated for PostgreSQL and secret management
- [ ] Test application startup and basic flows with new DB
    - [ ] Start backend server
    - [ ] Run basic user/API key/workflow creation flows
    - [ ] Check for DB-related errors

### 2. Full Code Review and Cleanup
- [ ] Review all backend and frontend code for duplication, dead code, and inconsistencies
    - [ ] Identify duplicate code blocks
    - [ ] List dead/unused code
    - [ ] Note inconsistencies in logic or style
- [ ] Refactor or remove duplicate/unused code
    - [ ] Refactor duplicated logic into shared functions/modules
    - [ ] Remove dead code
- [ ] Ensure all new features are documented and tested
    - [ ] Check for missing docstrings/comments
    - [ ] Write or update tests for new features
- [ ] Check for consistent naming, typing, and error handling
    - [ ] Review variable/class/function names
    - [ ] Ensure type hints are present where needed
    - [ ] Standardize error handling patterns
- [ ] Review and update documentation as needed
    - [ ] Update README and docs for recent changes
    - [ ] Add usage/setup instructions if missing

### 3. Final Check and Push
- [ ] Run all tests (backend and frontend)
    - [ ] Run backend test suite
    - [ ] Run frontend test suite
    - [ ] Check for failures and fix as needed
- [ ] Lint and format codebase
    - [ ] Run linter (e.g., flake8, eslint)
    - [ ] Run formatter (e.g., black, prettier)
    - [ ] Fix any reported issues
- [ ] Commit and push all changes to the repository
    - [ ] Stage all changes
    - [ ] Write clear commit messages
    - [ ] Push to remote repository
- [ ] Tag or mark the release if appropriate
    - [ ] Create a new tag or release in version control
    - [ ] Update changelog if present

---

**Notes:**
- Prioritize unblocking all DB-dependent features and migrations.
- Ensure the codebase is clean, maintainable, and ready for further development or deployment. 