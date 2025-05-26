import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class APIKeyBase(BaseModel):
    scopes: Optional[str] = Field(
        default="", description="Comma-separated scopes/roles for this key."
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="Expiration datetime for the key."
    )


class APIKeyCreate(APIKeyBase):
    user_id: Optional[uuid.UUID] = Field(
        default=None,
        description="User to associate with this key (admin only, else self).",
    )


class APIKeyRead(APIKeyBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    created_at: datetime
    revoked: bool
    key: Optional[str] = Field(
        default=None, description="API key string (only returned on creation)"
    )

    class Config:
        from_attributes = True


class APIKeyRevoke(BaseModel):
    id: uuid.UUID
    reason: Optional[str] = Field(default=None, description="Reason for revocation.")
