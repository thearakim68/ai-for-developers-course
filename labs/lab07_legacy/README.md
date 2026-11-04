# Lab 7: Refactor a legacy module safely

**Goal:** clean up `shopapi/app/legacy/report_export.py` without changing what it outputs. The finance team imports this file every Monday, so even one changed character breaks their spreadsheet.

Time: about 1 hour for this part (the deploy-triage part is in the S7 lecture notes).

## Steps
1. **Map it.** Ask your agent to explain the module: inputs, outputs, every quirk. Check its answer against the code.
2. **Pin the behaviour (characterization tests).** Copy the starter in and fill in the TODOs:
   ```bash
   cp labs/lab07_legacy/starter/test_report_export_characterization.py shopapi/tests/
   ```
   Capture what the code *does today*, quirks included (date format, upper-case status, the `TOTAL` line, unknown formats falling back to CSV, cancelled orders...). Don't fix anything yet.
3. **Commit.** Your tests are now the safety net.
4. **Refactor in small steps**, running the tests after each one. Ideas: no `import *`, no global `x`, real names, `Decimal` instead of float, `csv` module, type hints.
5. **Done when** all tests pass, the characterization tests are unchanged since step 3, and the output is byte-for-byte the same.

Found a real bug while pinning (for example, a customer name with a comma)? Write it down as a ticket. Don't fix it during the refactor: refactoring means no behaviour change.

## Explain it without AI
1. What is the difference between a characterization test and a normal test?
2. Which quirk would you have broken without the tests?
3. Why not fix the bugs you found in the same commit?
