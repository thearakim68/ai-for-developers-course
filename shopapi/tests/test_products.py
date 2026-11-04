def test_list_products_default_page(client):
    body = client.get("/products").json()
    assert body["total"] == 9
    assert len(body["items"]) == 9


def test_page_size_limits_the_number_of_items(client):
    body = client.get("/products", params={"page": 1, "page_size": 2}).json()
    assert len(body["items"]) == 2
    assert body["total"] == 9


def test_search_matches_name_and_description(client):
    body = client.get("/products", params={"q": "KEY"}).json()
    names = [p["name"] for p in body["items"]]
    assert names == ["Keyboard", "Wrist Rest"]  # Wrist Rest says "keyboard" in its description


def test_get_product(client):
    body = client.get("/products/1").json()
    assert body["name"] == "Keyboard"
    assert body["price"] == "49.90"


def test_unknown_product_is_404(client):
    assert client.get("/products/999").status_code == 404
