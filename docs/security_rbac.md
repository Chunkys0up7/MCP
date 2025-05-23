# Security: JWT and RBAC Design Notes

## 1. JWT Issuance and Validation

- **Issuance:**
    - `/auth/issue-dev-token`: Issues a JWT for development/testing purposes. Requires a valid `X-API-Key` header (configured via `MCP_API_KEY` environment variable). This token has a subject "dev_user" and no specific roles encoded by default (can be extended).
    - `/auth/token`: Standard OAuth2 password flow. Issues JWTs based on username/password credentials. The current implementation uses a hardcoded dummy user. In a production system, this would validate against a user database.
- **Validation:**
    - JWTs are validated by the `get_current_subject` dependency used in protected API endpoints.
    - This dependency decodes the token, checks its signature, and expiry.
    - It currently extracts the `sub` (subject) claim.

## 2. Role-Based Access Control (RBAC) - Initial Design

This section outlines initial thoughts on roles and permissions. Actual implementation of these RBAC checks is a future task and would involve:
- Adding a `roles` claim to the JWT.
- Modifying `get_current_subject` or creating new dependencies to extract and verify roles.
- Implementing permission checks within API endpoints or service layers.

### 2.1. Proposed User Roles

- **`user`**: Basic authenticated user. Can view public resources and execute permitted workflows.
- **`developer`**: Can create, manage, and share their own MCPs and workflows. Can view public resources.
- **`admin`**: Full control over the system, including managing all users, MCPs, and workflows.

### 2.2. Permissions for MCP Definitions (Marketplace - `/context/*`)

| Action        | Endpoint(s)                | `user`      | `developer`          | `admin`     | Notes                                               |
|---------------|----------------------------|-------------|----------------------|-------------|-----------------------------------------------------|
| List MCPs     | `GET /context`             | Allowed     | Allowed              | Allowed     | All can view available components.                  |
| View MCP      | `GET /context/{mcp_id}`    | Allowed     | Allowed              | Allowed     |                                                     |
| Create MCP    | `POST /context`            | Denied      | Allowed              | Allowed     | Only developers and admins can add new components.  |
| Update MCP    | `PUT /context/{mcp_id}`    | Denied      | Owner or Admin       | Allowed     | Developers can update their own; admins can update any. |
| Delete MCP    | `DELETE /context/{mcp_id}` | Denied      | Owner or Admin       | Allowed     | Developers can delete their own; admins can delete any. |
| Search MCPs   | `GET /context/search`      | Allowed     | Allowed              | Allowed     |                                                     |

*"Owner" implies the MCP definition would need an `owner_id` field linking to the user's subject ID.*

### 2.3. Permissions for Workflow Definitions (`/workflows/*`)

| Action           | Endpoint(s)                         | `user`      | `developer`          | `admin`     | Notes                                                  |
|------------------|-------------------------------------|-------------|----------------------|-------------|--------------------------------------------------------|
| List Workflows   | `GET /workflows`                    | Allowed     | Allowed              | Allowed     |                                                        |
| View Workflow    | `GET /workflows/{workflow_id}`      | Allowed     | Allowed              | Allowed     |                                                        |
| Create Workflow  | `POST /workflows`                   | Allowed     | Allowed              | Allowed     | All authenticated users might be able to create workflows. |
| Update Workflow  | `PUT /workflows/{workflow_id}`      | Denied      | Owner or Admin       | Allowed     |                                                        |
| Delete Workflow  | `DELETE /workflows/{workflow_id}`   | Denied      | Owner or Admin       | Allowed     |                                                        |
| Execute Workflow | `POST /workflows/{workflow_id}/execute` | Allowed (conditional) | Allowed (conditional) | Allowed     | Execution rights might depend on workflow sensitivity.   |

*"Owner" implies the workflow definition would need an `owner_id` field.*
*"Conditional" execution for users/developers might mean some workflows are public, others private or role-restricted.*

## 3. Future Enhancements

- Granular permissions (e.g., `mcp:create`, `workflow:execute`).
- Sharing mechanisms (user-to-user, user-to-group).
- Organization/tenant level isolation if needed. 