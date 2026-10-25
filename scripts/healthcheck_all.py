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
        # 120s: free tiers queue hard - Gemini Flash probes measured
        # 35-55s for a 16-token reply, so 60s produced false timeouts.
        with urllib.request.urlopen(req, timeout=120) as r:
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
        all_models = [m["id"] for m in json.loads(roster_file.read_text())["models"]]
        if p["id"] == "cloudflare":
            # The catalog mixes chat, embedding, image and audio models;
            # only chat-capable ones answer a chat probe.
            chat = [m for m in all_models if "instruct" in m or "gpt-oss" in m]
            models = (chat or all_models)[:PER]
        elif p["id"] == "gemini":
            # The live catalog leads with legacy models that are closed
            # to new users (gemini-2.5-flash returns 404 on generateContent
            # for new accounts) and mixes in TTS/image/live variants plus
            # codename previews (gemini-4-argon answers 403). Probe only
            # mainstream numbered chat models, newest version first.
            import re

            pat = re.compile(r"^gemini-(\d+)(?:\.(\d+))?-(flash|pro)(-lite)?$")

            def keyf(m):
                mm = pat.match(m)
                ver = (int(mm.group(1)), int(mm.group(2) or 0))
                return (ver, 0 if mm.group(4) else 1)

            chat = [m for m in all_models if pat.match(m)]
            chat.sort(key=keyf, reverse=True)
            # Free-tier Gemini can leave a model unresponsive for minutes
            # (gemini-3.7-flash timed out at both 60s and 120s while
            # 3.8-flash answered). Keep the full candidate list: probing
            # below walks it until PER models answer, max 4 probed, and
            # records every attempt - a timeout stays visible, it is
            # not silently skipped.
            models = chat or all_models[:PER]
        else:
            models = all_models[:PER]
        results = []
        ok_count = 0
        for m in models:
            if p["id"] == "gemini" and (ok_count >= PER or len(results) >= 4):
                break
            got = probe(p, m, key)
            if got:
                results.append({"model": m, "status": got[0], "secs": got[1]})
                print(p["id"], m, "->", got[0])
                if got[0] == "ok":
                    ok_count += 1
        method = (f"one tiny chat request per model, top {PER} of roster"
                  if p["id"] != "gemini" else
                  f"newest mainstream models first, until {PER} answer "
                  "(max 4 probed, all attempts recorded)")
        (DATA / f"status-{p['id']}.json").write_text(json.dumps(
            {"provider": p["id"], "checked_at": stamp,
             "method": method,
             "results": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
