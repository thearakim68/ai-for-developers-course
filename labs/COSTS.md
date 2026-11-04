# What things cost (checked 2026-11-04)

Prices checked on 2026-11-04; they change — always check the linked page.
All prices are in USD. Every number comes from the official page linked next to it.
If an official page did not say something clearly, we write "not stated on official page".

## 1. Monthly subscriptions (one person)

| Plan | Price | Billing unit | Coding agent included? | Source (checked 2026-11-04) |
|---|---|---|---|---|
| Claude Pro | $20 | per month (billed monthly); or $17/month billed as $200/year | Yes, "Claude Code" is listed as a Pro feature | https://claude.com/pricing |
| ChatGPT Plus | $20 | per month | Yes, Codex is included in Free, Go, Plus, Pro, Business, Edu and Enterprise plans | https://learn.chatgpt.com/docs/pricing |
| ChatGPT Free | $0 | per month | Yes, "Explore Codex capabilities on quick coding tasks" | https://learn.chatgpt.com/docs/pricing |
| GitHub Copilot Free | $0 | per month | 2,000 completions per month; chat/agent: "Limited chat and agent usage" (exact number not stated on official page) | https://github.com/features/copilot/plans |
| GitHub Copilot Pro | $10 | per user per month | Unlimited code completions; "$15 monthly total credits" for chat/agent (1 AI credit = $0.01) | https://github.com/features/copilot/plans |
| Google AI Pro | not stated on official page (the page we got showed no USD amount) | per month | Gives more usage in Google Antigravity; Gemini CLI / Code Assist not mentioned | https://one.google.com/about/google-ai-plans/ |

**Important change for Gemini CLI / Gemini Code Assist:** since June 18, 2026, Gemini Code Assist
for individuals, Google AI Pro and Google AI Ultra no longer serve requests in the Code Assist IDE
extensions or Gemini CLI, and "Login with Google" no longer works for them. Google points users to
Antigravity / Antigravity CLI.
Source (checked 2026-11-04): https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals

The Gemini CLI docs say a free (unpaid) Gemini API key gives "250 maximum model requests / user / day",
Flash models only. Source (checked 2026-11-04): https://geminicli.com/docs/resources/quota-and-pricing/

## 2. API prices (pay per token)

Prices are USD per 1 million tokens (1M = 1,000,000), standard rate, no caching, no batch.

| Provider | Model | Input / 1M | Output / 1M | Source (checked 2026-11-04) |
|---|---|---|---|---|
| Anthropic | Claude Opus 5.5 | $4 | $20 | https://platform.claude.com/docs/en/about-claude/pricing |
| Anthropic | Claude Sonnet 5.5 | $2 | $10 | https://platform.claude.com/docs/en/about-claude/pricing |
| Anthropic | Claude Haiku 5.5 (prompts up to 100,000 tokens) | $0.10 | $0.50 | https://platform.claude.com/docs/en/about-claude/pricing |
| Anthropic | Claude Haiku 5.5 (prompts over 100,000 tokens) | $0.50 | $2.50 | https://platform.claude.com/docs/en/about-claude/pricing |
| OpenAI (large) | gpt-6-astra | $10.00 | $50.00 | https://developers.openai.com/api/docs/pricing |
| OpenAI (small) | gpt-5.4-mini | $0.75 | $4.50 | https://developers.openai.com/api/docs/pricing |
| Google | Gemini 3.8 Flash, paid tier | $0.75 (until 2026-12-31), then $1.50 from 2027-01-01 | $3.75 (until 2026-12-31), then $7.50 from 2027-01-01 | https://aistudio.google.com/docs/pricing |

- OpenAI prices are the standard tier, short context (up to 272K input tokens). The same page also
  lists a smaller model, gpt-6-luna, at $0.10 input / $0.50 output.
- Gemini API free tier: yes. The page says "Start building free of charge with generous limits",
  and Gemini 3.8 Flash is "Free of charge" on the free tier. Source: https://aistudio.google.com/docs/pricing

**Check against the course code (`shared/llm.py`, `PRICES`):**
Opus 5.5 = (4.00, 20.00), Sonnet 5.5 = (2.00, 10.00), Haiku 5.5 = (0.10, 0.50).
All three match the official page. One note: the Haiku 5.5 value matches the price for prompts up to
100,000 tokens. Prompts over 100,000 tokens cost more ($0.50 / $2.50), so `llm.py` would under-count those.

