import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt

from mcp.config.settings import settings  # <-- Import global settings

# --- JWT Configuration ---
# All secrets/config are now loaded from settings.security
# settings.security.secret_key, settings.security.algorithm, settings.security.access_token_expire_minutes

# API Key header scheme
api_key_header_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def get_api_key(
    api_key_header_value: str = Security(api_key_header_scheme),
) -> str:
    """Validate API key from header."""
    API_KEY = os.getenv("MCP_API_KEY") or settings.security.secret_key  # Fallback to settings if env not set
    if api_key_header_value != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key_header_value


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.security.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.security.secret_key, algorithm=settings.security.algorithm
    )
    return encoded_jwt


def verify_access_token(
    token: str, credentials_exception: HTTPException
) -> Dict[str, Any]:
    """
    Decodes and verifies the JWT token.
    Returns the token payload (claims) if valid.
    Raises credentials_exception if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        return payload
    except JWTError:
        # Log the specific JWTError for debugging if needed
        # print(f"JWTError during token decoding: {e}")
        raise credentials_exception
