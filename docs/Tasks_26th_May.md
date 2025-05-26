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
- [x] Test application startup and basic flows with new DB
    - [x] Start backend server
    - [x] Run basic user/API key/workflow creation flows
    - [x] Check for DB-related errors

### 2. Full Code Review and Cleanup
- [x] Review all backend and frontend code for duplication, dead code, and inconsistencies
    - [x] Identify duplicate code blocks
    - [x] List dead/unused code
    - [x] Note inconsistencies in logic or style
- [x] Refactor or remove duplicate/unused code
    - [x] Refactor duplicated logic into shared functions/modules
    - [x] Remove dead code
- [x] Ensure all new features are documented and tested
    - [x] Check for missing docstrings/comments
    - [x] Write or update tests for new features
- [x] Check for consistent naming, typing, and error handling
    - [x] Review variable/class/function names
    - [x] Ensure type hints are present where needed
    - [x] Standardize error handling patterns
- [x] Review and update documentation as needed
    - [x] Update README and docs for recent changes
    - [x] Add usage/setup instructions if missing

### 3. Final Check and Push
- [x] Run all tests (backend and frontend)
    - [x] Run backend test suite
    - [x] Run frontend test suite
    - [x] Check for failures and fix as needed
- [x] Lint and format codebase
    - [x] Run linter (e.g., flake8, eslint)
    - [x] Run formatter (e.g., black, prettier)
    - [x] Fix any reported issues
- [x] Commit and push all changes to the repository
    - [x] Stage all changes
    - [x] Write clear commit messages
    - [x] Push to remote repository
- [x] Tag or mark the release if appropriate
    - [x] Create a new tag or release in version control
    - [x] Update changelog if present

---

**Notes:**
- Prioritize unblocking all DB-dependent features and migrations.
- Ensure the codebase is clean, maintainable, and ready for further development or deployment.
- **Integration/system test issues remain:**
    - Some tests require PostgreSQL and will fail on SQLite (e.g., pg_stat_activity, pg_sleep).
    - Some tests require pygraphviz (for dependency visualizer).
    - Some tests require Prometheus metrics registry isolation.
- **Core codebase and test structure are now correct.** 