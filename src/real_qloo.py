"""Real Qloo Taste AI adapter (env-only key).

Endpoint shape follows the official Qloo Agentic Hackathon Developer Guide
(docs.qloo.com, "Qloo Agentic Hackathon Developer Guide"):
  GET  {QLOO_API_BASE}/search?query=...          -> entity resolution
  GET  {QLOO_API_BASE}/v2/insights               -> recommendations
       query params: filter.type=<urn:entity:...> (REQUIRED),
       signal.interests.entities=<comma-joined seed entity ids>

IMPORTANT, corrected 2026-10-30 after reading that guide:
  - /v2/insights is a GET with query-string parameters, NOT a POST with a
    JSON body. A POST with a JSON body fails even with valid parameters.
  - filter.type accepts only documented entity categories (artist, book,
    brand, destination, movie, person, place, podcast, tv_show,
    video_game). There is no "dining" or "activity" filter.type, so the
    agent's plan domains are mapped here: dining -> place, place ->
    place, activity -> destination. Do NOT use /recommendations or /recs
    (legacy, unsupported for the hackathon).
  - Key header is "X-Api-Key". Never a query parameter, never Bearer.
  - Hackathon keys work ONLY against https://hackathon.api.qloo.com.

The key lives in .env ONLY (see .env.example). No key is hard-coded
anywhere in this repo. This adapter is imported by the server only when
QLOO_MODE=live, so the shipped demo cannot silently present mock
results as live Qloo results.

Usage:
  export QLOO_API_KEY=<redacted>
  export QLOO_API_BASE=https://hackathon.api.qloo.com
  python3 -c "from src.real_qloo import RealQlooClient; ..."
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request


class RealQlooNotConfigured(Exception):
    pass


# Agent plan domains -> documented Qloo filter.type values.
DOMAIN_TO_FILTER_TYPE = {
    "dining": "urn:entity:place",
    "place": "urn:entity:place",
    "activity": "urn:entity:destination",
    "music": "urn:entity:artist",
    "film": "urn:entity:movie",
}


def _entity_domain(raw_type):
    return (raw_type or "").replace("urn:entity:", "")


def _tags_of(entity):
    tags = entity.get("tags", []) or []
    out = []
    for tag in tags:
        if isinstance(tag, dict):
            name = tag.get("name")
        else:
            name = tag
        if name:
            out.append(name)
    return out


def _price_level_of(entity):
    """Best-effort price level 1-3; 2 when the entity carries no price.

    Qloo place entities may carry price info in properties; when absent
    we default to 2 (moderate) so the critic's budget filter does not
    drop every unknown-price pick, and document that fallback here.
    """
    props = entity.get("properties", {}) or {}
    for key in ("price_level", "price", "priceLevel"):
        value = props.get(key)
        if isinstance(value, int) and 1 <= value <= 3:
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.isdigit() and 1 <= int(stripped) <= 3:
                return int(stripped)
            if stripped:
                dollars = stripped.count("$")
                if 1 <= dollars <= 3:
                    return dollars
    return 2


def _entities_of(data):
    """Tolerant extraction: results.entities list, or a bare list."""
    if isinstance(data, dict):
        results = data.get("results", {})
        if isinstance(results, dict):
            return results.get("entities", []) or []
        if isinstance(results, list):
            return results
        return []
    if isinstance(data, list):
        return data
    return []


class RealQlooClient:
    def __init__(self, api_key=None, base=None):
        self.api_key = api_key or os.environ.get("QLOO_API_KEY")
        self.base = (base or os.environ.get("QLOO_API_BASE",
                                           "https://hackathon.api.qloo.com")).rstrip("/")
        if not self.api_key:
            raise RealQlooNotConfigured(
                "QLOO_API_KEY is not set. Put the key in .env only, "
                "and retry. No key is hard-coded anywhere in this repo.")

    def _get(self, path, params):
        url = self.base + path + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"X-Api-Key": self.api_key})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Qloo API HTTP {exc.code}: {exc.read()[:200]!r}")

    def search(self, query):
        data = self._get("/search", {"query": query})
        return [{"id": e.get("entity_id", e.get("id")),
                 "name": e.get("name"),
                 "domain": _entity_domain(e.get("type")),
                 "tags": _tags_of(e),
                 "price_level": _price_level_of(e)}
                for e in _entities_of(data)]

    def insights(self, seed_ids, target_domain=None, limit=5):
        filter_type = DOMAIN_TO_FILTER_TYPE.get(
            target_domain, target_domain or "urn:entity:place")
        if not filter_type.startswith("urn:entity:"):
            filter_type = f"urn:entity:{filter_type}"
        params = {"filter.type": filter_type}
        if seed_ids:
            params["signal.interests.entities"] = ",".join(seed_ids)
        data = self._get("/v2/insights", params)
        out = []
        for e in _entities_of(data)[:limit]:
            out.append({"id": e.get("entity_id", e.get("id")),
                        "name": e.get("name"),
                        "domain": _entity_domain(e.get("type")),
                        "tags": _tags_of(e),
                        "price_level": _price_level_of(e),
                        "affinity": e.get("affinity"),
                        "shared_tags": [],
                        "bridge": "Recommended by Qloo taste graph from your seed entities"})
        return out
