# AI for Developers — course labs

Code and labs for the Udemy course **"AI for Developers: How LLMs Work, Cost & Fail in Code"**.

## Start here (Lab 0)
Pick **one** path:

- **Cloud (nothing to install):** on this page click **Code → Codespaces → Create codespace**. VS Code opens in your browser with Python 3.12 and `uv` ready.
- **Local (Windows / macOS / Linux):** install [Git](https://git-scm.com/downloads), [uv](https://docs.astral.sh/uv/getting-started/installation/) and [VS Code](https://code.visualstudio.com/), then:
  ```bash
  git clone https://github.com/thearakim68/ai-for-developers-course.git
  cd ai-for-developers-course
  code .
  ```

Then, in the VS Code terminal:
```bash
cp .env.example .env          # keys stay in this file; git ignores it
uv run python labs/lab00_setup/doctor.py
```
"All green — you're ready" means you can start. Details: [labs/lab00_setup/README.md](labs/lab00_setup/README.md).

## What's inside
| Folder | What it is |
|---|---|
| `shared/llm.py` | One guarded AI client for every lab: spend cap, loop breaker, a free offline "fake" AI |
| `labs/lab00_setup` | Setup check (`doctor.py`) and a cost-guard demo |
| `labs/lab01_llm_basics` | Tokens, cost, sampling, effort, hallucinations, embeddings, prompt injection |
| `shopapi/` | ShopAPI, the small online-shop project used in Part 2 |
| `labs/lab04_*` … `labs/lab07_*` | Workday labs: ticket → PR, bug hunt, attack & defend, legacy code |
| `labs/COSTS.md` | Real, dated tool and API prices with official sources |

## Costs
Lab 0 and every offline demo cost **$0**. Paid tools are optional; see [labs/COSTS.md](labs/COSTS.md) and set a spending limit with your provider before using a real API key.

## Help
Stuck? Run the doctor, read the lab README's "Common problems", then ask in the course Q&A with the doctor output. **Never paste your `.env` file or keys anywhere.**
