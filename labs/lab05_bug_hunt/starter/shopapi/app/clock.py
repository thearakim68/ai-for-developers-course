"""The one place ShopAPI asks "what time is it?".

Endpoints get the time through the `get_now` dependency, so tests can freeze
the clock with `app.dependency_overrides[get_now] = lambda: FIXED_TIME`.
Always timezone-aware UTC: never call datetime.now() without a timezone.
"""
from datetime import datetime, timezone


def get_now() -> datetime:
    return datetime.now(timezone.utc)
