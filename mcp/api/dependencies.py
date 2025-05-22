"""Common FastAPI dependencies, e.g., for security."""

from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
import uuid # For random key generation
from typing import Optional
from fastapi import status
from .auth_utils import verify_access_token

# Load .env file to ensure MCP_API_KEY is available if set there
# This should ideally be loaded once at the app startup, but also safe here for the dependency.
load_dotenv()

API_KEY_NAME = "X-API-Key"
# ACTUAL_MCP_API_KEY_FROM_ENV = os.getenv("MCP_API_KEY") # DEBUG LINE - REMOVE
# print(f"DEBUG: Read MCP_API_KEY from env: '{ACTUAL_MCP_API_KEY_FROM_ENV}' (Type: {type(ACTUAL_MCP_API_KEY_FROM_ENV)})") # DEBUG LINE - REMOVE
# API_KEY = ACTUAL_MCP_API_KEY_FROM_ENV if ACTUAL_MCP_API_KEY_FROM_ENV is not None else None # DEBUG LINE - REMOVE

API_KEY = os.getenv("MCP_API_KEY") # Direct assignment

if API_KEY is None:
    print("WARNING: MCP_API_KEY not set in environment (os.getenv returned None). Generating a random, non-persistent API key for this session.")
    API_KEY = str(uuid.uuid4())
    print(f"Generated random API_KEY: {API_KEY}")
else:
    print(f"MCP_API_KEY loaded successfully from environment. Length: {len(API_KEY)}")

api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header_value: str = Security(api_key_header_scheme)) -> str:
    """
    FastAPI dependency to validate the API key provided in the X-API-Key header.
    Compares it against the server's configured API_KEY.
    """
    # print(f"DEBUG_ROUTE: Inside get_api_key. Server API_KEY is: '{API_KEY}'. Received header: '{api_key_header_value}'") # DEBUG LINE IN ROUTE - REMOVE
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