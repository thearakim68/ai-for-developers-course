"""effort_demo.py: the same question at the effort level set in COURSE_EFFORT.  (S1 L04)

Only meaningful with a real model (the fake AI ignores effort). From the course folder, PowerShell:
    $env:COURSE_LLM_PROVIDER="anthropic"; $env:COURSE_EFFORT="low"
    uv run --extra anthropic python labs/lab01_llm_basics/effort_demo.py
    $env:COURSE_EFFORT="high"
    uv run --extra anthropic python labs/lab01_llm_basics/effort_demo.py
Cost per run on the default large model, from shared/llm.py prices: at most about
(1,000 in x $4 + 4,000 out x $20) / 1M = $0.084, because max_tokens is 4000.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import llm  # noqa: E402

# The buggy endpoint from S0 L01 (course/labs/demo_s0_l01/app/main.py), copied here so the script runs anywhere.
CODE = """
def current_user(x_user_id: int = Header()) -> User:
    user = db.get(User, x_user_id)
    if user is None:
        raise HTTPException(status_code=401)
    return user


@app.get("/orders/{order_id}")
def get_order(order_id: int, user: User = Depends(current_user)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404)
    return {"id": order.id, "item": order.item}
"""
QUESTION = ("Customers report that user 2 can read order 10, which belongs to user 1. "
            "Find the cause in this code and suggest a one-line fix." + CODE)


def main() -> int:
    start = time.perf_counter()
    r = llm.get_guarded_client().complete(QUESTION, max_tokens=4000)
    seconds = time.perf_counter() - start
    print("effort:       ", os.getenv("COURSE_EFFORT", "low"))
    print("model:        ", r.model)
    print(f"seconds:       {seconds:.1f}")
    print("output tokens:", r.output_tokens)
    print("stop reason:  ", r.stop_reason)
    print(f"cost:          ${r.cost_usd:.6f}  (course estimate)")
    print("answer (first line):", r.text.strip().splitlines()[0] if r.text.strip() else "(empty)")
    hits = owner_check_lines(r.text)
    print("owner check:  ", " | ".join(hits) if hits else "(no line mentions user_id)")
    return 0


def owner_check_lines(text: str, limit: int = 2) -> list[str]:
    """Answer lines that mention user_id: a quick way to see whether the model found the owner check."""
    return [line.strip() for line in text.splitlines() if "user_id" in line][:limit]


if __name__ == "__main__":
    sys.exit(main())
