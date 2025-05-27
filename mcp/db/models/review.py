from uuid import UUID as PyUUID
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base_models import Base


class Review(Base):  # type: ignore[misc, valid-type]
    __tablename__ = "reviews"
    id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False)
    user_id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
