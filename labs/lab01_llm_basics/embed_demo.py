"""embed_demo.py: compare sentences by meaning with embeddings.  (S1 L06)

Two methods. The first output line always says which one ran:
  * embeddings: a small free local model (all-MiniLM-L6-v2) via sentence-transformers.
    Install once with  uv sync --extra embeddings  (the first run also downloads the model).
  * words: a tiny pure-Python fallback that counts SHARED WORDS (bag of words). It does NOT
    understand meaning. It runs everywhere, and it shows what embeddings improve on.
Run from the course folder:
    uv run python labs/lab01_llm_basics/embed_demo.py            # embeddings if installed, else words
    uv run python labs/lab01_llm_basics/embed_demo.py --words    # force the word-count fallback
"""
from __future__ import annotations

import math
import re
import sys
from collections import Counter

QUERY = "Ben can see Ana's order"
OTHERS = [
    "A customer can read another customer's order",
    "Ben ordered a new keyboard",
    "The shop is closed on Sunday",
]
MODEL_NAME = "all-MiniLM-L6-v2"


def bag_of_words(text: str) -> Counter:
    return Counter(re.findall(r"[a-z0-9']+", text.lower()))


def cosine(a: Counter, b: Counter) -> float:
    dot = sum(a[w] * b[w] for w in a)
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def word_scores(query: str, others: list[str]) -> list[float]:
    q = bag_of_words(query)
    return [cosine(q, bag_of_words(t)) for t in others]


def embedding_scores(query: str, others: list[str]) -> tuple[int, list[float]]:
    from sentence_transformers import SentenceTransformer, util

    model = SentenceTransformer(MODEL_NAME)
    q = model.encode(query)
    return len(q), util.cos_sim(q, model.encode(others))[0].tolist()


def has_sentence_transformers() -> bool:
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    use_words = "--words" in args or not has_sentence_transformers()
    if use_words:
        scores = word_scores(QUERY, OTHERS)
        print("method: words (fallback: counts SHARED WORDS, not meaning)")
        if "--words" not in args:
            print("  (sentence-transformers is not installed: run  uv sync --extra embeddings  for real embeddings)")
    else:
        size, scores = embedding_scores(QUERY, OTHERS)
        print(f"method: embeddings ({MODEL_NAME}, compares MEANING)")
        print("numbers per sentence:", size)
    print(f"query: {QUERY}")
    for text, score in sorted(zip(OTHERS, scores), key=lambda p: -p[1]):
        print(f"{score:.2f}  {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
