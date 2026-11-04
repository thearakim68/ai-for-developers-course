"""cost_meter_demo.py: one call through the guarded client, then what it cost.  (S1 L01, L02)

Run from the course folder:
    uv run python labs/lab01_llm_basics/cost_meter_demo.py            # output limit 100 tokens
    uv run python labs/lab01_llm_basics/cost_meter_demo.py 5          # output limit 5 tokens
    uv run python labs/lab01_llm_basics/cost_meter_demo.py --compare  # + the same tokens priced on each model

Free by default (fake AI). The fake AI counts WORDS, not tokens, and ignores the output limit.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import llm  # noqa: E402

REPORT = "Bug: Ben (user 2) can open order 10, but order 10 belongs to Ana."


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """The same formula as llm.py: (in x input price + out x output price) / 1,000,000."""
    pin, pout = llm._price(model)
    return round((input_tokens * pin + output_tokens * pout) / 1_000_000, 6)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    compare = "--compare" in args
    numbers = [a for a in args if a.isdigit()]
    limit = int(numbers[0]) if numbers else 100

    r = llm.get_guarded_client().complete("Summarise this bug report in one sentence: " + REPORT, max_tokens=limit)
    print("answer:       ", r.text)
    print("model:        ", r.model)
    print("input tokens: ", r.input_tokens)
    print("output tokens:", r.output_tokens)
    print("stop reason:  ", r.stop_reason)
    print(f"cost:          ${r.cost_usd:.6f}")
    print("course total: ", llm.spend_status())
    if compare:
        print()
        print(f"The same {r.input_tokens} in + {r.output_tokens} out on each priced model:")
        for model in llm.PRICES:
            print(f"  {model:<20} ${cost_usd(model, r.input_tokens, r.output_tokens):.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
