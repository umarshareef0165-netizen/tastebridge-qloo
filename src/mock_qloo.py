"""Mock Qloo Taste AI client.

MOCK DATA ONLY. These entities are well-known cultural examples used so the
demo runs end-to-end without an API key. Nothing here claims to be a live
Qloo result. Swap in RealQlooClient (real_qloo.py) for live results.

Mock model mirrors the real Qloo shape documented in public Qloo write-ups:
  search(query) -> entities with an id, name, domain and tags
  insights(seed_entity_ids, target_domain) -> ranked entities with an
  affinity score and a taste-bridge reason (the cross-domain jump).
"""

# (entity_id, name, domain, tags, price_level 1-3)
CATALOG = [
    # Music seeds
    ("urn:entity:artist:jazz-coltrane", "John Coltrane", "music",
     ["jazz", "improvisation", "warm", "classic"], 1),
    ("urn:entity:artist:lofi-girl", "lofi girl", "music",
     ["lofi", "chill", "study", "mellow"], 1),
    ("urn:entity:artist:bollywood-arijit", "Arijit Singh", "music",
     ["bollywood", "romantic", "emotional", "melodic"], 1),
    ("urn:entity:artist:indie-tame", "Tame Impala", "music",
     ["indie", "psychedelic", "dreamy", "adventurous"], 1),
    ("urn:entity:artist:rock-queen", "Queen", "music",
     ["rock", "anthemic", "energetic", "classic"], 1),
    # Film seeds
    ("urn:entity:film:wes-anderson", "The Grand Budapest Hotel", "film",
     ["quirky", "whimsical", "visual", "charming"], 1),
    ("urn:entity:film:spirited-away", "Spirited Away", "film",
     ["whimsical", "dreamy", "adventurous", "emotional"], 1),
    ("urn:entity:film:interstellar", "Interstellar", "film",
     ["sci-fi", "epic", "emotional", "adventurous"], 1),
    ("urn:entity:film:la-la-land", "La La Land", "film",
     ["romantic", "musical", "dreamy", "la"], 1),
    # Dining / places (cross-domain targets)
    ("urn:entity:place:jazz-bar-la", "Blue Whale Jazz Bar, Los Angeles", "dining",
     ["jazz", "warm", "intimate", "live-music"], 2),
    ("urn:entity:place:cozy-cafe-la", "Intelligentsia Coffee, Los Angeles", "dining",
     ["chill", "mellow", "study", "cozy"], 1),
    ("urn:entity:place:desi-kitchen-la", "Badmaash Gastropub, Los Angeles", "dining",
     ["bollywood", "spicy", "lively", "melodic"], 2),
    ("urn:entity:place:osteria-la", "Osteria La Buca, Los Angeles", "dining",
     ["romantic", "melodic", "cozy", "intimate"], 2),
    ("urn:entity:place:rooftop-la", "Perch Rooftop, Los Angeles", "dining",
     ["romantic", "dreamy", "scenic", "la"], 3),
    ("urn:entity:place:quirky-diner-la", "The Original Pantry Cafe, Los Angeles", "dining",
     ["quirky", "classic", "charming", "casual"], 1),
    ("urn:entity:place:adventure-park-la", "Griffith Observatory, Los Angeles", "place",
     ["adventurous", "epic", "scenic", "dreamy"], 1),
    ("urn:entity:place:art-walk-la", "The Getty Center, Los Angeles", "place",
     ["visual", "charming", "whimsical", "scenic"], 1),
    ("urn:entity:place:rock-venue-la", "The Wiltern, Los Angeles", "place",
     ["rock", "energetic", "anthemic", "live-music"], 2),
    # Activities (evening plan slots)
    ("urn:entity:activity:night-walk", "Sunset walk at Griffith Park", "activity",
     ["chill", "scenic", "romantic", "dreamy"], 1),
    ("urn:entity:activity:vinyl-night", "Vinyl listening night at home", "activity",
     ["jazz", "warm", "mellow", "intimate"], 1),
    ("urn:entity:activity:movie-night", "Outdoor movie night", "activity",
     ["film", "romantic", "whimsical", "charming"], 1),
]

# Seed taste -> target taste bridge (the "why" a generic LLM cannot invent:
# it is the graph jump, not a keyword guess).
BRIDGE = {
    "jazz": "Jazz listeners cluster around warm, intimate live rooms",
    "lofi": "Lofi listeners cluster around calm, cozy, low-stimulation spots",
    "bollywood": "Bollywood listeners cluster around lively, flavour-forward rooms",
    "indie": "Indie listeners cluster around dreamy, offbeat, scenic places",
    "rock": "Rock listeners cluster around high-energy live venues",
    "quirky": "Quirky-film fans cluster around visually playful, charming rooms",
    "romantic": "Romantic tastes cluster around scenic, intimate evenings",
    "adventurous": "Adventure tastes cluster around epic, open, scenic experiences",
    "dreamy": "Dreamy tastes cluster around scenic, slow, atmospheric places",
    "sci-fi": "Sci-fi fans cluster around epic, awe-inspiring viewpoints",
}


def _entity(row):
    eid, name, domain, tags, price = row
    return {"id": eid, "name": name, "domain": domain, "tags": tags,
            "price_level": price}


class MockQlooClient:
    """Deterministic stand-in for the Qloo API. No network, no key."""

    def search(self, query):
        q = query.lower()
        out = []
        for row in CATALOG:
            hay = " ".join([row[1], row[2]] + row[3]).lower()
            if any(word in hay for word in q.split() if len(word) > 2):
                out.append(_entity(row))
        return out

    def insights(self, seed_ids, target_domain=None, limit=5):
        seeds = [r for r in CATALOG if r[0] in seed_ids]
        seed_tags = set()
        for s in seeds:
            seed_tags.update(s[3])
        scored = []
        for row in CATALOG:
            if row[0] in seed_ids:
                continue
            if target_domain and row[2] != target_domain:
                continue
            shared = seed_tags.intersection(row[3])
            if not shared:
                continue
            bridge = sorted(shared)[0]
            scored.append({
                **_entity(row),
                "affinity": round(0.55 + 0.09 * len(shared), 2),
                "shared_tags": sorted(shared),
                "bridge": BRIDGE.get(bridge, f"Shares taste tags: {', '.join(sorted(shared))}"),
            })
        scored.sort(key=lambda e: -e["affinity"])
        return scored[:limit]
