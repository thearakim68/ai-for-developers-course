# Lab 4: From ticket to pull request

**Goal:** ship two small ShopAPI features with an AI coding agent: ticket → plan → small diffs → green tests → pull request.

Time: about 2 hours. Work on a branch: `git switch -c lab04`.

## Rules
- The **protected tests** decide when you're done. Copy them in once, then never edit them:
  ```bash
  cp labs/lab04_ticket_to_pr/protected_tests/test_ticket_*.py shopapi/tests/
  ```
  Tell your agent that too: add a line to `shopapi/AGENTS.md`.
- Before you open the PR: `python labs/lab04_ticket_to_pr/check_protected.py` must print only `OK`.
- `cd shopapi && python -m pytest` must be fully green (old tests too).
- Time yourself on ticket T1 and ticket T2. Write both times in the PR description.

## Ticket T1: "Only show what we can ship"
*As a customer, I want to hide sold-out products so I don't pick something I can't order.*

Acceptance criteria:
1. `GET /products?in_stock=true` returns only products with `stock > 0`.
2. Without `in_stock` (or with `in_stock=false`), the list is unchanged.
3. `total` counts only the filtered products, so pagination still works.
4. Works together with `q` (search).

Protected tests: `test_ticket_t1_in_stock.py`

## Ticket T2: "Find my shipped orders"
*As a customer, I want to filter my orders by status so I can find what's on its way.*

Acceptance criteria:
1. `GET /orders?status=shipped` returns only my orders with that status, newest first.
2. Allowed values: `pending`, `paid`, `shipped`, `cancelled`. Anything else → 422.
3. Without `status`, I get all my orders, as before.
4. Never shows another customer's orders.

Protected tests: `test_ticket_t2_order_status.py`

## Explain it without AI
1. Which acceptance criterion was easiest to get wrong, and which test caught it?
2. Why must the agent not edit the protected tests?
3. Was the AI faster on T1 or on T2? Why?
