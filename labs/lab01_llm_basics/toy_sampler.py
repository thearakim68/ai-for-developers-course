"""toy_sampler.py: a TOY next-word picker.  (S1 L02)

The scores are MADE UP for teaching. A real model scores every token it knows.
Run from the course folder (free, offline):
    uv run python labs/lab01_llm_basics/toy_sampler.py        # 10 picks at temperature 1.0
    uv run python labs/lab01_llm_basics/toy_sampler.py 2      # 10 picks at temperature 2.0
"""
from __future__ import annotations

import math
import random
import sys

SCORES = {"order": 3.0, "keyboard": 2.0, "cat": 0.0}  # toy scores for: "Ben can see Ana's ..."


def chances(temperature: float, scores: dict[str, float] = SCORES) -> dict[str, float]:
    if temperature <= 0:
        raise ValueError("temperature must be greater than 0 in this toy")
    weights = {w: math.exp(s / temperature) for w, s in scores.items()}
    total = sum(weights.values())
    return {w: v / total for w, v in weights.items()}


def pick(temperature: float, k: int = 10, rng: random.Random | None = None) -> list[str]:
    c = chances(temperature)
    return (rng or random).choices(list(c), weights=list(c.values()), k=k)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    for t in (0.5, 1.0, 2.0):
        print(f"temperature {t}: " + "  ".join(f"{w} {p:.1%}" for w, p in chances(t).items()))
    t = float(args[0]) if args else 1.0
    print(f"10 picks at temperature {t}: " + " ".join(pick(t)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
