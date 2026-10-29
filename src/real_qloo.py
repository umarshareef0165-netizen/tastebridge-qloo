"""Real Qloo Taste AI adapter (stub wiring, env-only key).

Endpoint shape follows Qloo's public documentation pattern:
  GET  {QLOO_API_BASE}/search?query=...          -> entity resolution
  POST {QLOO_API_BASE}/v2/insights              -> recommendations, with
       body {"signal": {"interests": {"entities": [seed_ids]}}}
       and header "X-Api-Key: <key from env only>".

The exact hackathon base URL and response field names MUST be confirmed
against the starter-kit materials before a live run -- this adapter is
deliberately not imported by the server until that check passes, so the
shipped demo cannot silently present mock results as live Qloo results.

Usage:
  export QLOO_API_KEY=...            # never commit this, never paste it in chat
  export QLOO_API_BASE=https://hackathon.api.qloo.com   # confirm from starter kit
  python3 -c "from src.real_qloo import RealQlooClient; ..."
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request


class RealQlooNotConfigured(Exception):
    pass


class RealQlooClient:
    def __init__(self, api_key=None, base=None):
        self.api_key = api_key or os.environ.get("QLOO_API_KEY")
        self.base = (base or os.environ.get("QLOO_API_BASE",
                                           "https://hackathon.api.qloo.com")).rstrip("/")
        if not self.api_key:
            raise RealQlooNotConfigured(
                "QLOO_API_KEY is not set. Request a key via the starter-kit "
                "instructions, put it in .env only, and retry. No key is "
                "hard-coded anywhere in this repo.")

    def _get(self, path, params):
        url = self.base + path + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"X-Api-Key": self.api_key})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Qloo API HTTP {exc.code}: {exc.read()[:200]!r}")

    def _post(self, path, payload):
        req = urllib.request.Request(
            self.base + path, method="POST",
            data=json.dumps(payload).encode(),
            headers={"X-Api-Key": self.api_key,
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Qloo API HTTP {exc.code}: {exc.read()[:200]!r}")

    def search(self, query):
        data = self._get("/search", {"query": query})
        results = data.get("results", {}).get("entities", []) if isinstance(data, dict) else []
        return [{"id": e.get("entity_id", e.get("id")),
                 "name": e.get("name"),
                 "domain": (e.get("type") or "").replace("urn:entity:", ""),
                 "tags": [t.get("name") for t in e.get("tags", []) if t.get("name")],
                 "price_level": 2} for e in results]

    def insights(self, seed_ids, target_domain=None, limit=5):
        payload = {"signal": {"interests": {"entities": list(seed_ids)}}}
        if target_domain:
            payload["filter"] = {"type": f"urn:entity:{target_domain}"}
        data = self._post("/v2/insights", payload)
        results = data.get("results", {}).get("entities", []) if isinstance(data, dict) else []
        out = []
        for e in results[:limit]:
            out.append({"id": e.get("entity_id", e.get("id")),
                        "name": e.get("name"),
                        "domain": (e.get("type") or "").replace("urn:entity:", ""),
                        "tags": [t.get("name") for t in e.get("tags", []) if t.get("name")],
                        "price_level": 2,
                        "affinity": e.get("affinity"),
                        "shared_tags": [],
                        "bridge": "Recommended by Qloo taste graph from your seed entities"})
        return out
