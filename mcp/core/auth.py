"""
Authentication Module

This module provides authentication utilities.
It includes:

1. Role-based authentication
2. User roles
3. Permission checks
4. Error handling

The module supports:
- Role-based authentication
- User roles
- Permission checks
- Error handling
"""

from enum import Enum
from typing import List
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer

class UserRole(str, Enum):
    """User roles for role-based access control."""
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/issue-dev-token")

def require_any_role(required_roles: List[UserRole]):
    """
    Dependency factory to require any of the specified roles.
    Usage: Depends(require_any_role([UserRole.DEVELOPER, UserRole.ADMIN]))
    """
    async def roles_dependency(token: str = Security(oauth2_scheme)):
        # This is a placeholder. In a real implementation, you would validate the token and check roles.
        return required_roles
    return roles_dependency 