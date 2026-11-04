from decimal import Decimal

from tests.conftest import ANA, BEN


def place(client, headers, items, coupon=None):
    return client.post("/orders", headers=headers, json={"items": items, "coupon_code": coupon})


def test_owner_can_read_order(client):
    r = client.get("/orders/10", headers=ANA)
    assert r.status_code == 200
    assert r.json()["items"][0]["product_name"] == "Keyboard"


def test_missing_order_is_404(client):
    assert client.get("/orders/999", headers=ANA).status_code == 404


def test_list_my_orders_newest_first(client):
    orders = client.get("/orders", headers=ANA).json()
    assert [o["id"] for o in orders] == [12, 10]


def test_create_order_computes_totals(client):
    r = place(client, ANA, [{"product_id": 1, "quantity": 2}])
    assert r.status_code == 201
    order = r.json()
    assert order["status"] == "pending"
    assert Decimal(order["subtotal"]) == Decimal("99.80")
    assert Decimal(order["discount"]) == Decimal("0.00")
    assert Decimal(order["tax"]) == Decimal("9.98")
    assert Decimal(order["total"]) == Decimal("109.78")


def test_create_order_takes_items_from_stock(client):
    place(client, BEN, [{"product_id": 4, "quantity": 3}])
    assert client.get("/products/4").json()["stock"] == 5


def test_new_order_shows_up_in_my_orders(client):
    new_id = place(client, BEN, [{"product_id": 3, "quantity": 1}]).json()["id"]
    assert new_id in [o["id"] for o in client.get("/orders", headers=BEN).json()]


def test_cannot_order_more_than_stock(client):
    assert place(client, ANA, [{"product_id": 4, "quantity": 9}]).status_code == 409


def test_unknown_product_in_order_is_404(client):
    assert place(client, ANA, [{"product_id": 999, "quantity": 1}]).status_code == 404


def test_empty_order_is_422(client):
    assert place(client, ANA, []).status_code == 422


def test_order_with_coupon(client):
    r = place(client, ANA, [{"product_id": 2, "quantity": 1}], coupon="SAVE10")
    assert r.status_code == 201
    assert r.json()["coupon_code"] == "SAVE10"
    assert Decimal(r.json()["discount"]) > 0


def test_order_with_expired_coupon_is_400(client):
    assert place(client, ANA, [{"product_id": 2, "quantity": 1}], coupon="WELCOME5").status_code == 400


def test_cancel_order_puts_stock_back(client):
    order_id = place(client, ANA, [{"product_id": 6, "quantity": 2}]).json()["id"]
    r = client.post(f"/orders/{order_id}/cancel", headers=ANA)
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"
    assert client.get("/products/6").json()["stock"] == 12


def test_cannot_cancel_twice(client):
    order_id = place(client, ANA, [{"product_id": 6, "quantity": 1}]).json()["id"]
    client.post(f"/orders/{order_id}/cancel", headers=ANA)
    assert client.post(f"/orders/{order_id}/cancel", headers=ANA).status_code == 409
