#!/usr/bin/env python3
"""Provider registry for FreeToken Bots.

One entry per free (or nearly free) model source. Two roster modes:

  - "api":  fetched live from the provider when its key is present
            in the environment (refresh_all.py does this).
  - "seed": a curated list shipped in this file for providers whose
            catalog cannot be read without a key. Seeds are labeled
            as seeds in the output data - never dressed up as live.

And one probe style per provider for health checks:
  - "openai": OpenAI-compatible chat completions endpoint.
  - "gemini": Google AI Studio generateContent endpoint.
  - None:     cannot be probed via API (local runtime, app-locked
              free tier) - the reason is documented per provider.

Free-limit figures come from the maintainer's research notes
(2026-10-23); community-sourced numbers are marked as such and every
provider's limits change without notice.
"""

PROVIDERS = [
    {
        "id": "openrouter",
        "name": "OpenRouter",
        "kind": "free-tier",
        "key_env": "OPENROUTER_API_KEY",
        "limits": "50 free-model requests/day per account (free tier); models priced $0",
        "signup": "https://openrouter.ai",
        "note": "Handled by scripts/refresh.py + scripts/healthcheck.py (the original pipeline).",
        "api": None,
        "seed_models": [],
    },
    {
        "id": "gemini",
        "name": "Google Gemini (AI Studio)",
        "kind": "free-tier",
        "key_env": "GEMINI_API_KEY",
        "limits": "Free tier, no card required. Community-measured: Flash models roughly 10 RPM and up to ~1,500 requests/day depending on model. Free-tier prompts may be used by Google to improve products; a project with billing enabled loses the free tier.",
        "signup": "https://aistudio.google.com/apikey",
        "api": {"style": "gemini"},
        "seed_models": [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
        ],
    },
    {
        "id": "groq",
        "name": "Groq",
        "kind": "free-tier",
        "key_env": "GROQ_API_KEY",
        "limits": "Free tier: headline ~1,000 requests/day per model, but a ~200K tokens/day cap (community tables) makes it run dry after a few long agent turns. Best for short tasks.",
        "signup": "https://console.groq.com/keys",
        "api": {"style": "openai", "base": "https://api.groq.com/openai/v1"},
        "seed_models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3-32b",
        ],
    },
    {
        "id": "nvidia",
        "name": "NVIDIA NIM (build.nvidia.com)",
        "kind": "free-tier",
        "key_env": "NVIDIA_API_KEY",
        "limits": "Developer program free credits: community tables list ~40 RPM and up to 10,000 requests/day per model - unusually generous; verify on your own account.",
        "signup": "https://build.nvidia.com",
        "api": {"style": "openai", "base": "https://integrate.api.nvidia.com/v1"},
        "seed_models": [
            "meta/llama-3.3-70b-instruct",
            "openai/gpt-oss-120b",
            "nvidia/nemotron-3-nano-30b-a3b",
        ],
    },
    {
        "id": "cloudflare",
        "name": "Cloudflare Workers AI",
        "kind": "free-tier",
        "key_env": "CLOUDFLARE_API_TOKEN",
        "key_env_extra": "CLOUDFLARE_ACCOUNT_ID",
        "limits": "10,000 Neurons/day free - roughly 4M input tokens/day on small models; the largest renewable free token pool, but you bring your own gateway/adapter.",
        "signup": "https://dash.cloudflare.com/?to=/:account/ai",
        "api": {"style": "cloudflare"},
        "seed_models": [
            "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
            "@cf/meta/llama-3.1-8b-instruct",
            "@cf/qwen/qwen2.5-coder-32b-instruct",
            "@cf/openai/gpt-oss-120b",
        ],
    },
    {
        "id": "zhipu",
        "name": "Zhipu GLM Flash (BigModel)",
        "kind": "free-tier",
        "key_env": "ZHIPU_API_KEY",
        "limits": "Flash-series endpoints are free (rate-limited to ~1 concurrent request). Requires a real-name verified account (China).",
        "signup": "https://open.bigmodel.cn",
        "api": {"style": "openai", "base": "https://open.bigmodel.cn/api/paas/v4"},
        "seed_models": ["glm-4-flash", "glm-4.5-flash"],
    },
    {
        "id": "modelscope",
        "name": "ModelScope (魔搭)",
        "kind": "free-tier",
        "key_env": "MODELSCOPE_API_KEY",
        "limits": "Free inference API, community-reported ~2,000 calls/day. Requires Alibaba Cloud binding + real-name verification (China).",
        "signup": "https://modelscope.cn",
        "api": {"style": "openai", "base": "https://api-inference.modelscope.cn/v1"},
        "seed_models": [
            "Qwen/Qwen3-235B-A22B",
            "Qwen/Qwen3-32B",
            "deepseek-ai/DeepSeek-V3.2",
        ],
    },
    {
        "id": "siliconflow",
        "name": "SiliconFlow (硅基流动)",
        "kind": "free-tier",
        "key_env": "SILICONFLOW_API_KEY",
        "limits": "A subset of models (mostly smaller Qwen/GLM/DeepSeek distillations) is free. Requires real-name verification (China).",
        "signup": "https://cloud.siliconflow.cn",
        "api": {"style": "openai", "base": "https://api.siliconflow.cn/v1"},
        "seed_models": [
            "Qwen/Qwen2.5-7B-Instruct",
            "THUDM/glm-4-9b-chat",
            "Qwen/Qwen3-8B",
        ],
    },
    {
        "id": "mistral",
        "name": "Mistral (La Plateforme)",
        "kind": "trial-credit",
        "key_env": "MISTRAL_API_KEY",
        "limits": "Not a free tier: the Experiment plan includes monthly free credit (~$10 reported). Codestral is a strong free-ish coding option while credit lasts.",
        "signup": "https://console.mistral.ai",
        "api": {"style": "openai", "base": "https://api.mistral.ai/v1"},
        "seed_models": ["codestral-latest", "mistral-small-latest"],
    },
    {
        "id": "cerebras",
        "name": "Cerebras",
        "kind": "trial-credit",
        "key_env": "CEREBRAS_API_KEY",
        "limits": "Not a free tier: $5 trial credit, expires in 30 days, card required. Extremely fast inference while it lasts.",
        "signup": "https://cloud.cerebras.ai",
        "api": {"style": "openai", "base": "https://api.cerebras.ai/v1"},
        "seed_models": ["llama-3.3-70b", "gpt-oss-120b"],
    },
    {
        "id": "ollama",
        "name": "Ollama (local)",
        "kind": "local",
        "key_env": None,
        "limits": "Truly unlimited: runs on your own machine - no key, no quota, no data leaving the device. Quality/speed bounded by your hardware.",
        "signup": "https://ollama.com",
        "api": {"style": "ollama"},
        "seed_models": ["qwen3:8b", "qwen2.5-coder:7b", "llama3.2:3b"],
        "note": "Roster becomes real when OLLAMA_HOST is set: refresh lists the models actually installed on that machine.",
    },
    {
        "id": "opencode-zen",
        "name": "OpenCode Zen (DeepSeek free)",
        "kind": "app-locked",
        "key_env": None,
        "limits": "deepseek-v4.1-flash-free is free for a limited time but only inside the OpenCode app - direct API calls are rejected (FreeTierError). Anonymous quota is shared per IP and was exhausted in the maintainer's test.",
        "signup": "https://opencode.ai",
        "api": None,
        "seed_models": ["deepseek-v4.1-flash-free"],
        "note": "Not API-probeable by design; listed so the roster is complete and honest about it.",
    },
]
