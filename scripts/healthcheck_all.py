#!/usr/bin/env python3
"""Probe providers beyond OpenRouter (which scripts/healthcheck.py owns).

For every provider whose key is present in the environment, send one
tiny chat request to each of its first PROBE_PER_PROVIDER roster models
and record the outcome in data/status-<provider>.json. Providers
without a configured key, and providers that cannot be probed via API
(local / app-locked), are skipped silently - an absent status file
means "not probed", and refresh_all.py's providers.json says why.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers import PROVIDERS

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PER = int(os.environ.get("PROBE_PER_PROVIDER", "2"))


def call(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            json.load(r)
        return "ok", round(time.time() - t, 1)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read()[:300].decode(errors="replace")
        except Exception:
            detail = ""
        print(f"  probe error HTTP {e.code}: {detail}")
        return {429: "rate-limited", 404: "no-endpoint"}.get(e.code, f"http-{e.code}"), round(time.time() - t, 1)
    except Exception as e:
        return f"error: {str(e)[:80]}", round(time.time() - t, 1)


def probe(p, model, key):
    style = p["api"]["style"]
    if style == "openai":
        return call(p["api"]["base"] + "/chat/completions",
                    {"model": model, "max_tokens": 16,
                     "messages": [{"role": "user", "content": "Reply with exactly: OK"}]},
                    {"Authorization": f"Bearer {key}"})
    if style == "gemini":
        return call(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={key}",
            {"contents": [{"parts": [{"text": "Reply with exactly: OK"}]}],
             "generationConfig": {"maxOutputTokens": 16}}, {})
    if style == "cloudflare":
        # OpenAI-compatible endpoint (docs: needs only Workers AI Read).
        # The older /ai/run/{model} path 404'd with the same token, so the
        # probe uses the canonical chat-completions route instead.
        acct = os.environ[p["key_env_extra"]]
        return call(
            f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/v1/chat/completions",
            {"model": model, "max_tokens": 16,
             "messages": [{"role": "user", "content": "Reply with exactly: OK"}]},
            {"Authorization": f"Bearer {key}"})
    return None


def main():
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    for p in PROVIDERS:
        if p["id"] == "openrouter" or not p.get("api") or not p.get("key_env"):
            continue
        key = os.environ.get(p["key_env"], "").strip()
        if not key or (p["api"]["style"] == "cloudflare"
                       and not os.environ.get(p.get("key_env_extra", ""), "")):
            continue
        roster_file = DATA / f"models-{p['id']}.json"
        if not roster_file.exists():
            continue
        models = [m["id"] for m in json.loads(roster_file.read_text())["models"][:PER]]
        results = []
        for m in models:
            got = probe(p, m, key)
            if got:
                results.append({"model": m, "status": got[0], "secs": got[1]})
                print(p["id"], m, "->", got[0])
        (DATA / f"status-{p['id']}.json").write_text(json.dumps(
            {"provider": p["id"], "checked_at": stamp,
             "method": f"one tiny chat request per model, top {PER} of roster",
             "results": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
