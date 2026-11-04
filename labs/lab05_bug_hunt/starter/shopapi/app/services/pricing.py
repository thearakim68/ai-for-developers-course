"""Order maths: subtotal, coupon discount, tax and total.

Rules (intended behaviour):
- All money is Decimal, rounded to the cent with ROUND_HALF_UP (0.005 -> 0.01).
- The discount is a percentage of the subtotal, applied once.
- Tax (10%) is charged on the amount after the discount.
- total = subtotal - discount + tax
"""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
TAX_RATE = Decimal("0.10")


def to_money(amount: Decimal | int | str) -> Decimal:
    """Round to whole cents. Never pass a float: floats can't store 0.10 exactly."""
    if isinstance(amount, float):
        raise TypeError("Use Decimal for money, not float")
    return Decimal(amount).quantize(CENT, rounding=ROUND_HALF_UP)


def line_total(unit_price: Decimal, quantity: int) -> Decimal:
    return to_money(unit_price * quantity)


def discount_for(subtotal: Decimal, percent_off: int) -> Decimal:
    return to_money(subtotal * percent_off / 100)


def tax_for(amount: Decimal) -> Decimal:
    return Decimal(str(round(float(amount) * float(TAX_RATE), 2)))


@dataclass(frozen=True)
class PriceLine:
    unit_price: Decimal
    quantity: int


@dataclass(frozen=True)
class PriceBreakdown:
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal


def price_order(lines: list[PriceLine], percent_off: int = 0) -> PriceBreakdown:
    subtotal = sum((line_total(line.unit_price, line.quantity) for line in lines), Decimal("0.00"))
    discount = discount_for(subtotal, percent_off)
    tax = tax_for(subtotal - discount)
    total = subtotal - discount + tax
    return PriceBreakdown(subtotal=subtotal, discount=discount, tax=tax, total=total)
