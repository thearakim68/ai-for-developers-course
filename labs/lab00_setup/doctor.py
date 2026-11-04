"""doctor.py: checks that your computer (or Codespace) is ready for the course.

Run it from the course folder:
    uv run python labs/lab00_setup/doctor.py
or, without uv:
    python labs/lab00_setup/doctor.py

What it does: about a dozen quick checks, one line each.
  OK  (green tick)  = good
  X   (red cross)   = must fix before the labs   -> counts in "N things to fix"
  !   (warning)     = optional, or a reminder    -> never blocks you
It never prints your API keys or your email address, makes no paid AI calls,
and only talks to your own computer (the optional Ollama check uses localhost).

Standard library only (plus the course's own shared/llm.py).
This file must still run on old Python, so it can tell you to upgrade.
"""
from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # labs/lab00_setup/doctor.py -> course folder

OK, FAIL, WARN = "ok", "fail", "warn"
Check = namedtuple("Check", "status label hint")

# Provider name -> environment variable names that hold its key (first match wins).
PROVIDER_KEYS = [
    ("Anthropic (Claude)", ("ANTHROPIC_API_KEY",)),
    ("OpenAI", ("OPENAI_API_KEY",)),
    ("Google Gemini", ("GEMINI_API_KEY", "GOOGLE_API_KEY")),
]
PLACEHOLDER_WORDS = ("your", "xxxx", "changeme", "placeholder", "<", "...")


# ---- small helpers (tests replace these) ---------------------------------------------------------
def which(name):
    return shutil.which(name)


