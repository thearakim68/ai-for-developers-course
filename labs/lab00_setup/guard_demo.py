"""guard_demo.py: watch the cost guard in shared/llm.py stop real calls.

Run it from the course folder:
    uv run python labs/lab00_setup/guard_demo.py

Free and offline: it uses the "fake" AI and a temporary spending record,
so it never touches your real spending record or any paid service.
The guard only protects calls that go through shared/llm.py.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import textwrap
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def temp_env(**values):
    old = {k: os.environ.get(k) for k in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def load_llm():
    shared = str(ROOT / "shared")
    if shared not in sys.path:
        sys.path.insert(0, shared)
    import llm
    return llm


def main(stream=None) -> int:
    stream = stream or sys.stdout
    say = lambda line="": stream.write(line + "\n")
    llm = load_llm()
    old_ledger = llm.LEDGER
    tmp = tempfile.mkdtemp(prefix="guard-demo-")
    stopped = 0
    try:
        llm.LEDGER = Path(tmp) / "spend.json"
        client = llm.get_guarded_client("fake")

        say("")
        say("Demo 1: the same request, again and again")
        with temp_env(COURSE_SPEND_CAP_USD="5", COURSE_MAX_CALLS_PER_MIN="20"):
            for i in range(1, 8):
                try:
                    client.complete("fix the failing test")
                    say(f"  call {i}: sent (fake AI, $0.00)")
                except llm.CostGuardError as e:
                    say(f"  call {i}: STOPPED by the loop breaker")
                    for part in textwrap.wrap(str(e), 56):
                        say("     " + part)
                    stopped += 1
                    break

        say("")
        say("Demo 2: spend cap set to $0")
        llm.LEDGER = Path(tmp) / "spend2.json"
        with temp_env(COURSE_SPEND_CAP_USD="0"):
            try:
                client.complete("write a new feature")
                say("  call 1: sent")
            except llm.CostGuardError:
                say("  call 1: STOPPED by the spend cap")
                say("     The cap is $0, so no call may run.")
                stopped += 1
        say("")
        say(f"{stopped} of 2 calls stopped by the cost guard.")
        say("")
    finally:
        llm.LEDGER = old_ledger
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if stopped == 2 else 1


if __name__ == "__main__":
    sys.exit(main())
