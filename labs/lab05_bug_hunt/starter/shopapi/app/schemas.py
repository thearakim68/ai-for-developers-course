"""Request and response shapes (pydantic). Money is sent as a string like "49.90"."""
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, PlainSerializer

# Decimal in Python, "12.30" in JSON: strings keep cents exact for clients too.
MoneyOut = Annotated[Decimal, PlainSerializer(lambda value: f"{value:.2f}", return_type=str)]


class LoginIn(BaseModel):
    email: str = Field(max_length=200)
    password: str = Field(max_length=200)


class TokenOut(BaseModel):
    token: str
    user_id: int
    name: str


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: MoneyOut
    stock: int


class ProductPage(BaseModel):
    items: list[ProductOut]
    page: int
    page_size: int
    total: int


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, le=100)


class OrderIn(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1, max_length=20)
    coupon_code: str | None = Field(default=None, max_length=40)


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: MoneyOut
    line_total: MoneyOut


class OrderOut(BaseModel):
    id: int
    status: str
    created_at: datetime
    coupon_code: str | None
    items: list[OrderItemOut]
    subtotal: MoneyOut
    discount: MoneyOut
    tax: MoneyOut
    total: MoneyOut


class PricePreviewOut(BaseModel):
    coupon_code: str
    percent_off: int
    subtotal: MoneyOut
    discount: MoneyOut
    tax: MoneyOut
    total: MoneyOut


class ReviewIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)


class ReviewOut(BaseModel):
    id: int
    product_id: int
    author: str
    rating: int
    comment: str
    created_at: datetime


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)


class CouponIn(BaseModel):
    code: str = Field(min_length=3, max_length=40)
    percent_off: int = Field(ge=1, le=90)
    expires_at: AwareDatetime  # must include a time zone, e.g. "2026-12-31T23:59:00+09:00"


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    percent_off: int
    expires_at: datetime
    is_active: bool


class SalesRow(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: MoneyOut


class SalesReport(BaseModel):
    orders_counted: int
    revenue: MoneyOut
    by_product: list[SalesRow]
