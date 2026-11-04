"""Orders: place an order, list my orders, read one, cancel one.

Ownership rule: a customer only ever sees their own orders. Someone else's
order answers 404 (not 403), so we don't even reveal that it exists.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import current_user
from app.clock import get_now
from app.db import get_db
from app.models import CANCELLABLE_STATUSES, CANCELLED, PENDING, Order, OrderItem, Product, User
from app.schemas import OrderIn, OrderItemOut, OrderOut
from app.services.coupons import CouponError, find_usable_coupon
from app.services.pricing import PriceLine, discount_for, line_total, price_order

router = APIRouter(prefix="/orders", tags=["orders"])


def order_to_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        status=order.status,
        created_at=order.created_at,
        coupon_code=order.coupon_code,
        items=[
            OrderItemOut(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=line_total(item.unit_price, item.quantity),
            )
            for item in order.items
        ],
        subtotal=order.subtotal,
        discount=order.discount,
        tax=order.tax,
        total=order.total,
    )


def get_own_order(db: Session, order_id: int, user: User) -> Order:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    body: OrderIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
):
    percent_off = 0
    coupon_code = None
    if body.coupon_code:
        try:
            coupon = find_usable_coupon(db, body.coupon_code, now)
        except CouponError as error:
            raise HTTPException(status_code=400, detail=str(error))
        percent_off, coupon_code = coupon.percent_off, coupon.code

    order = Order(user_id=user.id, status=PENDING, created_at=now, coupon_code=coupon_code)
    lines = []
    for wanted in body.items:
        product = db.get(Product, wanted.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product {wanted.product_id} not found")
        if product.stock < wanted.quantity:
            raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")
        product.stock -= wanted.quantity
        order.items.append(
            OrderItem(product=product, quantity=wanted.quantity, unit_price=product.price)
        )
        unit_price = product.price - discount_for(product.price, percent_off)
        lines.append(PriceLine(unit_price=unit_price, quantity=wanted.quantity))

    prices = price_order(lines, percent_off)
    order.subtotal, order.discount = prices.subtotal, prices.discount
    order.tax, order.total = prices.tax, prices.total
    db.add(order)
    db.commit()
    return order_to_out(order)


@router.get("", response_model=list[OrderOut])
def list_my_orders(user: User = Depends(current_user), db: Session = Depends(get_db)):
    orders = db.scalars(
        select(Order)
        .where(Order.user_id == user.id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .order_by(Order.created_at.desc(), Order.id.desc())
    ).all()
    return [order_to_out(order) for order in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_to_out(order)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    order = get_own_order(db, order_id, user)
    if order.status == CANCELLED:
        raise HTTPException(status_code=409, detail=f"A {order.status} order can't be cancelled")
    for item in order.items:
        item.product.stock += item.quantity  # put the items back on the shelf
    order.status = CANCELLED
    db.commit()
    return order_to_out(order)
