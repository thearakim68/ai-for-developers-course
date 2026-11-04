"""Product reviews. Only customers who bought a product may review it, once."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import current_user
from app.clock import get_now
from app.db import get_db
from app.models import CANCELLED, Order, OrderItem, Product, Review, User
from app.schemas import ReviewIn, ReviewOut

router = APIRouter(prefix="/products/{product_id}/reviews", tags=["reviews"])


def review_to_out(review: Review) -> ReviewOut:
    return ReviewOut(
        id=review.id,
        product_id=review.product_id,
        author=review.user.name,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
    )


def has_bought(db: Session, user: User, product_id: int) -> bool:
    """True if the user has a non-cancelled order that contains this product."""
    bought = db.scalar(
        select(Order.id)
        .where(Order.user_id == user.id, Order.status != CANCELLED)
        .limit(1)
    )
    return bought is not None


@router.get("", response_model=list[ReviewOut])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    reviews = db.scalars(
        select(Review).where(Review.product_id == product_id).order_by(Review.id)
    ).all()
    return [review_to_out(review) for review in reviews]


@router.post("", response_model=ReviewOut, status_code=201)
def create_review(
    product_id: int,
    body: ReviewIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
):
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if not has_bought(db, user, product_id):
        raise HTTPException(status_code=403, detail="Only customers who bought this can review it")
    already = db.scalar(
        select(Review.id).where(Review.product_id == product_id, Review.user_id == user.id)
    )
    if already is not None:
        raise HTTPException(status_code=409, detail="You already reviewed this product")

    review = Review(
        product_id=product_id, user=user, rating=body.rating, comment=body.comment, created_at=now
    )
    db.add(review)
    db.flush()  # gives the review its id
    return review_to_out(review)
