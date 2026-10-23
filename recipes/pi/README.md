# Recipe: Pi coding agent on free models

Run the open-source [Pi](https://github.com/earendil-works/pi) coding
agent entirely on free OpenRouter models. Verified end-to-end on
2026-10-22: the agent completed write-tool and bash-tool tasks on
`cohere/north-mini-code:free`, with the output checked by a human.

## 1. Install Pi

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
pi --version
```

## 2. Get a free OpenRouter key

Create an account at openrouter.ai and generate an API key
(Keys → Create Key). Free models still require a key. You do not need
to add credit: free models draw from a separate daily allowance
(50 requests/day on a fresh account when this recipe was written).

```bash
export OPENROUTER_API_KEY=sk-or-v1-...   # your own key, never commit it
```

## 3. Drop in the config

```bash
mkdir -p ~/.pi/agent
cp models.json settings.json ~/.pi/agent/
```

- `models.json` registers the current free roster with Pi at $0 cost.
  Regenerate it any time with `scripts/refresh.py` (this repo's data)
  or simply rely on Pi's built-in OpenRouter catalog.
- `settings.json` sets the default model to the verified pick and -
  important - restricts `enabledModels` to the free roster plus the
  `openrouter/free` router. That is your no-paid-model guardrail: the
  same model *without* the `:free` suffix (for example
  `poolside/laguna-s-2.1`) is a paid model and is deliberately not in
  the list. Optionally set a small spending limit on the key itself in
  the OpenRouter dashboard as a second lock.

## 4. Run

```bash
cd your-project
pi -p "Summarize the TODO comments in src/ and write them to TODO.md"
```

## Living with free models

- **Expect 429s.** Free models share upstream pools. Build failover:
  if a run fails, retry with the next model in `data/free-models.json`,
  and keep `openrouter/free` (a router that picks a working free model
  server-side) as the last resort.
- **Expect churn.** A listed model can 404 tomorrow. Refresh the roster
  before a work session; if a model returns 404, drop it for the day.
- **Budget your probes.** Every health check is a real request against
  the same daily allowance your agent uses.
- **Quality varies.** Use free models for grunt work (search, scripts,
  drafts, bulk edits) and review their output before trusting it.

## Files

- `models.json` - Pi model entries for the free roster
- `settings.json` - default model + free-only model cycling list
