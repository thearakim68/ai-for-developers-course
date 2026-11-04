# AGENTS.md: ShopAPI

Starter rules for AI coding agents. Lab 3 improves this file and measures the difference.

## Project
FastAPI + SQLAlchemy 2.0 + SQLite shop API, Python 3.12. Map: see README.md "Code map".

## Commands
- Tests: `python -m pytest` (run inside `shopapi/`; must stay green and under 10 s)
- Run: `./run.sh` or `./run.ps1` (resets demo data, port 8000)

## Rules
- Money is `Decimal`, rounded with `services/pricing.to_money`. Never use float.
- Get the time from `app.clock.get_now`. Never call `datetime.now()` directly. Datetimes are timezone-aware UTC.
- Customers only see their own orders. Someone else's order answers 404.
- Every behaviour change comes with a test. Don't edit or delete existing tests to make them pass.
- Keep diffs small; one ticket per change. Don't add dependencies without asking.
- Don't touch `app/legacy/` unless the task says so.
- Never commit secrets or real personal data. Demo tokens live only in `seed.py`.
