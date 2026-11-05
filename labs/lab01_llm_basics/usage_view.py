"""usage_view.py: a short, readable summary of one Claude Code run.  (S1 L01-L04, L06)

Claude Code can print what one run really used, as JSON. Pipe it into this script:
    claude -p "In one sentence: what is a token?" --output-format json | uv run python labs/lab01_llm_basics/usage_view.py
Options:
    --find TEXT   also show up to 2 answer lines that contain TEXT (e.g. --find user_id)
    --answer N    show the first N characters of the answer (default 160)
    --brief       only the answer and the stop-reason line (to compare several runs)

No AI call happens here: the script only reads the JSON that Claude Code printed.
The dollar figure is Claude Code's list-price estimate. Subscription users aren't billed per call.
"""
from __future__ import annotations

import json
import sys


def summarise(data: dict, find: str | None = None, answer_chars: int = 160, brief: bool = False) -> list[str]:
    if data.get("is_error"):
        return [f"error: {data.get('result') or data.get('subtype') or 'unknown error'}"]
    models = data.get("modelUsage") or {}
    total = {k: sum(int(m.get(k, 0) or 0) for m in models.values())
             for k in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens", "thinkingTokens")}
    main = max(models.items(), key=lambda kv: kv[1].get("outputTokens", 0), default=("?", {}))
    name, info = main
    answer = " ".join(str(data.get("result", "")).split())
    if len(answer) > answer_chars:
        answer = answer[:answer_chars].rstrip() + " …"
    sent = total["inputTokens"] + total["cacheReadInputTokens"] + total["cacheCreationInputTokens"]
    others = [m for m in models if m != name]
    calls = (data.get("usage") or {}).get("iterations") or []
    last = sum(int(calls[-1].get(k, 0) or 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")) if calls else sent
    lines = [
        f"answer:        {answer}",
        f"model:         {name}" + (f" (+ {', '.join(others)})" if others else "")
        + f" · context window {info.get('contextWindow', 0):,}",
        f"input tokens:  {total['inputTokens']:,}",
        f"cache read:    {total['cacheReadInputTokens']:,}",
        f"cache write:   {total['cacheCreationInputTokens']:,}",
        f"output tokens: {total['outputTokens']:,} (thinking: {total['thinkingTokens']:,})",
        f"tokens read:   {sent:,} (input + cache read + cache write, all model calls)",
        f"last call:     {last:,} tokens of context",
        f"stop reason:   {data.get('stop_reason')} · turns: {data.get('num_turns')}"
        f" · seconds: {(data.get('duration_ms') or 0) / 1000:.1f}",
        f"list-price estimate: ${float(data.get('total_cost_usd') or 0):.4f}"
        " (subscription users aren't billed per call)",
    ]
    if brief:  # just the answer and how it ended (for comparing several runs on one screen)
        lines = [lines[0], lines[8]]
    if find:
        hits = [ln.strip()[:110] for ln in str(data.get("result", "")).splitlines() if find in ln][:2]
        lines.append(f"'{find}' lines: " + (" | ".join(hits) if hits else "(none)"))
    return lines


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    find = args[args.index("--find") + 1] if "--find" in args and args.index("--find") + 1 < len(args) else None
    chars = int(args[args.index("--answer") + 1]) if "--answer" in args else 160
    raw = sys.stdin.read().lstrip("\ufeff")  # Windows PowerShell may add a byte-order mark when piping
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("usage_view.py expects the JSON from:  claude -p \"...\" --output-format json")
        return 1
    if isinstance(data, list):  # some versions print a list of events; the last one is the result
        data = next((d for d in reversed(data) if isinstance(d, dict) and d.get("type") == "result"), {})
    for line in summarise(data, find, chars, "--brief" in args):
        print(line)
    return 0


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
