
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel, TimestampMixin, UUIDMixin


class User(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    roles: Mapped[str] = mapped_column(
        String(128), nullable=False, default="user"
    )  # Comma-separated roles

    def __repr__(self):
        return (
            f"<User(username={self.username}, email={self.email}, roles={self.roles})>"
        )
