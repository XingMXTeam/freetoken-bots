#!/usr/bin/env python3
"""Probe the top free models with one tiny chat call each.

A model being listed as free does not mean it answers right now: free
models sit in shared upstream pools, so 429 (rate limited) and even 404
(no endpoint) are everyday results. This script records what actually
happened, with a timestamp, into data/status.json.

Budget honesty: every probe is a real free-tier request. The default
probe set is the top 5 roster models plus the openrouter/free router,
at 16 max tokens - about 6 of the 50 daily free requests on a fresh
OpenRouter account. Set PROBE_COUNT to change the roster depth.

Needs OPENROUTER_API_KEY in the environment. Without a key it writes a
status file saying the check was skipped, and exits 0.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
API = "https://openrouter.ai/api/v1/chat/completions"
PROBE_COUNT = int(os.environ.get("PROBE_COUNT", "5"))


def probe(model, key):
    body = json.dumps({"model": model, "max_tokens": 16,
                       "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        return {"model": model, "status": "ok",
                "secs": round(time.time() - t, 1),
                "answered_by": data.get("model")}
    except urllib.error.HTTPError as e:
        status = {429: "rate-limited", 404: "no-endpoint"}.get(e.code, f"http-{e.code}")
        return {"model": model, "status": status, "secs": round(time.time() - t, 1)}
    except Exception as e:
        return {"model": model, "status": "error", "detail": str(e)[:120],
                "secs": round(time.time() - t, 1)}


def main():
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        (DATA / "status.json").write_text(json.dumps(
            {"checked_at": stamp, "skipped": "OPENROUTER_API_KEY not set",
             "results": []}, indent=2))
        print("skipped: no OPENROUTER_API_KEY")
        return 0

    roster = json.loads((DATA / "free-models.json").read_text())
    targets = [m["id"] for m in roster["models"][:PROBE_COUNT]] + ["openrouter/free"]
    results = [probe(m, key) for m in targets]
    (DATA / "status.json").write_text(json.dumps(
        {"checked_at": stamp,
         "method": f"one chat completion per model, max_tokens=16, top {PROBE_COUNT} + router",
         "results": results}, indent=2, ensure_ascii=False))
    for r in results:
        print(r["model"], "->", r["status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
