from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # Will be used by the dependency, not directly here for this endpoint
from typing import Dict
from pydantic import BaseModel # Added import

from ..dependencies import get_api_key # For protecting this dev token endpoint
from ..auth_utils import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/issue-dev-token", response_model=Token)
async def issue_dev_token(api_key: str = Depends(get_api_key)):
    """
    Issues a JWT for development/testing purposes.
    Protected by the existing X-API-Key.
    """
    # The subject can be anything meaningful for a dev token
    # For a real user system, this would be the user_id or username
    access_token_data = {"sub": "developer_access_subject"} 
    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"} 