from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
ANA = {"X-User-Id": "1"}
BEN = {"X-User-Id": "2"}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_ana_gets_her_order():
    r = client.get("/orders/10", headers=ANA)
    assert r.status_code == 200
    assert r.json() == {"id": 10, "item": "keyboard"}


def test_ben_cannot_see_anas_order():
    assert client.get("/orders/10", headers=BEN).status_code == 404


def test_unknown_user_is_rejected():
    assert client.get("/orders/10", headers={"X-User-Id": "99"}).status_code == 401
