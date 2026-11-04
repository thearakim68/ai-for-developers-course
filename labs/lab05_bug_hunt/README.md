# Lab 5: Bug hunt in ShopAPI

**Goal:** find and fix 10 "almost right" bugs, the kind AI coding agents write. All the visible tests pass. That's the point: green tests don't prove the code is right.

Time: about 1.5 hours.

## Setup

`starter/shopapi/` is a copy of ShopAPI with 10 bugs planted. Work in there:

```bash
cd labs/lab05_bug_hunt/starter/shopapi
python -m pytest              # all green... and still 10 bugs
./run.ps1                     # or ./run.sh, then open http://localhost:8000/docs
```

Want to start over? `git checkout -- labs/lab05_bug_hunt/starter` restores the starter.

## Rules
- Hunt in the starter, not in the main `shopapi/` folder, and don't diff the two folders. Comparing them shows you the answers and teaches you nothing.
- Bug 1 is in the same area as the S0 demo. The other nine involve money, dates, input checks, permissions and saving data.
- For each bug: **reproduce it**, **write a failing test** in `starter/shopapi/tests/`, **fix the code**, then run all the tests.
- You may use your AI agent to review a file or explain a diff. Check what it says before you accept it.
- Stuck? `hints.md` has 3 levels per area.

## Check your score

```bash
cd labs/lab05_bug_hunt
python grade.py               # or: python grade.py path/to/your/shopapi
```

`grade.py` runs your visible tests and the hidden tests, offline. It shows each unfixed bug's area; when you fix a bug, its name appears. A bug counts as fixed when all its hidden tests pass, and your visible tests must still pass too.

## Explain it without AI
1. Why did the visible tests pass with 10 bugs in the code?
2. Which bug would hurt real customers most, and why?
3. What one test would you add to every new endpoint from now on?
