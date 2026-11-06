# ShopAPI: the course project

A tiny shop API where every customer sees only their own orders. We grow it chapter by chapter with an AI coding agent, and check the AI's work with tests.

```
cd shop
uv sync
uv run pytest -q          # 4 passed
uv run uvicorn app.main:app
curl.exe -H "X-User-Id: 1" http://127.0.0.1:8000/orders/10
```

The `X-User-Id` header is a demo stand-in for "who is calling". It is **not** real login: replace it with real authentication before any public deploy.
