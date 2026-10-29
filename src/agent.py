"""TasteBridge agent: prompt -> seed taste -> Qloo cross-domain plan -> critic.

Pipeline (agentic, not a single lookup):
  1. Parse: extract seed keywords, city, budget, group size, vibe.
  2. Seed: resolve seeds via Qloo search.
  3. Recommend: Qloo insights into dining + place + activity (cross-domain).
  4. Critic: dedupe, budget filter, domain coverage, minimum score.
  5. Plan: order into an evening timeline with a taste-bridge reason per stop.
If any step finds nothing, the agent says so instead of inventing a pick.
"""

import re

SEED_KEYWORDS = {
    "jazz": ["jazz", "coltrane", "swing", "blues"],
    "lofi": ["lofi", "lo-fi", "chill", "study", "calm"],
    "bollywood": ["bollywood", "arijit", "desi", "hindi"],
    "indie": ["indie", "tame impala", "psychedelic"],
    "rock": ["rock", "queen", "metal"],
    "quirky": ["quirky", "wes anderson", "whimsical"],
    "romantic": ["romantic", "date", "anniversary", "couple"],
    "adventurous": ["adventure", "adventurous", "epic", "explore"],
    "dreamy": ["dreamy", "dream", "aesthetic"],
    "sci-fi": ["sci-fi", "scifi", "interstellar", "space"],
}

CITIES = ["los angeles", "new york", "san francisco", "chicago", "london"]
BUDGETS = {"cheap": 1, "budget": 1, "low": 1, "moderate": 2, "mid": 2,
           "fancy": 3, "luxury": 3, "splurge": 3}


def parse_prompt(prompt):
    text = (prompt or "").lower()
    seeds = [k for k, words in SEED_KEYWORDS.items()
             if any(w in text for w in words)]
    city = next((c.title() for c in CITIES if c in text), "Los Angeles")
    budget = 2
    for word, level in BUDGETS.items():
        if word in text:
            budget = level
    group = 2
    m = re.search(r"(\d+)\s*(people|friends|of us)", text)
    if m:
        group = int(m.group(1))
    return {"seeds": seeds, "city": city, "budget": budget, "group": group,
            "raw": prompt or ""}


def build_plan(client, prompt):
    """Returns (plan_dict, trace_list). plan_dict['error'] set if unbuildable."""
    parsed = parse_prompt(prompt)
    trace = [f"Parsed seeds={parsed['seeds']}, city={parsed['city']}, "
             f"budget<={parsed['budget']}, group={parsed['group']}"]
    if not parsed["seeds"]:
        return {"error": ("I could not find a taste seed in that prompt. "
                           "Try naming a music style, artist, film or mood, "
                           "e.g. 'jazz evening in LA' or 'romantic Bollywood night'."),
                "parsed": parsed}, trace

    seed_entities = []
    seen_seed_ids = set()
    for seed in parsed["seeds"]:
        found = client.search(seed)
        trace.append(f"Qloo search '{seed}' -> {len(found)} entities")
        for entity in found[:2]:
            if entity["id"] not in seen_seed_ids:
                seen_seed_ids.add(entity["id"])
                seed_entities.append(entity)
    if not seed_entities:
        return {"error": "Qloo search returned no seed entities for those tastes.",
                "parsed": parsed}, trace
    seed_ids = [e["id"] for e in seed_entities]

    picks = []
    for domain in ("dining", "place", "activity"):
        recs = client.insights(seed_ids, target_domain=domain, limit=5)
        trace.append(f"Qloo insights -> {domain}: {len(recs)} candidates")
        for rec in recs:
            # Critic: budget filter, dedupe, affinity floor.
            if rec.get("price_level", 2) > parsed["budget"]:
                continue
            if rec.get("affinity") is not None and rec["affinity"] < 0.55:
                continue
            if any(p["id"] == rec["id"] for p in picks):
                continue
            picks.append(rec)
            break
    if not picks:
        return {"error": ("No recommendations passed the critic checks "
                           "(budget / diversity / affinity). Try a higher "
                           "budget or a different taste seed."),
                "parsed": parsed, "seeds": seed_entities}, trace

    timeline = ["6:00 PM — Meet & warm up", "7:30 PM — Main stop",
                "9:30 PM — Wind down"]
    stops = []
    for slot, pick in zip(timeline, picks):
        stops.append({"time": slot, "name": pick["name"],
                      "domain": pick["domain"],
                      "why": pick.get("bridge", "Taste-graph match"),
                      "shared_tags": pick.get("shared_tags", []),
                      "affinity": pick.get("affinity")})
    return {"parsed": parsed,
            "seeds": [{"name": e["name"], "domain": e["domain"]}
                      for e in seed_entities],
            "stops": stops,
            "mode": "mock" if type(client).__name__ == "MockQlooClient" else "live",
            }, trace
