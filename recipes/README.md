# Integration recipes

One folder per product: copy-paste configuration that wires the free
models from `data/free-models.json` into that product, each verified by
actually running it. A recipe that has not been run is not published.

| Product | Status |
|---------|--------|
| [Pi coding agent](pi/) | Verified 2026-10-22 (write + bash tool tasks completed and checked) |
| Generic OpenAI-compatible clients | The `openrouter/free` router plus any `:free` model ID works anywhere an OpenRouter key is accepted |
| More agents (Claude Code, Cursor, OpenCode, ...) | Planned; pull requests with a verified run are welcome |

Two rules every recipe follows:

1. **Free-only by construction.** Configs whitelist `:free` model IDs
   so an accidental switch to the paid twin of the same model is
   impossible or at least loud.
2. **Your own key.** Recipes always use the reader's own free account.
   Never share keys, and never pool keys to serve the public - free
   tiers prohibit it and the quotas would not survive it anyway.
