from tests.conftest import ADMIN, ANA


def test_list_reviews(client):
    reviews = client.get("/products/1/reviews").json()
    assert [(r["author"], r["rating"]) for r in reviews] == [("Ana", 5)]


def test_buyer_can_review(client):
    # Ana bought the USB-C cable in order #12.
    r = client.post("/products/3/reviews", headers=ANA, json={"rating": 4, "comment": "Solid."})
    assert r.status_code == 201
    assert r.json()["author"] == "Ana"
    assert r.json()["rating"] == 4


def test_someone_with_no_orders_cannot_review(client):
    r = client.post("/products/1/reviews", headers=ADMIN, json={"rating": 1})
    assert r.status_code == 403


def test_one_review_per_product(client):
    r = client.post("/products/1/reviews", headers=ANA, json={"rating": 3})
    assert r.status_code == 409


def test_rating_must_be_1_to_5(client):
    assert client.post("/products/3/reviews", headers=ANA, json={"rating": 6}).status_code == 422


def test_reviews_of_unknown_product_is_404(client):
    assert client.get("/products/999/reviews").status_code == 404
