import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mcp.api.dependencies import get_current_roles, get_current_subject
from mcp.db.base_models import log_audit_action
from mcp.db.models.review import Review
from mcp.db.session import get_db_session
from mcp.schemas.review import ReviewCreate, ReviewRead

from .auth import UserRole

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewRead)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
    current_roles: List[str] = Depends(get_current_roles),
):
    if not any(
        role in current_roles for role in [UserRole.USER, UserRole.DEVELOPER, UserRole.ADMIN]
    ):
        raise HTTPException(status_code=403, detail="Insufficient role to create review.")
    db_review = Review(
        component_id=review.component_id,
        user_id=review.user_id,
        rating=review.rating,
        review_text=review.review_text,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    log_audit_action(
        db,
        user_id=current_user_sub,
        action_type="create_review",
        target_id=db_review.id,
        details=review.dict(),
    )
    return db_review


@router.get("/", response_model=List[ReviewRead])
def list_reviews(db: Session = Depends(get_db_session)):
    return db.query(Review).all()


@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db_session)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/component/{component_id}", response_model=List[ReviewRead])
def get_reviews_for_component(component_id: uuid.UUID, db: Session = Depends(get_db_session)):
    return db.query(Review).filter(Review.component_id == component_id).all()


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
    current_roles: List[str] = Depends(get_current_roles),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if UserRole.ADMIN not in current_roles and str(review.user_id) != str(current_user_sub):
        raise HTTPException(status_code=403, detail="Not permitted to delete this review.")
    db.delete(review)
    db.commit()
    log_audit_action(
        db,
        user_id=current_user_sub,
        action_type="delete_review",
        target_id=review_id,
        details={"review_id": str(review_id)},
    )
    return None
