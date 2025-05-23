from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import HTTPException
from jose import JWTError, jwt

# --- JWT Configuration ---
# TODO: Move these to environment variables or a secure settings management system
JWT_SECRET_KEY = "a_very_secure_random_secret_key_for_mcp_project"  # CHANGE THIS IN PRODUCTION!
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException) -> Dict[str, Any]:
    """
    Decodes and verifies the JWT token.
    Returns the token payload (claims) if valid.
    Raises credentials_exception if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        # Log the specific JWTError for debugging if needed
        # print(f"JWTError during token decoding: {e}")
        raise credentials_exception 