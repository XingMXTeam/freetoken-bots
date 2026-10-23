# FreeToken Bots

**Free LLM models for your AI agents - re-checked daily, and actually called to prove they still answer.**

[中文版](README.zh-CN.md)

Most "free AI models" lists are stale the day they are published. Models
get renamed, free tiers shrink, and a model that is *listed* as free may
answer with a 429 - or a 404 - when your agent actually calls it. This
repository treats the free tier as a moving target:

- **Daily roster.** A script re-reads the public OpenRouter catalog and
  keeps only models that are *genuinely* free (every pricing field is
  $0), support tool calls, and output text. Out of 468 catalog models,
  16 qualify today. → [`data/free-models.json`](data/free-models.json)
- **Live health checks.** The top picks are probed with real (tiny) API
  calls and the results - OK, rate-limited, no-endpoint - are recorded
  with timestamps. → [`data/status.json`](data/status.json)
- **Copy-paste recipes.** Verified configuration that wires these
  models into agent products, starting with the Pi coding agent.
  → [`recipes/`](recipes/)

## Current roster (refreshed 2026-10-23)

| # | Model | Context | Reasoning |
|---|-------|---------|-----------|
| 1 | `poolside/laguna-s-2.1:free` | 262K | yes |
| 2 | `poolside/laguna-xs-2.1:free` | 262K | yes |
| 3 | `cohere/north-mini-code:free` | 256K | yes |
| 4 | `thinkingmachines/inkling-small:free` | 1M | yes |
| 5 | `thinkingmachines/inkling:free` | 1M | yes |
| 6 | `nvidia/nemotron-3-ultra-550b-a55b:free` | 1M | yes |
| 7 | `nvidia/nemotron-3.5-lightning:free` | 1M | yes |
| 8 | `nvidia/nemotron-3.5-super-vl:free` | 1M | yes |
| 9 | `dots-studio/dots-3-note-preview:free` | 512K | yes |
| 10 | `google/gemma-4-26b-a4b-it:free` | 262K | yes |
| 11 | `google/gemma-4-31b-it:free` | 262K | yes |
| 12 | `nvidia/nemotron-3-super-120b-a12b:free` | 262K | yes |
| 13 | `recursive/flint-v1.0:free` | 262K | yes |
| 14 | `xingchen-agi/xing4.0-29b-a4b:free` | 262K | yes |
| 15 | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256K | yes |
| 16 | `liquid/lfm-2.5-2.6b:free` | 66K | yes |

Plus `openrouter/free`, a meta-router that picks a working free model
server-side - the recommended last-resort fallback for any agent.

Full machine-readable roster with scores: `data/free-models.json`.
The table above is regenerated daily by CI; see
`data/free-models.md` for the always-current version.

## Latest health check (2026-10-22, manual probes)

| Model | Result |
|-------|--------|
| `cohere/north-mini-code:free` | OK - then completed real agent tasks (write + bash tools), output human-verified |
| `openrouter/free` | OK in ~1.3s |
| `google/gemma-4-31b-it:free` | Answered once, then HTTP 429 (shared upstream pool) |
| `poolside/laguna-s-2.1:free` | HTTP 429 on direct call; answered when reached through the router |
| `nvidia/nemotron-3-super-120b-a12b:free` | HTTP 404 despite being listed |

Lesson baked into every recipe here: **free models need failover.**
Never hard-code a single free model into an agent and walk away.

## Quick start

1. Get a free key at [openrouter.ai](https://openrouter.ai) (Keys →
   Create Key). No credit card, no credit balance needed.
2. Pick a recipe, e.g. the [Pi coding agent](recipes/pi/) - two config
   files and you are running an agent on $0 models.
3. For any OpenAI-compatible client, use base URL
   `https://openrouter.ai/api/v1` with model `openrouter/free` or any
   `:free` ID from the roster.

## Guardrails (so "free" stays free)

- Whitelist `:free` IDs only. The same model without the `:free`
  suffix is usually the **paid** twin - the classic footgun.
- Set a small spending limit on your key in the OpenRouter dashboard
  as a second lock.
- Use **your own** key. Sharing or pooling keys to serve the public
  violates free-tier terms, and one leaked key burns everyone's quota.
- Budget your probes: health checks spend the same daily allowance
  your agents use (this repo probes ~6 tiny requests per day).

## Roadmap

- [x] OpenRouter roster + health checks (daily, via GitHub Actions)
- [x] Pi agent recipe
- [ ] More providers: Gemini free tier, Groq, NVIDIA NIM, Cloudflare
      Workers AI, and free domestic endpoints (Zhipu GLM Flash,
      ModelScope, SiliconFlow)
- [ ] More recipes: Claude Code, Cursor, OpenCode

## Credits & disclaimer

Roster logic adapted from the FreeToken template by
[@MinLiBuilds](https://grokbot.dev/marketplace/freetoken/), extended
with health checks, guardrails, and recipes. Maintained by
[@maoxunxing](https://x.com/maoxunxing) - an indie developer who runs
these models daily for real work, which is where the health data comes
from.

Not affiliated with OpenRouter or any model provider. Free tiers,
quotas, and model availability change without notice; the timestamps
in `data/` tell you how fresh any claim in this repo is.
