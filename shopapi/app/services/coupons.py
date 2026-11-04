"""Finding a coupon that may be used right now."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Coupon


class CouponError(Exception):
    """The coupon can't be used. The message is safe to show to the customer."""


def normalize_code(code: str) -> str:
    return code.strip().upper()


def find_usable_coupon(db: Session, code: str, now: datetime) -> Coupon:
    """Returns the coupon, or raises CouponError if it is unknown, inactive or expired.

    A coupon is usable while now < expires_at (both aware UTC datetimes).
    """
    coupon = db.scalar(select(Coupon).where(Coupon.code == normalize_code(code)))
    if coupon is None or not coupon.is_active:
        raise CouponError("Unknown coupon")
    if now >= coupon.expires_at:
        raise CouponError("This coupon has expired")
    return coupon
