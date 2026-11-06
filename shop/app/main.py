"""ShopAPI starter: a tiny shop where every customer sees only their own orders.

Demo only: the caller says who they are with an X-User-Id header. That shows the
ownership logic, but it is NOT real login. Replace it with real auth before any public deploy.
"""
from fastapi import Depends, FastAPI, Header, HTTPException

USERS = {1: "Ana", 2: "Ben"}
ORDERS = {
    10: {"id": 10, "user_id": 1, "item": "keyboard"},
    11: {"id": 11, "user_id": 2, "item": "mouse"},
    12: {"id": 12, "user_id": 1, "item": "monitor"},
}

app = FastAPI(title="ShopAPI")


def current_user(x_user_id: int = Header()) -> int:
    """Who is calling? (demo: read from the X-User-Id header)."""
    if x_user_id not in USERS:
        raise HTTPException(status_code=401, detail="unknown user")
    return x_user_id


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def get_order(order_id: int, user_id: int = Depends(current_user)):
    order = ORDERS.get(order_id)
    if order is None or order["user_id"] != user_id:
        # Someone else's order looks exactly like a missing one: 404, no hint that it exists.
        raise HTTPException(status_code=404, detail="order not found")
    return {"id": order["id"], "item": order["item"]}
