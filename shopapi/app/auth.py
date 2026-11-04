"""Login and "who is calling?" for ShopAPI.

DEMO-GRADE AUTH, for teaching only. Each user has one fixed API token,
sent as `Authorization: Bearer <token>`. A real shop would use expiring
tokens (OAuth2/OIDC or signed sessions), rate limits on login, and a
password hasher such as argon2.
"""
import hashlib
import hmac

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

PBKDF2_ITERATIONS = 100_000


def hash_password(password: str, salt: str) -> str:
    """Returns "salt$hexdigest". The salt is stored next to the hash."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt, _, _ = stored_hash.partition("$")
    return hmac.compare_digest(hash_password(password, salt), stored_hash)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == normalize_email(email)))


def current_user(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency: the logged-in user, or 401."""
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    user = db.scalar(select(User).where(User.api_token == token))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def admin_user(user: User = Depends(current_user)) -> User:
    """FastAPI dependency: the logged-in user, who must be an admin, or 403."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return user