## 3. GitHub Codespaces (personal accounts)

| Item | GitHub Free | GitHub Pro | Source (checked 2026-11-04) |
|---|---|---|---|
| Included compute per month | 120 hours | 180 hours | https://docs.github.com/en/billing/concepts/product-billing/github-codespaces |
| Included storage per month | 15 GB-month | 20 GB-month | same page |

The page calls this "compute time" in hours, and lists an "included usage multiplier" equal to the core
count (2, 4, 8, 16, 32). How the multiplier reduces the included hours is not stated on official page.

Prices after the free amount (same page, checked 2026-11-04):

| Machine | Price |
|---|---|
| 2-core | $0.18 per hour |
| 4-core | $0.36 per hour |
| 8-core | $0.72 per hour |
| 16-core | $1.44 per hour |
| 32-core | $2.88 per hour |
| Storage | $0.07 per GB-month |

**Stopped codespaces still cost storage.** GitHub says a codespace "will continue to accrue storage
charges until it is deleted", whether it is running or stopped.
Source (checked 2026-11-04): https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle
By default, stopped codespaces are deleted after 30 days of no use.
Source (checked 2026-11-04): https://docs.github.com/en/codespaces/setting-your-user-preferences/configuring-automatic-deletion-of-your-codespaces
Tip: delete codespaces you no longer need.

## 4. Spending controls

| Provider | Hard limit (requests stop)? | Alerts only? | Source (checked 2026-11-04) |
|---|---|---|---|
| Anthropic (Claude Console) | Yes. Every tier has a monthly spend cap (Start $500, Build $1,000, Scale $200,000). You can also set your own lower limit on the Billing page. When reached, requests fail until next month or until you raise it. | Alerts: not stated on official page | https://platform.claude.com/docs/en/api/rate-limits |
| OpenAI (project budgets) | Yes, only if you turn on "Enforce a hard limit". Then requests fail with 429 `project_spend_limit_exceeded`. Enforcement is not instant, so spend can go slightly over. | Yes, by default: "Spend alerts do not enforce a cap" | https://developers.openai.com/api/docs/guides/spend-limits |
| Prepaid credits: Anthropic | "Most organizations pay with prepaid usage credits" (invoicing only via Sales). At zero credits, "you can no longer call the API or use the playground until you add more." Auto-reload exists (you set the trigger and refill balances); whether it is on or off by default: not stated on official page. Spend caps (above) still apply. | n/a | https://support.claude.com/en/articles/8977456-how-do-i-pay-for-my-claude-api-usage |
| Prepaid credits: OpenAI | When all credits run out, "API requests fail with HTTP `429` and error code `credit_balance_exhausted`." Auto Recharge exists and can add credits automatically; whether it is on by default, and whether prepaid is the default: not stated on the official page we could open. Project spend limits (above) still exist. | n/a | https://developers.openai.com/api/docs/guides/chatgpt-api-credits |

## 5. Worked example: one request

One request with **2,000 input tokens** and **500 output tokens**. Formula:
cost = (input tokens / 1,000,000 x input price) + (output tokens / 1,000,000 x output price)

**Claude Sonnet 5.5** ($2 input, $10 output per 1M):
- Input: 2,000 / 1,000,000 x $2 = $0.004
- Output: 500 / 1,000,000 x $10 = $0.005
- Total: **$0.009** (less than 1 cent)

**Claude Haiku 5.5** ($0.10 input, $0.50 output per 1M; prompt is under 100,000 tokens):
- Input: 2,000 / 1,000,000 x $0.10 = $0.0002
- Output: 500 / 1,000,000 x $0.50 = $0.00025
- Total: **$0.00045** (about 20 times cheaper than Sonnet here)

## What this course needs

- **Today's setup check costs $0.**
- **A free path exists.** You can follow the course with free options: ChatGPT Free (includes Codex),
  GitHub Copilot Free, the Gemini API free tier, and the free Codespaces hours.
- **One subscription is optional.** If you want a faster, stronger coding agent, one subscription (for example
  Claude Pro or ChatGPT Plus, each $20/month) is optional. API usage has separate billing: a subscription does
  not pay for API calls.
- If you use an API key, set a spend limit first (see section 4).
