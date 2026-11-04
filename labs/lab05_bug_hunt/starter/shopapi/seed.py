"""Demo data for ShopAPI. Same data every time (deterministic).

    python seed.py          # wipes shopapi.db and loads the demo data

Users (demo passwords, never use real ones):
    1  Ana    ana@example.com    ana-password    token: ana-token
    2  Ben    ben@example.com    ben-password    token: ben-token
    3  Admin  admin@example.com  admin-password  token: admin-token (is_admin)

Order #10 is Ana's keyboard, just like the S0 demo.
"""
import os
from datetime import datetime, timezone
from decimal import Decimal
from functools import lru_cache

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.db import DEFAULT_DATABASE_URL, Base, make_engine, make_session_factory
from app.models import CANCELLED, PAID, SHIPPED, Coupon, Order, OrderItem, Product, Review, User
from app.services.pricing import PriceLine, price_order

UTC = timezone.utc


@lru_cache
def _demo_hash(password: str, salt: str) -> str:
    # Hashing is slow on purpose; cache it so the test suite seeds quickly.
    return hash_password(password, salt)


def _user(user_id: int, name: str, password: str, is_admin: bool = False) -> User:
    login = name.lower()
    return User(
        id=user_id,
        name=name,
        email=f"{login}@example.com",
        password_hash=_demo_hash(password, f"demo-salt-{login}"),
        api_token=f"{login}-token",
        is_admin=is_admin,
    )


def _order(order_id, user_id, status, created_at, items, coupon=None) -> Order:
    """items = [(product, quantity), ...]; totals are computed, never typed in."""
    percent_off = coupon.percent_off if coupon else 0
    prices = price_order([PriceLine(p.price, qty) for p, qty in items], percent_off)
    return Order(
        id=order_id,
        user_id=user_id,
        status=status,
        created_at=created_at,
        coupon_code=coupon.code if coupon else None,
        items=[OrderItem(product=p, quantity=qty, unit_price=p.price) for p, qty in items],
        subtotal=prices.subtotal,
        discount=prices.discount,
        tax=prices.tax,
        total=prices.total,
    )


def seed_database(db: Session) -> None:
    """Adds the demo data to an empty database. The caller commits."""
    ana = _user(1, "Ana", "ana-password")
    ben = _user(2, "Ben", "ben-password")
    admin = _user(3, "Admin", "admin-password", is_admin=True)

    def product(pid, name, price, stock, description):
        return Product(id=pid, name=name, price=Decimal(price), stock=stock, description=description)

    keyboard = product(1, "Keyboard", "49.90", 25, "Mechanical keyboard, US layout")
    mouse = product(2, "Mouse", "19.90", 40, "Wireless mouse, 2 buttons and a wheel")
    cable = product(3, "USB-C Cable", "9.50", 100, "1 m braided cable")
    monitor = product(4, "Monitor", "189.00", 8, "24 inch IPS monitor")
    stand = product(5, "Laptop Stand", "34.00", 15, "Aluminium, folds flat")
    webcam = product(6, "Webcam", "59.90", 12, "1080p webcam with privacy cover")
    headphones = product(7, "Headphones", "79.00", 10, "Over-ear, wired")
    lamp = product(8, "Desk Lamp", "25.00", 20, "Warm white LED")
    wrist_rest = product(9, "Wrist Rest", "15.00", 30, "Foam wrist rest for any keyboard")

    save10 = Coupon(id=1, code="SAVE10", percent_off=10, expires_at=datetime(2030, 12, 31, 23, 59, tzinfo=UTC))
    welcome5 = Coupon(id=2, code="WELCOME5", percent_off=5, expires_at=datetime(2024, 1, 31, 23, 59, tzinfo=UTC))
    retired = Coupon(id=3, code="OLD20", percent_off=20, expires_at=datetime(2030, 1, 1, tzinfo=UTC), is_active=False)

    orders = [
        _order(10, ana.id, PAID, datetime(2026, 5, 2, 10, 0, tzinfo=UTC), [(keyboard, 1)]),
        _order(11, ben.id, PAID, datetime(2026, 5, 3, 9, 30, tzinfo=UTC), [(mouse, 2)]),
        _order(12, ana.id, SHIPPED, datetime(2026, 5, 4, 14, 15, tzinfo=UTC), [(cable, 2), (stand, 1)], save10),
        _order(13, ben.id, CANCELLED, datetime(2026, 5, 5, 18, 45, tzinfo=UTC), [(webcam, 1)]),
    ]
    review = Review(
        id=1, product_id=keyboard.id, user=ana, rating=5,
        comment="Great keys, a bit loud.", created_at=datetime(2026, 5, 6, 8, 0, tzinfo=UTC),
    )

    db.add_all([ana, ben, admin, keyboard, mouse, cable, monitor, stand, webcam, headphones,
                lamp, wrist_rest, save10, welcome5, retired, *orders, review])


def reset_database(database_url: str) -> None:
    engine = make_engine(database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with make_session_factory(engine)() as db:
        seed_database(db)
        db.commit()
    engine.dispose()


if __name__ == "__main__":
    url = os.environ.get("SHOPAPI_DATABASE_URL", DEFAULT_DATABASE_URL)
    reset_database(url)
    print(f"Seeded demo data into {url}")
