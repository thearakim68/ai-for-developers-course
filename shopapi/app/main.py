"""Builds the ShopAPI app.

Run it with:  uvicorn app.main:create_app --factory --port 8000
(or use run.ps1 / run.sh, which also load the demo data first).
"""
import os

from fastapi import FastAPI

from app.db import DEFAULT_DATABASE_URL, Base, make_engine, make_session_factory
from app.routers import admin, auth, coupons, orders, products, reviews


def create_app(database_url: str | None = None) -> FastAPI:
    """Creates a fresh app with its own database connection.

    Tests call create_app("sqlite://") to get a private in-memory database.
    """
    url = database_url or os.environ.get("SHOPAPI_DATABASE_URL", DEFAULT_DATABASE_URL)
    engine = make_engine(url)
    Base.metadata.create_all(engine)

    app = FastAPI(title="ShopAPI", version="1.0.0", description="Course lab shop. Demo-grade auth.")
    app.state.engine = engine
    app.state.session_factory = make_session_factory(engine)

    for module in (auth, products, orders, coupons, reviews, admin):
        app.include_router(module.router)

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app
