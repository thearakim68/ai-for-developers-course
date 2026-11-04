"""tokens_demo.py: see how one real tokenizer cuts text into tokens.  (S1 L01)

Run from the course folder (free; the first run downloads the tokenizer file):
    uv run --with tiktoken python labs/lab01_llm_basics/tokens_demo.py
    uv run --with tiktoken python labs/lab01_llm_basics/tokens_demo.py "your own text here"

tiktoken is OpenAI's open-source tokenizer. Other model families cut text a bit differently,
so the same text can have a different token count on another model.
"""
from __future__ import annotations

import sys

TEXTS = (
    "Bug: Ben (user 2) can open order 10, but order 10 belongs to Ana.",
    "get_order() in ShopAPI checks current_user",
)


def split(text: str, encoding: str = "o200k_base") -> list[str]:
    import tiktoken

    enc = tiktoken.get_encoding(encoding)
    return [enc.decode([i]) for i in enc.encode(text)]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        print("tiktoken is not installed. Run:  uv run --with tiktoken python labs/lab01_llm_basics/tokens_demo.py")
        return 1
    for text in (args or TEXTS):
        pieces = split(text)
        print("|" + "|".join(pieces) + "|")
        print(f"words: {len(text.split())} / tokens: {len(pieces)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
