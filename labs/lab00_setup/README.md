# Lab 0: Set up your workspace

**Goal:** run one command and see **"All green — you're ready"**.

Time: about 30 minutes. You only do this once.

---

## Pick your path

| | Cloud path | Local path |
|---|---|---|
| Where it runs | GitHub Codespaces, in your browser | Your own computer (Windows, macOS or Linux) |
| Good for | Any computer, quick start, API-based labs | Local AI models with Ollama, working offline |
| You install | Nothing | git, uv, VS Code (and Ollama, if you want local models) |

Not sure? Start with the cloud path. You can switch later.

---

## Steps

### Cloud path (GitHub Codespaces)
1. Open the course repository on GitHub.
2. Click **Code → Codespaces → Create codespace**.
3. Wait until VS Code opens in your browser. The course's dev container installs Python 3.12, uv and git for you.
4. Open the terminal: menu **☰ → Terminal → New Terminal**. The course folder is already open.
5. Go to step "Everyone" below.

Good habits on the cloud path:
- **Keep the codespace running while you work on the lab.**
- **Save your work** at every checkpoint (see "Save your work" below).
- **After the lab, stop the codespace.** A running codespace uses your free hours. A stopped codespace still uses storage, so delete codespaces you no longer need (save your work first). Hours, storage and prices: see [`labs/COSTS.md`](../COSTS.md).
- Set the idle timeout to a short time in your GitHub Codespaces settings.

### Save your work (commit and push)
You can't push to the course repository itself. Your work goes to **your own copy** on GitHub.

1. **Make your own copy (once):** if you haven't already, create your own copy of the course repository on GitHub with **Fork** (or **Use this template**, if the course page shows it) [verify which one the course repo offers]. If you started a codespace on the course repository directly, GitHub offers to create a fork when you push for the first time [verify].
2. **Commit** (save a version): open **Source Control** (the branch icon on the left), type a short message like `Lab 0 done`, and click **Commit**.
3. **Push** (send it to GitHub): click **Sync Changes**.

Or, in the terminal:
```
git add -A
git commit -m "Lab 0 done"
git push
```
`git add -A` never adds your `.env`, because `.gitignore` ignores it. Still, check the list of changed files before you commit.

### Local path (Windows, macOS, Linux)
1. Install **git**: https://git-scm.com
2. Install **uv** (it can install Python 3.12 for you). See the official page:
   https://docs.astral.sh/uv/getting-started/installation/
   - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Close and reopen your terminal afterwards.
3. Install **VS Code**: https://code.visualstudio.com
   (So the `code` command works on macOS: in VS Code press Cmd+Shift+P → "Shell Command: Install 'code' command in PATH".)
4. Get the course code:
   ```
   git clone <course-repo-url> ai-dev-course
   cd ai-dev-course
   code .
   ```
   Please use `git clone`, not a zip download. Git protects your secrets (see `.env` below).

### Everyone
1. Make your `.env` file from the example (works in PowerShell, macOS, Linux and Codespaces):
   ```
   cp .env.example .env
   ```
2. Run the doctor:
   ```
   uv run python labs/lab00_setup/doctor.py
   ```
   (No uv yet? `python labs/lab00_setup/doctor.py` also works. It will tell you what is missing.)
3. Fix every **✗** line, then run the doctor again.
4. When you see **All green — you're ready**, you're done.

---

## What the symbols mean

| Symbol | Meaning | Do I need to act? |
|---|---|---|
| ✓ | Good | No |
| ✗ | Must fix before the labs | Yes. These are counted in "N things to fix" |
| ! | Optional, or a reminder | No. A `!` never blocks you |

Some terminals can't show ✓ and ✗. Then you see `OK`, `X` and `!` instead. Same meaning.

---

## What each check means

