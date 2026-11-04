from decimal import Decimal

from tests.conftest import ADMIN, ANA


def test_sales_report_ignores_cancelled_orders(client):
    report = client.get("/admin/reports/sales", headers=ADMIN).json()
    assert report["orders_counted"] == 3  # orders 10, 11, 12 (13 was cancelled)
    # order 10: 49.90 · order 11: 2 x 19.90 · order 12: 53.00 minus the 10% SAVE10 coupon
    assert Decimal(report["revenue"]) == Decimal("49.90") + Decimal("39.80") + Decimal("47.70")
    keyboard = report["by_product"][0]
    assert (keyboard["product_name"], keyboard["units_sold"]) == ("Keyboard", 1)


def test_admin_can_add_a_product(client):
    r = client.post(
        "/admin/products",
        headers=ADMIN,
        json={"name": "Mouse Pad", "price": "7.50", "stock": 50},
    )
    assert r.status_code == 201
    assert client.get(f"/products/{r.json()['id']}").json()["price"] == "7.50"


def test_admin_can_add_a_coupon(client):
    r = client.post(
        "/admin/coupons",
        headers=ADMIN,
        json={"code": "summer15", "percent_off": 15, "expires_at": "2026-08-31T23:59:00Z"},
    )
    assert r.status_code == 201
    assert r.json()["code"] == "SUMMER15"


def test_coupon_expiry_needs_a_time_zone(client):
    r = client.post(
        "/admin/coupons",
        headers=ADMIN,
        json={"code": "NOZONE", "percent_off": 15, "expires_at": "2026-08-31T23:59:00"},
    )
    assert r.status_code == 422


def test_duplicate_coupon_code_is_409(client):
    r = client.post(
        "/admin/coupons",
        headers=ADMIN,
        json={"code": "save10", "percent_off": 15, "expires_at": "2026-08-31T23:59:00Z"},
    )
    assert r.status_code == 409


def test_admin_ships_an_order(client):
    r = client.post("/admin/orders/10/ship", headers=ADMIN)
    assert r.status_code == 200
    assert client.get("/orders/10", headers=ANA).json()["status"] == "shipped"


def test_cannot_ship_a_cancelled_order(client):
    assert client.post("/admin/orders/13/ship", headers=ADMIN).status_code == 409


def test_orders_export_smoke(client):
    r = client.get("/admin/reports/orders-export", headers=ADMIN)
    assert r.status_code == 200
    lines = r.text.splitlines()
    assert lines[0] == "order_id,date,customer,items,status,total"
    assert lines[-1].startswith("TOTAL")
