from tests.conftest import ANA, BEN


def test_login_returns_the_users_token(client):
    r = client.post("/auth/login", json={"email": "ana@example.com", "password": "ana-password"})
    assert r.status_code == 200
    assert r.json() == {"token": "ana-token", "user_id": 1, "name": "Ana"}


def test_login_with_wrong_password_is_401(client):
    r = client.post("/auth/login", json={"email": "ana@example.com", "password": "nope"})
    assert r.status_code == 401


def test_login_with_unknown_email_is_401(client):
    r = client.post("/auth/login", json={"email": "zoe@example.com", "password": "ana-password"})
    assert r.status_code == 401


def test_missing_token_is_401(client):
    assert client.get("/orders").status_code == 401


def test_wrong_token_is_401(client):
    assert client.get("/orders", headers={"Authorization": "Bearer guessed"}).status_code == 401


def test_customers_cannot_use_admin_endpoints(client):
    assert client.get("/admin/reports/sales", headers=ANA).status_code == 403
    assert client.get("/admin/reports/sales", headers=BEN).status_code == 403
