"""PROTECTED (Lab 4, ticket T2). Do not edit. check_protected.py verifies this file."""
from tests.conftest import ANA, BEN


def test_filter_my_orders_by_status(client):
    orders = client.get("/orders", params={"status": "shipped"}, headers=ANA).json()
    assert [o["id"] for o in orders] == [12]


def test_filter_never_shows_other_customers_orders(client):
    orders = client.get("/orders", params={"status": "paid"}, headers=BEN).json()
    assert [o["id"] for o in orders] == [11]


def test_no_filter_returns_all_my_orders(client):
    assert [o["id"] for o in client.get("/orders", headers=ANA).json()] == [12, 10]


def test_unknown_status_is_422(client):
    assert client.get("/orders", params={"status": "lost"}, headers=ANA).status_code == 422
