#!/usr/bin/env python3
"""Refresh rosters for every provider in scripts/providers.py.

Per provider:
  - If it has a live list API *and* its key is in the environment,
    fetch the real catalog (source: "api").
  - Else, if it has seed models, write them out labeled
    (source: "seed") - a curated starting list, not live data.
  - OpenRouter is skipped here: scripts/refresh.py owns it.

Also (re)writes data/providers.json, the index consumed by the
README table and the status website: per provider, the roster mode,
model count, and whether a probe key is configured.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers import PROVIDERS

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def http_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_api_roster(p):
    style = p["api"]["style"]
    key = os.environ[p["key_env"]]
    if style == "openai":
        data = http_json(p["api"]["base"] + "/models",
                         {"Authorization": f"Bearer {key}"})
        return [m["id"] for m in data.get("data", [])]
    if style == "gemini":
        data = http_json(
            "https://generativelanguage.googleapis.com/v1beta/models"
            f"?key={key}&pageSize=1000")
        return [m["name"].replace("models/", "")
                for m in data.get("models", [])
                if "generateContent" in (m.get("supportedGenerationMethods") or [])]
    if style == "cloudflare":
        acct = os.environ[p["key_env_extra"]]
        data = http_json(
            f"https://api.cloudflare.com/client/v4/accounts/{acct}"
            "/ai/models/search?per_page=100",
            {"Authorization": f"Bearer {key}"})
        return [m["name"] for m in data.get("result", [])]
    if style == "ollama":
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        data = http_json(host.rstrip("/") + "/api/tags")
        return [m["name"] for m in data.get("models", [])]
    return None


def main():
    DATA.mkdir(exist_ok=True)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    index = []
    for p in PROVIDERS:
        if p["id"] == "openrouter":
            roster = json.loads((DATA / "free-models.json").read_text())
            index.append({"id": p["id"], "name": p["name"], "kind": p["kind"],
                          "limits": p["limits"], "signup": p["signup"],
                          "roster_source": "api", "model_count": roster["count"],
                          "key_env": p["key_env"],
                          "key_configured": bool(os.environ.get(p["key_env"]))})
            continue

        models, source = None, None
        api = p.get("api")
        can_api = api and (
            (api["style"] == "ollama" and os.environ.get("OLLAMA_HOST")) or
            (p.get("key_env") and os.environ.get(p["key_env"]) and
             (api["style"] != "cloudflare" or os.environ.get(p.get("key_env_extra", "")))))
        if can_api:
            try:
                models, source = fetch_api_roster(p), "api"
            except urllib.error.HTTPError as e:
                # Log the provider's error code/message (never a token)
                # so a 404 vs 403 can be told apart in CI logs.
                try:
                    detail = e.read()[:300].decode(errors="replace")
                except Exception:
                    detail = ""
                print(f"{p['id']}: live fetch failed (HTTP {e.code}); "
                      f"body={detail}; falling back to seed")
            except Exception as e:
                print(f"{p['id']}: live fetch failed ({e}); falling back to seed")
        if models is None and p.get("seed_models"):
            models, source = list(p["seed_models"]), "seed"

        payload = {"provider": p["id"], "refreshed_at": stamp,
                   "source": source, "count": len(models or []),
                   "models": [{"id": m} for m in (models or [])]}
        (DATA / f"models-{p['id']}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False))
        index.append({"id": p["id"], "name": p["name"], "kind": p["kind"],
                      "limits": p["limits"], "signup": p["signup"],
                      "roster_source": source,
                      "model_count": len(models or []),
                      "key_env": p.get("key_env"),
                      "key_configured": bool(p.get("key_env") and os.environ.get(p["key_env"])),
                      "note": p.get("note")})
        print(f"{p['id']}: source={source} models={len(models or [])}")

    (DATA / "providers.json").write_text(json.dumps(
        {"refreshed_at": stamp, "providers": index}, indent=2, ensure_ascii=False))
    print("providers.json written:", len(index), "providers")


if __name__ == "__main__":
    main()
