from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from ..dependencies import get_api_key
from ..auth_utils import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class Token(BaseModel):
    access_token: str
    token_type: str

# Define roles enum
class UserRole(str):
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"

@router.post("/issue-dev-token", response_model=Token)
async def issue_dev_token(api_key: str = Depends(get_api_key)):
    """
    Issues a JWT for development/testing purposes.
    Protected by the existing X-API-Key.
    """
    # For development, issue a token with developer role
    access_token_data = {
        "sub": "developer_access_subject",
        "roles": [UserRole.DEVELOPER]  # Add roles claim
    }
    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"} 