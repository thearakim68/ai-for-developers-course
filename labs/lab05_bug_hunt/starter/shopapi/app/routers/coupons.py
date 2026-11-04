"""Coupons: preview what an order would cost with a coupon, before ordering."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import current_user
from app.clock import get_now
from app.db import get_db
from app.models import Product, User
from app.schemas import OrderItemIn, PricePreviewOut
from app.services.coupons import CouponError, find_usable_coupon
from app.services.pricing import PriceLine, price_order

router = APIRouter(prefix="/coupons", tags=["coupons"])


class PreviewIn(BaseModel):
    code: str = Field(max_length=40)
    items: list[OrderItemIn] = Field(min_length=1, max_length=20)


@router.post("/preview", response_model=PricePreviewOut)
def preview_coupon(
    body: PreviewIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
):
    try:
        coupon = find_usable_coupon(db, body.code, now)
    except CouponError as error:
        raise HTTPException(status_code=400, detail=str(error))

    lines = []
    for wanted in body.items:
        product = db.get(Product, wanted.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product {wanted.product_id} not found")
        lines.append(PriceLine(unit_price=product.price, quantity=wanted.quantity))

    prices = price_order(lines, coupon.percent_off)
    return PricePreviewOut(
        coupon_code=coupon.code,
        percent_off=coupon.percent_off,
        subtotal=prices.subtotal,
        discount=prices.discount,
        tax=prices.tax,
        total=prices.total,
    )
