# Lab 1: Cost meter + catch a made-up API

**Goal:** by the end, every AI call you make shows its **tokens and its cost**, and you have **caught one made-up API with code** (not with trust).

Time: about 1 hour. **Free:** everything works with the fake AI. A real model is optional; the optional real-model steps below cost well under $0.01 in total through the course client (prices in `shared/llm.py`).
Lectures: S1 L01 (tokens & cost) and S1 L05 (hallucinations). The other S1 demos are here too (see "More demos").

Run every command from the **course folder** (the one with `pyproject.toml`).

---

## Part A: The cost meter

### Step 1: Run the meter with the fake AI
```
uv run python labs/lab01_llm_basics/cost_meter_demo.py
```
**Checkpoint 1:** you see `model: fake-model`, `input tokens: 21`, `cost: $0.000000`.
Remember: the fake AI counts **words**, not tokens. Real models report real token counts.

### Step 2: Work it out by hand, then check
Use the price table in `shared/llm.py` (search for `PRICES =`). Prices are USD per 1 million tokens: (input, output).
On paper, work out what **21 input + 23 output tokens** would cost on the large model, `claude-opus-5-5`.
Formula: `(input tokens × input price + output tokens × output price) ÷ 1,000,000`.
Then check:
```
uv run python labs/lab01_llm_basics/cost_meter_demo.py --compare
```
**Checkpoint 2:** your number matches the `claude-opus-5-5` line.

<details><summary>Hint 1</summary>

Find the two prices for `claude-opus-5-5`: the first is per 1M input tokens, the second per 1M output tokens.
</details>
<details><summary>Hint 2</summary>

21 × 4 = 84 and 23 × 20 = 460. Add them, then divide by 1,000,000.
</details>
<details><summary>Hint 3 (answer)</summary>

(84 + 460) ÷ 1,000,000 = **$0.000544**.
</details>

### Step 3: Build your own meter
Create `labs/lab01_llm_basics/my_meter.py`. It takes **any prompt from the command line**, sends it through the guarded client, and prints: model, input tokens, output tokens, cost, and your course total.
```
uv run python labs/lab01_llm_basics/my_meter.py "Explain what a token is in one sentence."
```
**Checkpoint 3:** it prints the five lines, and with the fake AI the cost is `$0.000000`.
Rule: call AI **only** through `get_guarded_client()` (never import an AI SDK directly; the grader checks this).

<details><summary>Hint 1</summary>

Start from `cost_meter_demo.py`. It already shows how to import `llm` from the `shared` folder and how to read `r.input_tokens`, `r.output_tokens` and `r.cost_usd`.
</details>
<details><summary>Hint 2</summary>

The prompt is in `sys.argv[1:]`. Join the parts with spaces: `" ".join(sys.argv[1:])`. If it's empty, print a short usage line and exit.
</details>
<details><summary>Hint 3 (a full solution)</summary>

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import llm

prompt = " ".join(sys.argv[1:])
if not prompt:
    sys.exit('Usage: my_meter.py "your prompt"')
