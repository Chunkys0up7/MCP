"""Common FastAPI dependencies, e.g., for security."""

import os
import uuid  # For random key generation
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session

from mcp.db.models.apikey import APIKey
from mcp.db.models.user import User

from .auth_utils import get_api_key, verify_access_token
from mcp.db.session import get_db_session
from .routers.auth import UserRole

# Load environment variables from .env file
load_dotenv()

# API Key header scheme
api_key_header_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False)

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/issue-dev-token", auto_error=False)

# Remove API_KEY loading from here since it's now in get_api_key


async def get_api_key(
    api_key_header_value: str = Security(api_key_header_scheme),
) -> str:
    """Validate API key from header."""
    API_KEY = os.getenv("MCP_API_KEY")  # Load API key dynamically
    if api_key_header_value != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
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
        raise CREDENTIALS_EXCEPTION_UNAUTHORIZED  # Or a more specific error
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


async def get_current_user_or_apikey(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    # Try JWT first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = verify_access_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid JWT: no subject")
            user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found for JWT")
            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid JWT: {str(e)}")
    # Try API key
    api_key = request.headers.get("X-API-KEY")
    if api_key:
        apikey_obj = (
            db.query(APIKey)
            .filter(APIKey.key == api_key, APIKey.revoked == False)
            .first()
        )
        if not apikey_obj:
            raise HTTPException(status_code=401, detail="Invalid or revoked API key")
        if apikey_obj.expires_at and apikey_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="API key expired")
        user = db.query(User).filter(User.id == apikey_obj.user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found for API key")
        return user
    raise HTTPException(
        status_code=401, detail="Not authenticated: provide Bearer JWT or X-API-KEY"
    )


def get_db():
    """Dependency that provides a SQLAlchemy session for FastAPI routes."""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()
