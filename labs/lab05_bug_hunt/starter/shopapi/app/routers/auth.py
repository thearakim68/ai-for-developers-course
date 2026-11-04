"""POST /auth/login: swap email + password for the user's API token."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import find_user_by_email, verify_password
from app.db import get_db
from app.schemas import LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = find_user_by_email(db, body.email)
    # Same message for "no such user" and "wrong password": don't reveal which emails exist.
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return TokenOut(token=user.api_token, user_id=user.id, name=user.name)