r = llm.get_guarded_client().complete(prompt)
print("model:        ", r.model)
print("input tokens: ", r.input_tokens)
print("output tokens:", r.output_tokens)
print(f"cost:          ${r.cost_usd:.6f}")
print("course total: ", llm.spend_status())
```
</details>

### Step 4a (optional, no API key): a real model through Claude Code
If you have Claude Code installed and signed in, it can print what one real call used, as JSON. `usage_view.py` makes that readable:
```
claude -p "In one sentence: what is a token?" --output-format json | uv run python labs/lab01_llm_basics/usage_view.py
```
You'll see input, cache read, cache write, output and thinking tokens, the context of the last call, the stop reason, the turns, the seconds and a **list-price estimate**. Subscription users aren't billed per call. Run the same command twice and compare the cache lines. Useful options: `--brief`, `--find TEXT` and `--answer N`.

### Step 4b (optional, needs a key): a real model through the course client
Set the provider for this terminal only, then run your meter:
```
$env:COURSE_LLM_PROVIDER="anthropic"; $env:COURSE_CLAUDE_MODEL="claude-haiku-5-5"     # PowerShell
export COURSE_LLM_PROVIDER=anthropic COURSE_CLAUDE_MODEL=claude-haiku-5-5            # macOS / Linux / Codespaces
uv run --extra anthropic python labs/lab01_llm_basics/my_meter.py "Explain what a token is in one sentence."
```
Compare the real input token count with the fake one for the same prompt. Then check that the `model:` line matches a name in `PRICES` (a dated ID like `claude-haiku-5-5-2026...` is priced like its base name; an unknown model gets the conservative fallback price).
Other providers (OpenAI, Gemini, Ollama): see the top of `shared/llm.py`.

### Step 5: See real tokens (free)
```
uv run --with tiktoken python labs/lab01_llm_basics/tokens_demo.py "Your own sentence, or a line of your code"
```
Try a line of code, a long name, and a sentence in another language you know. Which uses the most tokens per word?

---

## Part B: Catch a made-up API

### Step 6: Ask without context
Open an AI chat (or a coding agent **in an empty folder**, so it can't read this repo) and ask:
> In my Python course repo, `shared/llm.py` has `get_guarded_client()` that returns a client with a `complete()` method. How do I set the temperature to 0 when I call it? Show the code.

Copy the answer into `labs/lab01_llm_basics/my_catch.md`.

### Step 7: Check it with code
```
uv run python -c "import sys, inspect; sys.path.insert(0, 'shared'); import llm; print(inspect.signature(llm.GuardedClient.complete))"
```
If the answer used a method name, check it too (replace `NAME`):
```
uv run python -c "import sys; sys.path.insert(0, 'shared'); import llm; print(hasattr(llm.GuardedClient, 'NAME'))"
```
**Checkpoint 4:** in `my_catch.md`, write three lines: **what the AI said**, **the command you ran**, **what the code really says**.
If the AI was careful (it asked for the file or said it can't know), that's a good answer. Write that down, then try the same idea with a library you use (e.g. ask about a function in a specific version) and check it with `help()` or the official docs.

<details><summary>Hint 1</summary>

`inspect.signature` prints the real parameters of a function. Anything the AI used that isn't in that list doesn't exist.
</details>
<details><summary>Hint 2</summary>

The real `complete()` takes `prompt`, `system` and `max_tokens`. Is `temperature` there?
</details>
<details><summary>Hint 3 (example catch)</summary>

"AI said: `client.complete(prompt, temperature=0)`. I ran `inspect.signature(llm.GuardedClient.complete)`. Real: `(self, prompt, system=None, max_tokens=1024)`, so there is no temperature parameter."
</details>

### Step 8: Fix the cause
Ask the same question again, but this time attach or paste `shared/llm.py`. Does the answer change? Add one line about it to `my_catch.md`.

---

## More demos (from the S1 lectures; free with the fake AI)
| Command | Lecture | What you see |
|---|---|---|
| `uv run python labs/lab01_llm_basics/toy_sampler.py 2` | L02 | a toy next-word picker; change `SCORES` and the temperature |
| `uv run python labs/lab01_llm_basics/cost_meter_demo.py 5` | L02 | with a real model: an answer cut off at 5 tokens (`stop reason: max_tokens`); the fake AI ignores the limit |
| `uv run python labs/lab01_llm_basics/effort_demo.py` | L04 | the same question at `COURSE_EFFORT` low / high (real model needed to see a difference; on the default large model each run costs at most about $0.08, see the top of the file) |
| `uv run python labs/lab01_llm_basics/embed_demo.py` | L06 | similarity scores; the first line says the method: real **embeddings** (after `uv sync --extra embeddings`) or the **words** fallback (counts shared words only) |
| `uv run python labs/lab01_llm_basics/injection_echo.py` | L07 | what a model receives when a bug report hides an instruction |

Run the lab's tests (offline, free):
```
uv run pytest labs/lab01_llm_basics -q
```

---

## Common problems
| Problem | Fix |
|---|---|
| `CostGuardError: The same prompt was sent 5 times in 2 minutes` | That's the loop breaker. Wait 2 minutes or change the prompt. |
| `CostGuardError: Spend cap reached` | You hit `COURSE_SPEND_CAP_USD`. Check `llm.spend_status()`; raise the cap only if you mean to. |
| `tiktoken is not installed` | Use `uv run --with tiktoken ...` as shown above. |
| `embed_demo.py` says `method: words` | sentence-transformers isn't installed. That's fine for the lab; for real embeddings run `uv sync --extra embeddings` (a large download). |
| `ModuleNotFoundError: anthropic` | Add `--extra anthropic` to `uv run`. |
| A real call costs more than you expected | Check the `model:` line. An unknown model uses the conservative fallback price ($5 / $25 per 1M). |

---

## Explain it without AI
Answer in your own words in `my_catch.md`, before you open the solution branch:
1. Why can the same prompt cost different amounts on two models, and what two numbers decide the cost?
2. Why did the AI suggest an API that doesn't exist, even though it sounded sure?
3. Name one way to check an AI-suggested function and one way to check an AI-suggested package before you use it.
