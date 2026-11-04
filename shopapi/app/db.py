"""Database setup: engine, sessions and two column types for money and time."""
from collections.abc import Iterator
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from fastapi import Request
from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator

DEFAULT_DATABASE_URL = "sqlite:///./shopapi.db"
CENT = Decimal("0.01")


class Base(DeclarativeBase):
    pass


class Money(TypeDecorator):
    """Stores Decimal amounts as text like "49.90".

    SQLite has no exact decimal type: a Numeric column would quietly become a
    float. Text keeps every cent exact.
    """

    impl = String(20)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP))

    def process_result_value(self, value, dialect):
        return None if value is None else Decimal(value)


class UTCDateTime(TypeDecorator):
    """Stores aware datetimes as UTC and gives them back as aware UTC.

    SQLite forgets time zones, so we convert to UTC before saving and
    re-attach UTC when loading.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("ShopAPI only stores timezone-aware datetimes")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect):
        return None if value is None else value.replace(tzinfo=timezone.utc)


def make_engine(database_url: str = DEFAULT_DATABASE_URL) -> Engine:
    if database_url == "sqlite://":
        # In-memory database (tests): one shared connection, or each
        # session would see its own empty database.
        return create_engine(
            database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
    return create_engine(database_url, connect_args={"check_same_thread": False})


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_db(request: Request) -> Iterator[Session]:
    """FastAPI dependency: one session per request, always closed afterwards.

    Closing rolls back anything that was not committed, so an endpoint that
    forgets `db.commit()` loses its changes.
    """
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()
