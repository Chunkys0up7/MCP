import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    component_id: uuid.UUID = Field(
        ..., description="ID of the reviewed component (MCP)"
    )
    user_id: uuid.UUID = Field(..., description="ID of the user who wrote the review")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    review_text: Optional[str] = Field(None, description="Text of the review")


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
