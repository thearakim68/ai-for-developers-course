"""Tests for doctor.py. Run from the course folder:  python -m pytest labs/lab00_setup -q
Offline: no network, no real git config, no paid AI calls."""
import importlib
import io
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import doctor  # noqa: E402

SECRET_KEY = "sk-TESTSECRET1234567890"
SECRET_EMAIL = "student.private@example.org"


class Utf8Stream(io.StringIO):
    encoding = "utf-8"


class AsciiStream(io.StringIO):
    encoding = "ascii"


@pytest.fixture(autouse=True)
def isolate(monkeypatch):
    """Keep each test from leaking sys.path entries, the llm module, or env vars into other tests
    (a fake repo's llm.py on sys.path would be picked up by a later importlib.reload)."""
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(os, "environ", os.environ.copy())
    saved = sys.modules.get("llm")
    yield
    if saved is None:
        sys.modules.pop("llm", None)
    else:
        sys.modules["llm"] = saved


@pytest.fixture()
def llm(tmp_path, monkeypatch):
    monkeypatch.setenv("COURSE_LEDGER", str(tmp_path / "real-ledger" / "spend.json"))
    monkeypatch.setenv("COURSE_NO_DOTENV", "1")  # a developer's own .env must not leak into tests
    sys.path.insert(0, str(REPO / "shared"))
    import llm as m
    return importlib.reload(m)


@pytest.fixture()
def fake_repo(tmp_path):
    """A minimal course folder: shared/llm.py (the real one), labs/, shopapi/."""
    (tmp_path / "shared").mkdir()
    (tmp_path / "shared" / "llm.py").write_text((REPO / "shared" / "llm.py").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "labs").mkdir()
    (tmp_path / "shopapi").mkdir()
    return tmp_path


def fake_run(git_ignore_code=0, name="Ana Kim", email=SECRET_EMAIL):
    def run(cmd, cwd=None):
        if cmd[:2] == ["uv", "--version"]:
            return 0, "uv 0.9.0 (abc 2026-10-01)"
        if cmd[:3] == ["git", "config", "user.name"]:
            return (0, name) if name else (1, "")
        if cmd[:3] == ["git", "config", "user.email"]:
            return (0, email) if email else (1, "")
        if cmd[:2] == ["git", "check-ignore"]:
            return git_ignore_code, ""
        return None, ""
    return run


# ---- single checks -----------------------------------------------------------------------------------
def test_python_new_enough():
    assert doctor.check_python((3, 12, 4)).status == doctor.OK
    assert doctor.check_python((3, 13, 0)).status == doctor.OK


def test_python_too_old():
    c = doctor.check_python((3, 11, 9))
    assert c.status == doctor.FAIL and "3.12" in c.label and "uv run" in c.hint


def test_uv_missing_and_present(monkeypatch):
    monkeypatch.setattr(doctor, "which", lambda n: None)
    assert doctor.check_uv().status == doctor.FAIL
    monkeypatch.setattr(doctor, "which", lambda n: "/bin/" + n)
    monkeypatch.setattr(doctor, "run", fake_run())
    c = doctor.check_uv()
    assert c.status == doctor.OK and c.label == "uv 0.9.0"


def test_git_ok_never_prints_email(monkeypatch, tmp_path):
    monkeypatch.setattr(doctor, "which", lambda n: "/bin/" + n)
    monkeypatch.setattr(doctor, "run", fake_run())
    c = doctor.check_git(tmp_path)
    assert c.status == doctor.OK and SECRET_EMAIL not in str(c) and "Ana" not in str(c)


def test_git_missing_identity(monkeypatch, tmp_path):
    monkeypatch.setattr(doctor, "which", lambda n: "/bin/" + n)
    monkeypatch.setattr(doctor, "run", fake_run(email=""))
    c = doctor.check_git(tmp_path)
    assert c.status == doctor.FAIL and "user.email" in c.label and "git config --global user.email" in c.hint


def test_git_not_installed(monkeypatch, tmp_path):
    monkeypatch.setattr(doctor, "which", lambda n: None)
    assert doctor.check_git(tmp_path).status == doctor.FAIL


def test_vscode_is_only_a_warning(monkeypatch):
    monkeypatch.setattr(doctor, "which", lambda n: None)
    assert doctor.check_vscode().status == doctor.WARN
    monkeypatch.setattr(doctor, "which", lambda n: "/bin/code")
    assert doctor.check_vscode().status == doctor.OK


def test_layout(fake_repo, tmp_path_factory):
    assert doctor.check_layout(fake_repo).status == doctor.OK
    empty = tmp_path_factory.mktemp("empty")
    c = doctor.check_layout(empty)
    assert c.status == doctor.FAIL and "shared/llm.py" in c.label


