import secrets
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mcp.api.dependencies import get_current_subject, get_db, require_admin
from mcp.db.models.apikey import APIKey
from mcp.db.models.user import User
from mcp.schemas import APIKeyCreate, APIKeyRead, APIKeyRevoke

router = APIRouter(prefix="/api/apikeys", tags=["API Keys"])


def get_user_from_subject(db: Session, subject: str) -> User:
    user = db.query(User).filter(User.id == subject).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found for JWT subject")
    return user


@router.post("/", response_model=APIKeyRead)
def create_apikey(
    apikey_in: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user_sub: str = Depends(get_current_subject),
):
    current_user = get_user_from_subject(db, current_user_sub)
    # Only admin can create for others
    if apikey_in.user_id and apikey_in.user_id != current_user.id:
        require_admin(current_user)
        user_id = apikey_in.user_id
    else:
        user_id = current_user.id
    key = secrets.token_urlsafe(32)
    apikey = APIKey(
        key=key,
        user_id=user_id,
        scopes=apikey_in.scopes or "",
        expires_at=apikey_in.expires_at,
        revoked=False,
    )
    db.add(apikey)
    db.commit()
    db.refresh(apikey)
    return APIKeyRead.from_orm(apikey).copy(update={"key": key})


@router.get("/", response_model=List[APIKeyRead])
def list_apikeys(
    db: Session = Depends(get_db), current_user_sub: str = Depends(get_current_subject)
):
    current_user = get_user_from_subject(db, current_user_sub)
    # Admin sees all, user sees own
    if "admin" in (current_user.roles or ""):
        apikeys = db.query(APIKey).all()
    else:
        apikeys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return [APIKeyRead.from_orm(a) for a in apikeys]


@router.post("/revoke", response_model=APIKeyRead)
def revoke_apikey(
    revoke_in: APIKeyRevoke,
    db: Session = Depends(get_db),
    current_user_sub: str = Depends(get_current_subject),
):
    current_user = get_user_from_subject(db, current_user_sub)
    apikey = db.query(APIKey).filter(APIKey.id == revoke_in.id).first()
    if not apikey:
        raise HTTPException(status_code=404, detail="API key not found")
    # Only admin or owner can revoke
    if apikey.user_id != current_user.id and "admin" not in (current_user.roles or ""):
        raise HTTPException(status_code=403, detail="Not authorized to revoke this key")
    apikey.revoked = True
    db.commit()
    db.refresh(apikey)
    return APIKeyRead.from_orm(apikey)
