from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    """Token model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model."""

    user_id: str
    exp: datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create an access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.security.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.security.secret_key, algorithm=settings.security.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.security.refresh_token_expire_days
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.security.secret_key, algorithm=settings.security.algorithm
    )
    return encoded_jwt


def create_tokens(user_id: str) -> Token:
    """Create both access and refresh tokens."""
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    return Token(access_token=access_token, refresh_token=refresh_token)


def verify_token(token: str) -> Optional[TokenData]:
    """Verify a token and return its data."""
    try:
        payload = jwt.decode(
            token,
            settings.security.secret_key,
            algorithms=[settings.security.algorithm],
        )
        user_id: str = payload.get("sub")
        exp: int = payload.get("exp")
        if user_id is None or exp is None:
            return None
        return TokenData(user_id=user_id, exp=datetime.fromtimestamp(exp))
    except JWTError:
        return None


def check_permission(user_id: str, chain_id: int, required_level: str) -> bool:
    """Check if a user has the required permission level for a chain."""
    from ..db.session import SessionLocal

    db = SessionLocal()
    try:
        # Define permission hierarchy
        permission_levels = {"read": 1, "write": 2, "admin": 3}

        permission = db.query(Permission).filter(
            Permission.user_id == user_id,
            Permission.chain_id == chain_id
        ).first()

        if not permission:
            return False

        required_level_value = permission_levels.get(required_level, 0)
        user_level_value = permission_levels.get(permission.access_level, 0)

        return user_level_value >= required_level_value
    finally:
        db.close()


def require_permission(required_level: str):
    """Decorator to require a specific permission level."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get user_id and chain_id from the request
            # This is a placeholder - implement based on your request handling
            user_id = kwargs.get("user_id")
            chain_id = kwargs.get("chain_id")

            if not user_id or not chain_id:
                raise ValueError("User ID and Chain ID are required")

            if not check_permission(user_id, chain_id, required_level):
                raise PermissionError(
                    f"User does not have {required_level} permission for this chain"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
