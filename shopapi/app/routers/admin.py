"""Admin-only endpoints: add products and coupons, ship orders, sales reports."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth import admin_user
from app.db import get_db
from app.legacy.report_export import export_orders
from app.models import CANCELLABLE_STATUSES, CANCELLED, SHIPPED, Coupon, Order, OrderItem, Product
from app.routers.orders import order_to_out
from app.schemas import CouponIn, CouponOut, OrderOut, ProductIn, ProductOut, SalesReport, SalesRow
from app.services.coupons import normalize_code

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(admin_user)])


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(body: ProductIn, db: Session = Depends(get_db)):
    product = Product(**body.model_dump())
    db.add(product)
    db.commit()
    return product


@router.post("/coupons", response_model=CouponOut, status_code=201)
def create_coupon(body: CouponIn, db: Session = Depends(get_db)):
    coupon = Coupon(
        code=normalize_code(body.code), percent_off=body.percent_off, expires_at=body.expires_at
    )
    db.add(coupon)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="A coupon with this code already exists")
    return coupon


@router.post("/orders/{order_id}/ship", response_model=OrderOut)
def ship_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in CANCELLABLE_STATUSES:  # only open orders can ship
        raise HTTPException(status_code=409, detail=f"A {order.status} order can't be shipped")
    order.status = SHIPPED
    db.commit()
    return order_to_out(order)


@router.get("/reports/sales", response_model=SalesReport)
def sales_report(db: Session = Depends(get_db)):
    """Units and revenue per product, from all orders that were not cancelled.

    Total revenue is what customers paid for the goods: subtotal minus
    discount (tax is not revenue). Per-product revenue is before coupon
    discounts, because a coupon applies to the whole order.
    Summed in Python with Decimal, not in SQL (SQLite would use floats).
    """
    orders = db.scalars(
        select(Order)
        .where(Order.status != CANCELLED)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    ).all()

    rows: dict[int, SalesRow] = {}
    for order in orders:
        for item in order.items:
            row = rows.setdefault(
                item.product_id,
                SalesRow(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    units_sold=0,
                    revenue=Decimal("0.00"),
                ),
            )
            row.units_sold += item.quantity
            row.revenue += item.unit_price * item.quantity

    return SalesReport(
        orders_counted=len(orders),
        revenue=sum((order.subtotal - order.discount for order in orders), Decimal("0.00")),
        by_product=sorted(rows.values(), key=lambda row: row.product_id),
    )


@router.get("/reports/orders-export", response_class=PlainTextResponse)
def orders_export(
    fmt: str = Query(default="csv", pattern="^(csv|tsv)$"),
    include_cancelled: bool = False,
    db: Session = Depends(get_db),
):
    """The finance team's order export (old code, see app/legacy/report_export.py)."""
    text = export_orders(db, fmt, include_cancelled)
    media_type = "text/csv" if fmt == "csv" else "text/tab-separated-values"
    return PlainTextResponse(text, media_type=media_type)
