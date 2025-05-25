import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel, TimestampMixin, UUIDMixin


class APIKey(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "api_keys"

    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    scopes: Mapped[str] = mapped_column(String(256), nullable=True, default="")
    expires_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<APIKey(user_id={self.user_id}, scopes={self.scopes}, revoked={self.revoked})>"
