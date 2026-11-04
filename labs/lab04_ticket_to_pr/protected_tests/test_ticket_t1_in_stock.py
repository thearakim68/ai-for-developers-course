"""PROTECTED (Lab 4, ticket T1). Do not edit. check_protected.py verifies this file."""
from tests.conftest import ADMIN


def add_sold_out_product(client):
    r = client.post("/admin/products", headers=ADMIN, json={"name": "Sold Out Mug", "price": "8.00", "stock": 0})
    return r.json()["id"]


def test_in_stock_true_hides_sold_out_products(client):
    sold_out = add_sold_out_product(client)
    body = client.get("/products", params={"in_stock": "true", "page_size": 50}).json()
    assert sold_out not in [p["id"] for p in body["items"]]
    assert all(p["stock"] > 0 for p in body["items"])
    assert body["total"] == 9


def test_without_filter_sold_out_products_are_listed(client):
    sold_out = add_sold_out_product(client)
    body = client.get("/products", params={"page_size": 50}).json()
    assert sold_out in [p["id"] for p in body["items"]]


def test_in_stock_works_with_search(client):
    add_sold_out_product(client)
    body = client.get("/products", params={"in_stock": "true", "q": "mug"}).json()
    assert body["items"] == [] and body["total"] == 0