def test_llm_import_fails_on_broken_file(tmp_path, monkeypatch):
    (tmp_path / "shared").mkdir()
    (tmp_path / "shared" / "llm.py").write_text("this is not python (", encoding="utf-8")
    monkeypatch.delitem(sys.modules, "llm", raising=False)
    monkeypatch.setattr(sys, "path", list(sys.path))
    check, module = doctor.load_llm(tmp_path)
    assert check.status == doctor.FAIL and module is None


def test_env_file_states(monkeypatch, tmp_path):
    assert doctor.check_env_file(tmp_path).status == doctor.FAIL  # missing
    (tmp_path / ".env").write_text("COURSE_LLM_PROVIDER=fake\n", encoding="utf-8")
    monkeypatch.setattr(doctor, "run", fake_run(git_ignore_code=0))
    assert doctor.check_env_file(tmp_path).status == doctor.OK
    monkeypatch.setattr(doctor, "run", fake_run(git_ignore_code=1))
    c = doctor.check_env_file(tmp_path)
    assert c.status == doctor.FAIL and ".gitignore" in c.hint
    monkeypatch.setattr(doctor, "run", fake_run(git_ignore_code=128))
    assert doctor.check_env_file(tmp_path).status == doctor.WARN


def test_keys_none_is_a_warning(tmp_path):
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=\nOPENAI_API_KEY=your-key-here\n", encoding="utf-8")
    assert doctor.check_keys({}, tmp_path).status == doctor.WARN


def test_keys_show_provider_names_only(tmp_path):
    (tmp_path / ".env").write_text('GEMINI_API_KEY="AIzaTESTSECRET0987654321"\n', encoding="utf-8")
    c = doctor.check_keys({"ANTHROPIC_API_KEY": SECRET_KEY}, tmp_path)
    assert c.status == doctor.OK
    assert "Anthropic (Claude): key set" in c.label and "Google Gemini: key set (in .env)" in c.label
    assert "OpenAI" not in c.label
    for secret in (SECRET_KEY, "sk-", "AIza", "TESTSECRET"):
        assert secret not in str(c)


def test_read_env_file_does_not_touch_environ(tmp_path, monkeypatch):
    monkeypatch.delenv("DOCTOR_TEST_VAR", raising=False)
    (tmp_path / ".env").write_text("# comment\nexport DOCTOR_TEST_VAR='abc'\nB=1 # note\n", encoding="utf-8")
    values = doctor.read_env_file(tmp_path / ".env")
    assert values == {"DOCTOR_TEST_VAR": "abc", "B": "1"}
    import os
    assert "DOCTOR_TEST_VAR" not in os.environ


def test_spend_cap_default_and_bad_values(llm):
    c = doctor.check_spend_cap(llm, {})
    assert c.status == doctor.OK and "$5.00" in c.label
    assert doctor.check_spend_cap(llm, {"COURSE_SPEND_CAP_USD": "ten"}).status == doctor.FAIL
    assert doctor.check_spend_cap(llm, {"COURSE_SPEND_CAP_USD": "0"}).status == doctor.FAIL
    assert "$12.50" in doctor.check_spend_cap(llm, {"COURSE_SPEND_CAP_USD": "12.5"}).label


def test_spend_cap_reached_is_a_warning(llm, monkeypatch):
    monkeypatch.setattr(llm, "spend_status", lambda: {"spent_usd": 5.2, "cap_usd": 5.0, "left_usd": -0.2})
    c = doctor.check_spend_cap(llm, {})
    assert c.status == doctor.WARN and "cap reached" in c.label


def test_dry_run_is_free_and_leaves_real_ledger_alone(llm):
    real_ledger = llm.LEDGER
    for _ in range(7):  # more than the loop breaker allows: doctor must still pass every time
        assert doctor.check_dry_run(llm).status == doctor.OK
    assert not real_ledger.exists()
    assert llm.LEDGER == real_ledger


def test_dry_run_ignores_student_provider(llm, monkeypatch):
    monkeypatch.setenv("COURSE_LLM_PROVIDER", "anthropic")
    assert doctor.check_dry_run(llm).status == doctor.OK


def test_dry_run_failure(llm, monkeypatch):
    def boom(*a):
        raise RuntimeError("broken")
    monkeypatch.setitem(llm.PROVIDERS, "fake", boom)
    c = doctor.check_dry_run(llm)
    assert c.status == doctor.FAIL and "RuntimeError" in c.label
    assert doctor.check_dry_run(None).status == doctor.FAIL


def test_ollama_is_only_a_warning(monkeypatch):
    urls = []
    monkeypatch.setattr(doctor, "http_ok", lambda url, timeout=1.5: urls.append(url) or False)
    assert doctor.check_ollama({}).status == doctor.WARN
    assert urls == ["http://localhost:11434/api/tags"]
    monkeypatch.setattr(doctor, "http_ok", lambda url, timeout=1.5: True)
    assert doctor.check_ollama({"OLLAMA_HOST": "127.0.0.1:11434"}).status == doctor.OK


