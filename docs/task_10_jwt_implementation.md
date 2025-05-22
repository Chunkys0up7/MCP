# Task 10: Implement JWT Authentication

**Status:** In Progress

**Goal:** Replace the current X-API-Key authentication with JWT-based authentication for enhanced security and standard compliance.

## Implementation Plan (Simplified Approach):

1.  **Install Dependencies:**
    *   Add `python-jose[cryptography]` to project dependencies (e.g., `requirements.txt` or `pyproject.toml`) and install it.

2.  **Configuration:**
    *   Define `JWT_SECRET_KEY` (a strong, randomly generated string).
    *   Define `JWT_ALGORITHM` (e.g., "HS256").
    *   Define `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (e.g., 30 or 60).
    *   These will be managed, ideally via environment variables, and accessed through a settings module (e.g., `mcp.core.config.py` if it exists, or directly in `mcp.api.dependencies.py` for now).

3.  **Token Utility Functions (e.g., in `mcp.api.auth_utils.py` or extend `mcp.api.dependencies.py`):
    *   `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`:
        *   Takes a dictionary `data` to encode into the JWT.
        *   Calculates token expiration.
        *   Encodes the JWT using `SECRET_KEY` and `ALGORITHM`.
    *   `verify_access_token(token: str, credentials_exception: HTTPException) -> dict`:
        *   Takes a JWT string.
        *   Decodes the token using `SECRET_KEY` and `ALGORITHMS`.
        *   Handles potential `JWTError` (e.g., expired signature, invalid token) by raising `credentials_exception`.
        *   Returns the decoded token payload (claims).

4.  **Developer Token Endpoint (e.g., in `mcp.api.routers.auth.py` or `mcp.api.main.py`):
    *   Create a new endpoint, for example, `POST /auth/issue-dev-token`.
    *   This endpoint will be protected by the *existing* `X-API-Key` (`Depends(get_api_key)`).
    *   Upon successful API key validation, it will generate a JWT using `create_access_token`. The JWT payload can contain a simple subject like `{"sub": "developer_access"}`.
    *   It will return the generated `access_token` and `token_type: "bearer"`.

5.  **New JWT Verification Dependency (e.g., in `mcp.api.dependencies.py`):
    *   Define an `OAuth2PasswordBearer` scheme: `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/issue-dev-token")` (pointing to our dev token endpoint).
    *   Create a new dependency, e.g., `async def get_current_active_user_subject(token: str = Security(oauth2_scheme)) -> str:`.
    *   This dependency will call `verify_access_token` with the provided token.
    *   It will extract and return the subject (or relevant user identifier) from the token payload.
    *   It will handle exceptions raised by `verify_access_token`.

6.  **Update Existing API Endpoints:**
    *   In `mcp.api.routers.workflows.py` and for the `/context` routes in `mcp.api.main.py`:
        *   Replace `Depends(get_api_key)` with `Depends(get_current_active_user_subject)` (or whatever the new JWT dependency is named).
        *   The return value of this dependency (e.g., the subject string) can be used if needed, or simply act as an authentication guard.

7.  **Update API Tests (`tests/api/test_workflows_api.py`, `tests/api/test_context_api.py`):
    *   Modify test fixtures or individual tests.
    *   First, make a call to `POST /auth/issue-dev-token` using the existing `X-API-Key` (`TEST_API_KEY` already defined in tests) to obtain a JWT.
    *   For all subsequent API calls to protected endpoints, include the obtained JWT in the `Authorization` header: `{"Authorization": f"Bearer {jwt_token}"}`.
    *   Add test cases for accessing protected endpoints with:
        *   No `Authorization` header.
        *   An invalid/expired JWT.
        *   A malformed `Authorization` header.

8.  **Environment Variable for `MCP_API_KEY` (Cleanup/Review):
    *   The `MCP_API_KEY` will now primarily be used to get the initial JWT via the dev token endpoint. Ensure its handling in `mcp.api.dependencies.py` (loading from `.env`, fallback to random) is still appropriate.

## Post-Implementation:

*   Verify all tests pass.
*   Manually test endpoints using a tool like Postman or Swagger UI with the new JWT flow.
*   Consider security implications (e.g., token lifetime, need for refresh tokens if sessions are long).
*   Update API documentation to reflect JWT authentication. 