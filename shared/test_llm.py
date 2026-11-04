"""Tests for the cost guard. Run: python -m pytest shared -q  (offline, uses the fake provider)."""
import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))


@pytest.fixture()
def llm(tmp_path, monkeypatch):
    monkeypatch.setenv("COURSE_LEDGER", str(tmp_path / "spend.json"))
    monkeypatch.setenv("COURSE_LLM_PROVIDER", "fake")
    import llm as m
    return importlib.reload(m)


def test_fake_call_is_free(llm):
    r = llm.get_guarded_client().complete("hello world")
    assert r.provider == "fake" and r.cost_usd == 0.0 and "hello" in r.text


def test_loop_breaker_stops_repeated_prompt(llm):
    c = llm.get_guarded_client()
    for _ in range(5):
        c.complete("same prompt")
    with pytest.raises(llm.CostGuardError, match="loop"):
        c.complete("same prompt")


def test_rate_breaker(llm, monkeypatch):
    monkeypatch.setenv("COURSE_MAX_CALLS_PER_MIN", "3")
    c = llm.get_guarded_client()
    for i in range(3):
        c.complete(f"p{i}")
    with pytest.raises(llm.CostGuardError, match="in one minute"):
        c.complete("p4")


def test_spend_cap(llm, monkeypatch):
    monkeypatch.setenv("COURSE_SPEND_CAP_USD", "0.000001")
    monkeypatch.setitem(llm.PROVIDERS, "fake", lambda p, s, m, t: llm.Result("x", "fake", "claude-opus-5-5", 1000, 1000, 0.0))
    monkeypatch.setattr(llm, "FREE", set())  # treat the fake as paid for this test
    c = llm.get_guarded_client()
    c.complete("first")  # costs money, crosses the tiny cap
    with pytest.raises(llm.CostGuardError, match="Spend cap"):
        c.complete("second")


def test_price_math(llm, monkeypatch):
    monkeypatch.setitem(llm.PROVIDERS, "fake", lambda p, s, m, t: llm.Result("x", "fake", "claude-opus-5-5", 1_000_000, 100_000, 0.0))
    monkeypatch.setattr(llm, "FREE", set())
    r = llm.get_guarded_client().complete("cost")
    assert r.cost_usd == pytest.approx(4.00 + 2.00)  # 1M in × $4 + 0.1M out × $20


def test_unknown_provider(llm):
    with pytest.raises(ValueError, match="Unknown provider"):
        llm.get_guarded_client("nope")


def test_dotenv_loader_rules(tmp_path, monkeypatch):
    import os
    import shared.llm as llm
    fake_root = tmp_path / "repo"; (fake_root / "shared").mkdir(parents=True)
    lines = ["# c", "export COURSE_T_A=abc # note", 'COURSE_T_B="x # y"', "COURSE_T_C=from_file", "EMPTY="]
    (fake_root / ".env").write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    monkeypatch.setattr(llm, "__file__", str(fake_root / "shared" / "llm.py"))
    for k in ("COURSE_T_A", "COURSE_T_B", "EMPTY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("COURSE_T_C", "from_env")
    llm._load_dotenv()
    assert os.environ["COURSE_T_A"] == "abc"
    assert os.environ["COURSE_T_B"] == "x # y"
    assert os.environ["COURSE_T_C"] == "from_env"
    assert "EMPTY" not in os.environ
    for k in ("COURSE_T_A", "COURSE_T_B"):
        monkeypatch.delenv(k)


def test_price_matches_dated_model_ids(llm):
    assert llm._price("claude-sonnet-5-5") == llm.PRICES["claude-sonnet-5-5"]
    assert llm._price("claude-sonnet-5-5-20261001") == llm.PRICES["claude-sonnet-5-5"]
    assert llm._price("claude-haiku-5-5@20261001") == llm.PRICES["claude-haiku-5-5"]
    # not a dated suffix of a known model -> conservative fallback
    assert llm._price("claude-sonnet-5-50") == llm.UNKNOWN_PRICE
    assert llm._price("claude-sonnet-5") == llm.UNKNOWN_PRICE
    assert llm._price("some-other-model") == llm.UNKNOWN_PRICE
