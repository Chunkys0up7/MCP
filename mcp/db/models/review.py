from datetime import datetime
from uuid import uuid4

from sqlalchemy import (CheckConstraint, Column, DateTime, ForeignKey, Integer,
                        String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, TimestampMixin, UUIDMixin


class Review(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "reviews"

    component_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="valid_rating_range"),)

    # Relationships
    component = relationship("MCP", backref="reviews")

    def __repr__(self):
        return f"<Review(component_id={self.component_id}, user_id={self.user_id}, rating={self.rating})>"