def run(cmd, cwd=None):
    """Run a command. Returns (exit_code, stdout). exit_code is None if it could not start."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=15)
        return p.returncode, (p.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return None, ""


def http_ok(url, timeout=1.5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def read_env_file(path):
    """Read KEY=VALUE lines from a .env file into a dict. Does NOT change os.environ."""
    values = {}
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].strip()
        values[key.strip()] = value
    return values


def is_real_value(value):
    """True if a key value looks real (not empty, not a placeholder). Never prints it."""
    v = (value or "").strip()
    if len(v) < 8:
        return False
    low = v.lower()
    return not any(w in low for w in PLACEHOLDER_WORDS)


# ---- the checks ------------------------------------------------------------------------------------
def check_python(version=None):
    v = tuple(version or sys.version_info)[:3]
    shown = ".".join(str(x) for x in v)
    if v >= (3, 12):
        return Check(OK, "Python " + shown, "")
    return Check(FAIL, "Python " + shown + " (need 3.12 or newer)",
                 "Run it with uv: uv run python labs/lab00_setup/doctor.py")


def check_uv():
    if not which("uv"):
        return Check(FAIL, "uv not found",
                     "Install uv (see README), then reopen your terminal")
    code, out = run(["uv", "--version"])
    return Check(OK, (out or "uv").split("(")[0].strip(), "")


def check_git(root=ROOT):
    if not which("git"):
        return Check(FAIL, "git not found", "Install git (git-scm.com), then reopen your terminal")
    missing = []
    for field in ("user.name", "user.email"):
        code, out = run(["git", "config", field], cwd=str(root))
        if code != 0 or not out:
            missing.append(field)
    # We only check that name and email exist. We never print them.
    if missing:
        f = missing[0]
        hint = 'git config --global {} "{}"'.format(f, "Your Name" if f == "user.name" else "you@example.com")
        return Check(FAIL, "git: " + ", ".join(missing) + " not set", hint)
    return Check(OK, "git: name set, email set", "")


def check_vscode():
    if which("code"):
        return Check(OK, "VS Code: 'code' command found", "")
    return Check(WARN, "VS Code: 'code' command not on PATH",
                 "Optional. See the README (Common problems)")


def check_layout(root=ROOT):
    need = ["shared/llm.py", "labs", "shopapi"]
    missing = [p for p in need if not (Path(root) / p).exists()]
    if missing:
        return Check(FAIL, "Course folder: missing " + ", ".join(missing),
                     "cd into the course folder, then run again")
    return Check(OK, "Course folder looks complete", "")


def load_llm(root=ROOT):
    """Import shared/llm.py. Returns (Check, module or None)."""
    shared = str(Path(root) / "shared")
    if shared not in sys.path:
        sys.path.insert(0, shared)
    try:
        module = importlib.import_module("llm")
    except Exception as e:  # show the error type only; it is enough to search for
        return Check(FAIL, "shared/llm.py does not load (" + type(e).__name__ + ")",
                     "Get a fresh copy: git checkout -- shared/llm.py"), None
    return Check(OK, "shared/llm.py loads", ""), module


def check_env_file(root=ROOT):
    env = Path(root) / ".env"
    if not env.exists():
        return Check(FAIL, ".env file missing",
                     "Run: cp .env.example .env")
    code, _ = run(["git", "check-ignore", "-q", ".env"], cwd=str(root))
    if code == 0:
        return Check(OK, ".env exists and git ignores it", "")
    if code == 1:
        return Check(FAIL, ".env is NOT ignored by git (keys could be uploaded)",
                     "Add a line .env to the .gitignore file")
    return Check(WARN, ".env exists, but this folder is not a git repo",
                 "Use git clone (not a zip), so git protects .env")


def check_keys(environ=None, root=ROOT):
    environ = os.environ if environ is None else environ
    file_values = read_env_file(Path(root) / ".env")
    found = []
    for name, variables in PROVIDER_KEYS:
        for var in variables:
            if is_real_value(environ.get(var)):
                found.append(name + ": key set")
                break
            if is_real_value(file_values.get(var)):
                found.append(name + ": key set (in .env)")
                break
    if not found:
        return Check(WARN, "AI keys: none set yet",
                     "Fine for now. Lab 0 needs no key")
    return Check(OK, "AI keys: " + "; ".join(found), "")


def check_spend_cap(llm, environ=None):
    environ = os.environ if environ is None else environ
    raw = environ.get("COURSE_SPEND_CAP_USD", "5")
    try:
        cap = float(raw)
    except ValueError:
        return Check(FAIL, "Spend cap: COURSE_SPEND_CAP_USD is not a number",
                     "Use a number, e.g. COURSE_SPEND_CAP_USD=5")
    if cap <= 0:
        return Check(FAIL, "Spend cap: must be more than $0", "Use a number, e.g. COURSE_SPEND_CAP_USD=5")
    try:
        s = llm.spend_status()
        spent = float(s["spent_usd"])
    except Exception:
        return Check(OK, "Spend cap: ${:.2f}".format(cap), "")
    label = "Spend cap: ${:.2f} (spent ${:.2f})".format(cap, spent)
    if spent >= cap:
        return Check(WARN, label + " - cap reached",
                     "Paid calls blocked. Raise the cap only if you mean to")
    return Check(OK, label, "")


def check_dry_run(llm):
    """One call through the guarded client with the free, offline 'fake' provider.
    Uses a temporary ledger, so it never touches your real spending record."""
    if llm is None:
        return Check(FAIL, "Test AI call skipped (shared/llm.py did not load)", "Fix the llm.py line above first")
    old_ledger = getattr(llm, "LEDGER", None)
    tmp = tempfile.mkdtemp(prefix="doctor-")
    try:
        llm.LEDGER = Path(tmp) / "spend.json"
        r = llm.get_guarded_client("fake").complete("doctor dry run", max_tokens=16)
        if r.provider != "fake" or r.cost_usd != 0:
            return Check(FAIL, "Test AI call: unexpected result", "Get a fresh copy: git checkout -- shared/llm.py")
        return Check(OK, "Test AI call (fake, offline): works, cost $0.00", "")
    except Exception as e:
        return Check(FAIL, "Test AI call failed (" + type(e).__name__ + ")",
                     "Get a fresh copy: git checkout -- shared/llm.py")
    finally:
        if old_ledger is not None:
            llm.LEDGER = old_ledger
        shutil.rmtree(tmp, ignore_errors=True)


def check_ollama(environ=None):
    environ = os.environ if environ is None else environ
    host = environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    if not host.startswith("http"):
        host = "http://" + host
    if http_ok(host + "/api/tags"):
        return Check(OK, "Ollama is running (local models)", "")
    return Check(WARN, "Ollama not running (only for the local path)",
                 "Optional. Local path only: install and start Ollama")


def check_codespaces(environ=None):
    environ = os.environ if environ is None else environ
    if environ.get("CODESPACES", "").lower() == "true":
        return Check(WARN, "You are in GitHub Codespaces",
                     "Push often. Stop the codespace when you finish")
    return Check(OK, "Running on your own computer", "")


# ---- output ------------------------------------------------------------------------------------------
def symbols_for(stream):
    """Use ✓ ✗ if the terminal can show them, else plain ASCII (old Windows code pages, pipes)."""
    try:
        "✓✗—→".encode(getattr(stream, "encoding", None) or "ascii")
        return {OK: "✓", FAIL: "✗", WARN: "!", "dash": "—", "arrow": "→"}
    except (UnicodeEncodeError, LookupError):
        return {OK: "OK", FAIL: "X ", WARN: "! ", "dash": "-", "arrow": "->"}


def effective_env(environ, root=ROOT):
    """What shared/llm.py will see: .env values, overridden by real environment variables."""
    if environ.get("COURSE_NO_DOTENV") == "1":
        return dict(environ)
    merged = {k: v for k, v in read_env_file(Path(root) / ".env").items() if v}
    merged.update(environ)
    return merged


def run_all(root=ROOT, environ=None):
    # Snapshot first: importing shared/llm.py copies .env values into os.environ,
    # and we want to tell "set in your shell" apart from "set in .env".
    environ = dict(os.environ) if environ is None else environ
    checks = [check_python(), check_uv(), check_git(root), check_vscode(), check_layout(root)]
    llm_check, llm = load_llm(root)
    checks.append(llm_check)
    checks += [check_env_file(root), check_keys(environ, root)]
    if llm is not None:
        checks.append(check_spend_cap(llm, effective_env(environ, root)))
    checks += [check_dry_run(llm), check_ollama(environ), check_codespaces(environ)]
    return checks


def main(argv=None, stream=None, root=ROOT, environ=None):
    stream = stream or sys.stdout
    sym = symbols_for(stream)
    checks = run_all(root, environ)
    out = ["", "Course doctor " + sym["dash"] + " checking your setup", ""]
    for c in checks:
        out.append(" {} {}".format(sym[c.status], c.label))
        if c.status != OK and c.hint:
            out.append("     {} {}".format(sym["arrow"], c.hint))
    fails = sum(1 for c in checks if c.status == FAIL)
    out.append("")
    if fails == 0:
        out.append("All green " + sym["dash"] + " you're ready")
    else:
        out.append("{} thing{} to fix (see the {} lines above)".format(fails, "" if fails == 1 else "s", sym[FAIL].strip()))
    out.append("")
    stream.write("\n".join(out) + "\n")
    stream.flush()
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
