"""Common FastAPI dependencies, e.g., for security."""

from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
import uuid # For random key generation
from typing import Optional, List
from fastapi import status
from .auth_utils import verify_access_token, get_api_key
from .routers.auth import UserRole

# Load environment variables from .env file
load_dotenv()

# API Key header scheme
api_key_header_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False)

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/issue-dev-token", auto_error=False)

# Remove API_KEY loading from here since it's now in get_api_key

async def get_api_key(api_key_header_value: str = Security(api_key_header_scheme)) -> str:
    """Validate API key from header."""
    API_KEY = os.getenv("MCP_API_KEY")  # Load API key dynamically
    if api_key_header_value != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key_header_value


# --- JWT Authentication Dependency ---

# This points to the endpoint that issues the token. 
# Even if we use a simple /auth/issue-dev-token for now, this is standard practice.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/issue-dev-token")

CREDENTIALS_EXCEPTION_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_EXCEPTION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Operation not permitted for the authenticated user/subject",
)

async def get_current_subject(token: str = Security(oauth2_scheme)) -> str:
    """
    FastAPI dependency to validate JWT and extract the subject.
    This can be used to protect endpoints that require JWT authentication.
    """
    payload = verify_access_token(token, CREDENTIALS_EXCEPTION_UNAUTHORIZED)
    subject: Optional[str] = payload.get("sub")
    if subject is None:
        # This case should ideally not happen if token creation always includes 'sub'
        raise CREDENTIALS_EXCEPTION_UNAUTHORIZED # Or a more specific error
    return subject 

async def get_current_roles(token: str = Security(oauth2_scheme)) -> List[str]:
    """
    FastAPI dependency to validate JWT and extract the roles.
    This can be used to protect endpoints that require specific roles.
    """
    payload = verify_access_token(token, CREDENTIALS_EXCEPTION_UNAUTHORIZED)
    roles: List[str] = payload.get("roles", [])
    return roles

def require_role(required_role: UserRole):
    """
    Dependency factory to require a specific role.
    Usage: Depends(require_role(UserRole.ADMIN))
    """
    async def role_dependency(token: str = Security(oauth2_scheme)):
        roles = await get_current_roles(token)
        if required_role not in roles:
            raise CREDENTIALS_EXCEPTION_FORBIDDEN
        return roles
    return role_dependency

def require_any_role(required_roles: List[UserRole]):
    """
    Dependency factory to require any of the specified roles.
    Usage: Depends(require_any_role([UserRole.DEVELOPER, UserRole.ADMIN]))
    """
    async def roles_dependency(token: str = Security(oauth2_scheme)):
        roles = await get_current_roles(token)
        if not any(role in roles for role in required_roles):
            raise CREDENTIALS_EXCEPTION_FORBIDDEN
        return roles
    return roles_dependency 