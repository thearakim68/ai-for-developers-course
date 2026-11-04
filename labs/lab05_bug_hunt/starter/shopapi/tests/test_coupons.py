from decimal import Decimal

from tests.conftest import ANA

KEYBOARD = [{"product_id": 1, "quantity": 1}]


def preview(client, code, items=KEYBOARD):
    return client.post("/coupons/preview", headers=ANA, json={"code": code, "items": items})


def test_preview_shows_the_discounted_price(client):
    r = preview(client, "SAVE10")
    assert r.status_code == 200
    body = r.json()
    assert body["percent_off"] == 10
    assert Decimal(body["subtotal"]) == Decimal("49.90")
    assert Decimal(body["discount"]) == Decimal("4.99")
    assert Decimal(body["tax"]) == Decimal("4.49")
    assert Decimal(body["total"]) == Decimal("49.40")


def test_codes_are_not_case_sensitive(client):
    assert preview(client, " save10 ").json()["coupon_code"] == "SAVE10"


def test_expired_coupon_is_400(client):
    r = preview(client, "WELCOME5")
    assert r.status_code == 400
    assert "expired" in r.json()["detail"]


def test_inactive_coupon_is_400(client):
    assert preview(client, "OLD20").status_code == 400


def test_unknown_coupon_is_400(client):
    assert preview(client, "FREESTUFF").status_code == 400
