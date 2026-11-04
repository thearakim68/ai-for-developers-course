"""Lab 4: checks that the protected tests in shopapi/tests/ are exact copies of the originals.

    python labs/lab04_ticket_to_pr/check_protected.py
"""
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ORIGINALS = sorted((LAB_DIR / "protected_tests").glob("test_*.py"))
TESTS_DIR = LAB_DIR.parent.parent / "shopapi" / "tests"

problems = 0
for original in ORIGINALS:
    copy = TESTS_DIR / original.name
    if not copy.exists():
        print(f"MISSING  {copy}")
        problems += 1
    elif copy.read_bytes().replace(b"\r\n", b"\n") != original.read_bytes().replace(b"\r\n", b"\n"):
        print(f"CHANGED  {copy}  <- protected tests must not be edited")
        problems += 1
    else:
        print(f"OK       {copy.name}")
sys.exit(1 if problems else 0)
