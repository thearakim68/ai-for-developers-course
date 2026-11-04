"""Unit tests for the order maths (no web server, no database)."""
from decimal import Decimal

import pytest

from app.services.pricing import PriceLine, discount_for, line_total, price_order, tax_for, to_money


def test_to_money_rounds_half_up_to_cents():
    assert to_money("2.675") == Decimal("2.68")
    assert to_money("2.665") == Decimal("2.67")
    assert to_money(3) == Decimal("3.00")


def test_to_money_refuses_floats():
    with pytest.raises(TypeError):
        to_money(0.1)


def test_line_total():
    assert line_total(Decimal("49.90"), 3) == Decimal("149.70")


def test_discount_is_a_percentage_of_the_subtotal():
    assert discount_for(Decimal("49.90"), 10) == Decimal("4.99")
    assert discount_for(Decimal("49.90"), 0) == Decimal("0.00")


def test_tax_is_ten_percent():
    assert tax_for(Decimal("100.00")) == Decimal("10.00")
    assert tax_for(Decimal("0.00")) == Decimal("0.00")


def test_price_order_without_coupon():
    prices = price_order([PriceLine(Decimal("49.90"), 2)])
    assert prices.subtotal == Decimal("99.80")
    assert prices.discount == Decimal("0.00")
    assert prices.tax == Decimal("9.98")
    assert prices.total == Decimal("109.78")


def test_price_order_with_coupon_taxes_the_discounted_amount():
    prices = price_order([PriceLine(Decimal("60.00"), 1), PriceLine(Decimal("20.00"), 2)], 10)
    assert prices.subtotal == Decimal("100.00")
    assert prices.discount == Decimal("10.00")
    assert prices.tax == Decimal("9.00")
    assert prices.total == Decimal("99.00")
