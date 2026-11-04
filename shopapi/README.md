# ShopAPI

A small online shop API, and the project you work on in Part 2 of the course (S3–S7).
It is the grown-up version of the S0 orders demo. You'll see the same people (Ana and Ben) and the same order #10 (Ana's keyboard).

**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 · SQLite · pytest

## Run it

| Windows (PowerShell) | macOS / Linux / WSL2 / Codespaces |
|---|---|
| `./run.ps1` | `./run.sh` |

Windows says "running scripts is disabled"? Run `powershell -ExecutionPolicy Bypass -File .\run.ps1` instead, or once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Each run resets the demo data, then starts the API on **http://localhost:8000**. Open **http://localhost:8000/docs** to try every endpoint in the browser.

Run the tests:

```bash
cd shopapi
python -m pytest        # or: uv run python -m pytest
```

## Demo users

| id | Name | Email | Password | Token |
|---|---|---|---|---|
| 1 | Ana | ana@example.com | ana-password | `ana-token` |
| 2 | Ben | ben@example.com | ben-password | `ben-token` |
| 3 | Admin | admin@example.com | admin-password | `admin-token` (admin) |

Send the token as a header: `Authorization: Bearer ana-token`.
In `/docs`, use `POST /auth/login` to get it.

> **Demo-grade auth.** Fixed tokens are fine for learning, never for a real shop. A real shop needs expiring tokens, rate-limited logins and a vetted login library.

Seed data also includes 9 products (id 1 is the Keyboard), the coupons `SAVE10` (valid), `WELCOME5` (expired) and `OLD20` (switched off), and orders #10–#13.

## Endpoints

| Method | Path | Who | What |
|---|---|---|---|
| POST | `/auth/login` | anyone | Email + password → token |
| GET | `/products?q=&page=1&page_size=10` | anyone | List and search products (page 1 is the first page) |
| GET | `/products/{id}` | anyone | One product |
| POST | `/orders` | customer | Place an order (`items`, optional `coupon_code`) |
| GET | `/orders` | customer | My orders, newest first |
| GET | `/orders/{id}` | customer | One of **my** orders (someone else's → 404) |
| POST | `/orders/{id}/cancel` | customer | Cancel a pending or paid order; stock goes back |
| POST | `/coupons/preview` | customer | What would this order cost with this coupon? |
| GET | `/products/{id}/reviews` | anyone | Reviews of a product |
| POST | `/products/{id}/reviews` | customer | Review a product you bought (once) |
| POST | `/admin/products` | admin | Add a product |
| POST | `/admin/coupons` | admin | Add a coupon (expiry must include a time zone) |
| POST | `/admin/orders/{id}/ship` | admin | Mark an order as shipped |
| GET | `/admin/reports/sales` | admin | Units and revenue per product |
| GET | `/admin/reports/orders-export?fmt=csv` | admin | Finance export (legacy code) |
| GET | `/health` | anyone | `{"status": "ok"}` |

## Business rules

- Money is `Decimal`, rounded half-up to the cent, and sent as strings like `"49.90"`. Never use float.
- Tax is 10%, charged after the coupon discount: `total = subtotal - discount + tax`.
- Times are timezone-aware UTC. Code gets "now" from `app/clock.py` so tests can freeze it.
- Order status: `pending` → `paid` → `shipped`, or `cancelled` (only from pending or paid).

## Code map

```
app/
  main.py            create_app(): builds the app, adds the routers
  db.py              engine, one session per request, Money and UTCDateTime column types
  models.py          tables: User, Product, Coupon, Order, OrderItem, Review
  schemas.py         request/response shapes (pydantic)
  auth.py            demo-grade login and "who is calling?"
  clock.py           get_now(): the only place that reads the clock
  routers/           one file per area: auth, products, orders, coupons, reviews, admin
  services/          pricing.py (order maths), coupons.py (is this coupon usable?)
  legacy/            report_export.py: old, messy, working. Lab 7 refactors it
seed.py              deterministic demo data
tests/               fast tests; each test gets its own in-memory database
AGENTS.md            rules for AI coding agents working in this folder
```

## How the labs use ShopAPI

| Lab | What you do |
|---|---|
| Lab 3 (S3) | Improve `AGENTS.md` and measure the agent before and after |
| Lab 4 (S4) | Take a ticket to a pull request with green protected tests (`labs/lab04_ticket_to_pr`) |
| Lab 5 (S5) | Find 10 planted bugs in a copy of ShopAPI (`labs/lab05_bug_hunt`) |
| Lab 6 (S6) | Attack and defend: prompt injection in reviews, secrets scanning (`labs/lab06_attack_defend`) |
| Lab 7 (S7) | Characterization tests, then refactor `app/legacy/report_export.py` (`labs/lab07_legacy`) |