| Check | What it looks at | Kind |
|---|---|---|
| Python | Python 3.12 or newer | ✗ if older |
| uv | The `uv` tool is installed | ✗ if missing |
| git | git is installed, and your name and email are set. The doctor only says "set". It never shows your email. | ✗ if missing |
| VS Code | The `code` command works in the terminal | ! only |
| Course folder | `shared/llm.py`, `labs/` and `shopapi/` are there | ✗ if missing |
| shared/llm.py | The course's AI client loads | ✗ if broken |
| .env | Your `.env` file exists, and git ignores it | ✗ if missing or not ignored |
| AI keys | Which providers have a key: names only, never the key | ! only. No key is fine for now |
| Spend cap | Your cost limit (`COURSE_SPEND_CAP_USD`, default $5) and what you spent | ✗ if not a number |
| Test AI call | One call through the course client with the **fake** provider: offline, free | ✗ if it fails |
| Ollama | A local Ollama is running (local path only) | ! only |
| Codespaces | Tells you if you are in a codespace, and reminds you to stop it | ! reminder |

---

## Keys and the `.env` file

- Your API keys go **only** in the `.env` file in the course folder.
- **Never** paste a key into your code, a chat, a screenshot, or a Q&A post.
- `.env` is listed in `.gitignore`, so git ignores it **while it is untracked** (never added). The doctor checks this for you. `.gitignore` cannot protect a key that was already committed.
- You don't need any key for Lab 0. Add keys when a lab asks for them.
- `shared/llm.py` reads `.env` for you. A variable set in your terminal wins over the same one in `.env`. (To switch this off: `COURSE_NO_DOTENV=1`.)
- On the cloud path, `.env` lives inside your codespace.

If a key ever leaks (you committed it, pushed it, or pasted it somewhere): **delete (revoke) it in the provider's dashboard and make a new one.** Removing it from the file is not enough.

## The cost guard

Every lab calls AI through `shared/llm.py`. It adds two safety checks:
- **Spend cap:** it stops new calls once its own running total of estimated costs passes `COURSE_SPEND_CAP_USD` (default $5).
- **Loop breaker:** it stops a request that repeats again and again, and too many calls in one minute.

What it can't do: it only sees calls that go **through `shared/llm.py`**. Other tools (Copilot, Claude Code, a provider's website) are not covered, and its cost numbers are estimates. It cannot guarantee your provider's bill. Set a spending limit in your provider account too.

See it work (free, offline):
```
uv run python labs/lab00_setup/guard_demo.py
```
It sends the same fake request until the loop breaker stops it, then tries one call with the cap set to $0.

The doctor's test call uses the free **fake** provider. It costs nothing and doesn't use your real spending record.

---

## Common problems

| You see | Fix |
|---|---|
| `✗ uv not found` | Install uv (step 2). **Close and reopen the terminal.** On Windows, also restart VS Code. |
| `✗ Python 3.11 (need 3.12 or newer)` | Run it with uv: `uv run python labs/lab00_setup/doctor.py`. The course pins Python 3.12, and uv downloads it if needed. |
| `✗ git: user.name not set` | `git config --global user.name "Your Name"` |
| `✗ git: user.email not set` | `git config --global user.email "you@example.com"` |
| `✗ .env file missing` | `cp .env.example .env` (in the old Windows cmd.exe: `copy .env.example .env`) |
| `✗ .env is NOT ignored by git` | Open `.gitignore` and add a line with `.env`. Run the doctor again. |
| `! .env exists, but this folder is not a git repo` | You downloaded a zip. Clone with `git clone` instead. |
| `✗ Course folder: missing ...` | You are in the wrong folder. `cd` into the course folder, then run again. |
| `✗ shared/llm.py does not load` | You changed it by accident. `git checkout -- shared/llm.py` |
| `✗ Spend cap: ... is not a number` | Use a plain number, like `COURSE_SPEND_CAP_USD=5` |
| `! VS Code: 'code' command not on PATH` (or `code .` does nothing) | Windows: close and reopen the terminal; if it still fails, run the VS Code installer again and tick "Add to PATH". macOS: in VS Code press Cmd+Shift+P → "Shell Command: Install 'code' command in PATH". Or open the folder with **File → Open Folder**. Optional. |
| `! Ollama not running` | Fine on the cloud path. Local path: install Ollama and start it. |

## Still stuck?

1. Read the ✗ line and the hint under it (the `→` line).
2. Check the course troubleshooting page.
3. Ask in the Q&A with the doctor output. The doctor never prints your keys or email, but **read the output for private details (like your name in a folder path) before you share it.** Never paste your `.env` file.

---

## For the curious: the tests

The doctor has its own tests. From the course folder:
```
uv run --with pytest python -m pytest labs/lab00_setup -q
```
