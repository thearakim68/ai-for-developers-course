"""Lab 5 scorecard: runs your visible tests and the hidden bug tests on your ShopAPI copy.

    python grade.py                  # grades labs/lab05_bug_hunt/starter/shopapi
    python grade.py path/to/shopapi  # or another folder

Runs fully offline. Nothing is uploaded. The hidden tests are packed in
hidden_tests.bin and unpacked into a temporary folder only while grading.
"""
import base64
import io
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
BUNDLE = LAB_DIR / "hidden_tests.bin"
DEFAULT_FOLDER = LAB_DIR / "starter" / "shopapi"


def run_pytest(folder: Path, extra_args: list[str]) -> tuple[int, str]:
    env = dict(os.environ, PYTHONPATH=str(folder), PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *extra_args],
        cwd=folder, env=env, capture_output=True, text=True, timeout=300,
    )
    return result.returncode, result.stdout + result.stderr


def load_bundle(target: Path) -> list[dict]:
    """Unpacks the hidden tests into `target` and returns the bug list."""
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(BUNDLE.read_bytes()))) as bundle:
        bundle.extractall(target)
    return json.loads((target / "bugs.json").read_text(encoding="utf-8"))


def hidden_results(folder: Path) -> tuple[list[dict], dict[str, bool]]:
    """Returns (bugs, bug id -> True if every hidden test for that bug passed)."""
    with tempfile.TemporaryDirectory() as tmp:
        hidden = Path(tmp) / "hidden"
        bugs = load_bundle(hidden)
        report = Path(tmp) / "hidden.xml"
        run_pytest(folder, ["-c", str(hidden / "pytest.ini"), "--rootdir", str(hidden),
                            f"--junitxml={report}", str(hidden)])
        if not report.exists():
            return bugs, {}
        fixed = {bug["id"]: True for bug in bugs}
        seen = set()
        for case in ET.parse(report).getroot().iter("testcase"):
            module = case.get("classname", "").split(".")[-1]  # e.g. test_b03_...
            bug_id = module[5:8].upper() if module.startswith("test_b") else None
            if bug_id not in fixed:
                continue
            seen.add(bug_id)
            if case.find("failure") is not None or case.find("error") is not None:
                fixed[bug_id] = False
        return bugs, {bug_id: ok and bug_id in seen for bug_id, ok in fixed.items()}


def main() -> int:
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FOLDER).resolve()
    if not (folder / "app" / "main.py").exists():
        print(f"No ShopAPI found in {folder}.")
        return 2

    print(f"Grading {folder}\n")
    code, output = run_pytest(folder, [])
    summary = output.strip().splitlines()[-1] if output.strip() else "(no output)"
    visible_ok = code == 0
    print(f"Visible tests: {'PASS' if visible_ok else 'FAIL'}  ({summary})")
    if not visible_ok:
        print("  Fix your visible tests first: a fix that breaks other behaviour doesn't count.")

    bugs, results = hidden_results(folder)
    if not results:
        print("\nCould not run the hidden tests. Does `python -m pytest` work in your folder?")
        return 2

    print("\nBug hunt")
    for number, bug in enumerate(bugs, start=1):
        if results[bug["id"]]:
            print(f"  [x] Bug {number:>2}  {bug['title']}")
        else:
            print(f"  [ ] Bug {number:>2}  area: {bug['area']}  (hints.md, section \"{bug['area']}\")")
    score = sum(results.values())
    print(f"\nScore: {score}/{len(bugs)} bugs fixed" + ("  - all clear, nice work!" if score == len(bugs) else ""))
    return 0 if visible_ok and score == len(bugs) else 1


if __name__ == "__main__":
    sys.exit(main())