def test_codespaces_reminder():
    c = doctor.check_codespaces({"CODESPACES": "true"})
    assert c.status == doctor.WARN and "Stop the codespace" in c.hint
    assert doctor.check_codespaces({}).status == doctor.OK


# ---- the whole run --------------------------------------------------------------------------------
def all_good(monkeypatch, fake_repo):
    monkeypatch.setattr(doctor, "which", lambda n: "/bin/" + n)
    monkeypatch.setattr(doctor, "run", fake_run())
    monkeypatch.setattr(doctor, "http_ok", lambda url, timeout=1.5: False)
    monkeypatch.setattr(doctor, "check_python", lambda version=None: doctor.Check(doctor.OK, "Python 3.12.4", ""))
    (fake_repo / ".env").write_text("ANTHROPIC_API_KEY=" + SECRET_KEY + "\n", encoding="utf-8")


def test_main_all_green(monkeypatch, fake_repo, llm):
    all_good(monkeypatch, fake_repo)
    out = Utf8Stream()
    code = doctor.main(stream=out, root=fake_repo, environ={"OPENAI_API_KEY": "sk-proj-ANOTHERSECRET999"})
    text = out.getvalue()
    assert code == 0
    assert "All green — you're ready" in text and "✓" in text
    assert "! Ollama not running" in text  # warnings do not block
    for secret in (SECRET_KEY, "ANOTHERSECRET", SECRET_EMAIL, "Ana Kim"):
        assert secret not in text


def test_main_counts_things_to_fix(monkeypatch, fake_repo, llm):
    all_good(monkeypatch, fake_repo)
    monkeypatch.setattr(doctor, "run", fake_run(name="", git_ignore_code=1))
    monkeypatch.setattr(doctor, "which", lambda n: None if n == "uv" else "/bin/" + n)
    out = Utf8Stream()
    code = doctor.main(stream=out, root=fake_repo, environ={})
    text = out.getvalue()
    assert code == 1
    assert "3 things to fix" in text  # uv, git name, .env not ignored
    assert "✗ uv not found" in text and "→" in text


def test_main_one_thing_to_fix_singular(monkeypatch, fake_repo, llm):
    all_good(monkeypatch, fake_repo)
    monkeypatch.setattr(doctor, "which", lambda n: None if n == "uv" else "/bin/" + n)
    out = Utf8Stream()
    assert doctor.main(stream=out, root=fake_repo, environ={}) == 1
    assert "1 thing to fix" in out.getvalue()


def test_ascii_fallback_for_old_terminals(monkeypatch, fake_repo, llm):
    all_good(monkeypatch, fake_repo)
    out = AsciiStream()
    assert doctor.main(stream=out, root=fake_repo, environ={}) == 0
    text = out.getvalue()
    text.encode("ascii")  # would raise if any fancy symbol slipped through
    assert "All green - you're ready" in text and " OK " in text


# ---- the cost guard demo (used in the setup lecture) ------------------------------------------------
def test_guard_demo_stops_both_calls(llm):
    import guard_demo
    real_ledger = llm.LEDGER
    out = Utf8Stream()
    assert guard_demo.main(stream=out) == 0
    text = out.getvalue()
    assert "call 5: sent" in text and "call 6: STOPPED by the loop breaker" in text
    assert "STOPPED by the spend cap" in text and "2 of 2 calls stopped" in text
    assert not real_ledger.exists() and llm.LEDGER == real_ledger


def test_spend_cap_reads_env_file_like_llm(monkeypatch, fake_repo, llm):
    all_good(monkeypatch, fake_repo)
    (fake_repo / ".env").write_text("COURSE_SPEND_CAP_USD=12.5" + chr(10), encoding="utf-8")
    out = Utf8Stream()
    assert doctor.main(stream=out, root=fake_repo, environ={}) == 0
    assert "Spend cap: $12.50" in out.getvalue()
    # a real environment variable wins over .env, as in shared/llm.py
    out = Utf8Stream()
    doctor.main(stream=out, root=fake_repo, environ={"COURSE_SPEND_CAP_USD": "7"})
    assert "Spend cap: $7.00" in out.getvalue()


def test_bad_spend_cap_in_env_file_fails(monkeypatch, fake_repo, llm):
    all_good(monkeypatch, fake_repo)
    (fake_repo / ".env").write_text("COURSE_SPEND_CAP_USD=ten" + chr(10), encoding="utf-8")
    out = Utf8Stream()
    assert doctor.main(stream=out, root=fake_repo, environ={}) == 1
    assert "not a number" in out.getvalue()
