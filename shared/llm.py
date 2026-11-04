"""llm.py: the course's guarded LLM client. Every lab calls AI only through `get_guarded_client()`.

Why: one interface for every provider ("any AI, any tool"), plus a COST GUARD so a bug or a runaway
agent loop can never drain your credit:
  * spend cap   - stops when the course total passes COURSE_SPEND_CAP_USD (default $5)
  * rate breaker - max COURSE_MAX_CALLS_PER_MIN calls per minute (default 20)
  * loop breaker - the same prompt more than 5 times in 2 minutes is treated as a loop and stopped

Providers (set COURSE_LLM_PROVIDER):
  fake      - offline, free, deterministic; used by every auto-test (default if nothing is set)
  anthropic - Claude via the official Anthropic SDK (ANTHROPIC_API_KEY or `ant auth login`)
  openai    - OpenAI via the official SDK (OPENAI_API_KEY; set COURSE_OPENAI_MODEL)
  gemini    - Google Gemini via google-genai (GEMINI_API_KEY; free tier available; set COURSE_GEMINI_MODEL)
  ollama    - local models via Ollama's HTTP API (no key; set COURSE_OLLAMA_MODEL)

Prices are per 1M tokens, checked 2026-11-04; free tiers / local models count as $0.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# ---- .env loader (standard library only) -------------------------------------------------------
def _load_dotenv() -> None:
    """Read KEY=value lines from the repo-root .env into os.environ, without overriding real env vars.
    Same rules as labs/lab00_setup/doctor.py: blank lines and # comments ignored, optional "export ",
    optional quotes, inline " # comment" stripped from unquoted values. Values are never printed."""
    env = Path(__file__).resolve().parent.parent / ".env"   # repo root only
    if not env.is_file():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, val = (part.strip() for part in line.split("=", 1))
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        elif " #" in val:
            val = val.split(" #", 1)[0].strip()
        if key and val:
            os.environ.setdefault(key, val)


if os.getenv("COURSE_NO_DOTENV") != "1":
    _load_dotenv()

# ---- prices (USD per 1M tokens: input, output) ------------------------------------------------
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
UNKNOWN_PRICE = (float(os.getenv("COURSE_PRICE_IN", "5")), float(os.getenv("COURSE_PRICE_OUT", "25")))  # conservative

LEDGER = Path(os.getenv("COURSE_LEDGER", Path.home() / ".ai-dev-course" / "spend.json"))


class CostGuardError(RuntimeError):
    """Raised before a call that would break the spend cap or looks like a runaway loop."""


@dataclass
class Result:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    stop_reason: str = "end_turn"


# ---- ledger ------------------------------------------------------------------------------------
def _load() -> dict:
    try:
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"total_usd": 0.0, "calls": []}


def _save(d: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, indent=1), encoding="utf-8")


def spend_status() -> dict:
    d = _load()
    cap = float(os.getenv("COURSE_SPEND_CAP_USD", "5"))
    return {"spent_usd": round(d["total_usd"], 4), "cap_usd": cap, "left_usd": round(cap - d["total_usd"], 4)}


def _price(model: str) -> tuple[float, float]:
    """Price for the model ID the API returned. Exact match first; then a dated/suffixed ID
    (e.g. "claude-sonnet-5-5-20261001" or "claude-sonnet-5-5@20261001") matches its base name
    (longest base name wins). Anything else gets the conservative UNKNOWN_PRICE."""
    if model in PRICES:
        return PRICES[model]
    for base in sorted(PRICES, key=len, reverse=True):
        if model.startswith(base) and model[len(base):len(base) + 1] in ("-", "@"):
            return PRICES[base]
    return UNKNOWN_PRICE


# ---- providers -----------------------------------------------------------------------------------
def _call_fake(prompt: str, system: str | None, model: str, max_tokens: int) -> Result:
    words = prompt.split()
    text = f"[fake:{model}] echo: " + " ".join(words[:40])
    return Result(text, "fake", model, len(words), len(text.split()), 0.0)


def _call_anthropic(prompt: str, system: str | None, model: str, max_tokens: int) -> Result:
    import anthropic

    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile
    kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": os.getenv("COURSE_EFFORT", "low")},  # labs are simple; set explicitly
    )
    if system:
        kwargs["system"] = system
    if os.getenv("COURSE_REFUSAL_FALLBACK", "1") == "1":
        # On a policy decline the API retries on Anthropic's recommended fallback model inside the same call.
        response = client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
    else:
        response = client.messages.create(**kwargs)
    text = "".join(b.text for b in response.content if b.type == "text")
    if response.stop_reason == "refusal":
        text = text or "[declined by the model's safety system]"
    return Result(text, "anthropic", response.model, response.usage.input_tokens, response.usage.output_tokens, 0.0,
                  response.stop_reason)


def _call_openai(prompt: str, system: str | None, model: str, max_tokens: int) -> Result:
    from openai import OpenAI

    client = OpenAI()
    r = client.responses.create(model=model, input=prompt, instructions=system, max_output_tokens=max_tokens)
    return Result(r.output_text, "openai", model, r.usage.input_tokens, r.usage.output_tokens, 0.0)


def _call_gemini(prompt: str, system: str | None, model: str, max_tokens: int) -> Result:
    from google import genai
    from google.genai import types

    client = genai.Client()
    r = client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=max_tokens))
    u = r.usage_metadata
    return Result(r.text or "", "gemini", model, u.prompt_token_count or 0, u.candidates_token_count or 0, 0.0)


def _call_ollama(prompt: str, system: str | None, model: str, max_tokens: int) -> Result:
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    body = json.dumps({"model": model, "messages": msgs, "stream": False, "options": {"num_predict": max_tokens}}).encode()
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    req = urllib.request.Request(f"{host}/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as f:
        d = json.load(f)
    return Result(d["message"]["content"], "ollama", model, d.get("prompt_eval_count", 0), d.get("eval_count", 0), 0.0)


PROVIDERS = {"fake": _call_fake, "anthropic": _call_anthropic, "openai": _call_openai, "gemini": _call_gemini, "ollama": _call_ollama}
DEFAULT_MODEL = {
    "fake": "fake-model",
    "anthropic": os.getenv("COURSE_CLAUDE_MODEL", "claude-opus-5-5"),
    "openai": os.getenv("COURSE_OPENAI_MODEL", ""),
    "gemini": os.getenv("COURSE_GEMINI_MODEL", ""),
    "ollama": os.getenv("COURSE_OLLAMA_MODEL", ""),
}
FREE = {"fake", "ollama"}  # $0; gemini counts $0 only if COURSE_GEMINI_FREE_TIER=1


# ---- the guarded client ------------------------------------------------------------------------
class GuardedClient:
    def __init__(self, provider: str | None = None, model: str | None = None):
        self.provider = provider or os.getenv("COURSE_LLM_PROVIDER", "fake")
        if self.provider not in PROVIDERS:
            raise ValueError(f"Unknown provider {self.provider!r}. Choose one of: {', '.join(PROVIDERS)}")
        self.model = model or DEFAULT_MODEL[self.provider]
        if not self.model:
            raise ValueError(f"Set a model for {self.provider}: e.g. COURSE_{self.provider.upper()}_MODEL=...")

    def _check(self, prompt: str) -> dict:
        d = _load()
        now = time.time()
        d["calls"] = [c for c in d["calls"] if now - c["t"] < 120]
        cap = float(os.getenv("COURSE_SPEND_CAP_USD", "5"))
        if d["total_usd"] >= cap:
            raise CostGuardError(f"Spend cap reached (${d['total_usd']:.2f} of ${cap:.2f}). Raise COURSE_SPEND_CAP_USD only if you mean to.")
        per_min = int(os.getenv("COURSE_MAX_CALLS_PER_MIN", "20"))
        if sum(1 for c in d["calls"] if now - c["t"] < 60) >= per_min:
            raise CostGuardError(f"More than {per_min} AI calls in one minute. Is a loop running away? Wait, then retry.")
        h = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        if sum(1 for c in d["calls"] if c["h"] == h) >= 5:
            raise CostGuardError("The same prompt was sent 5 times in 2 minutes. That looks like a loop, so it was stopped.")
        d["calls"].append({"t": now, "h": h})
        return d

    def complete(self, prompt: str, system: str | None = None, max_tokens: int = 1024) -> Result:
        d = self._check(prompt)
        r = PROVIDERS[self.provider](prompt, system, self.model, max_tokens)
        free = self.provider in FREE or (self.provider == "gemini" and os.getenv("COURSE_GEMINI_FREE_TIER") == "1")
        pin, pout = (0.0, 0.0) if free else _price(r.model)
        r.cost_usd = round((r.input_tokens * pin + r.output_tokens * pout) / 1_000_000, 6)
        d["total_usd"] += r.cost_usd
        _save(d)
        return r


def get_guarded_client(provider: str | None = None, model: str | None = None) -> GuardedClient:
    return GuardedClient(provider, model)
