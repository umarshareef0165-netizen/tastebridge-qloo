# TasteBridge — Qloo Agentic Evening Planner

**Qloo Agentic Hackathon, solo entry by Umar Shareef.**
**Deadline: Oct 30, 2026, 11:45pm ET.** Prizes: $25,000 (1st $15,000 / 2nd $6,000 / 3rd $4,000).
Top 3 finalists appear on air Nov 5 with the judges.

## The idea (why Qloo is the differentiator)

Generic agents guess what you want. TasteBridge **grounds** the plan in taste:
your music or film taste is the seed, and the Qloo taste graph jumps
**across domains** — jazz → an intimate live jazz room, Bollywood romance →
a melodic, romantic dinner, a dreamy indie mood → a scenic wind-down.
Without Qloo's cross-domain taste graph, this app would be a generic
keyword search. With it, the agent knows *why* a place fits *your* taste,
and shows that reason for every stop.

## How the agent works (not a single lookup)

1. **Parse** — seeds (music/film/mood), city, budget, group size from plain language.
2. **Seed** — Qloo search resolves each seed to entities.
3. **Recommend** — Qloo insights into dining + place + activity (cross-domain).
4. **Critic** — dedupe, budget filter, affinity floor, domain coverage.
   If a step finds nothing, the app says so — it never invents a pick.
5. **Plan** — an evening timeline, each stop with its taste-bridge reason
   and shared taste tags, plus a visible agent trace for judges.

## Run it (mock mode, no key needed)

```bash
cd qloo-hackathon
python3 src/server.py
# UI:      http://localhost:8001/
# Health:  http://localhost:8001/api/health
# Try: "Plan a romantic Bollywood evening in Los Angeles for 2, moderate budget"
# Try: "Jazz evening in Los Angeles, moderate budget, for 4 friends"
```

Python stdlib only — no pip install. Tests:

```bash
python3 -m unittest discover -s tests
```

## Deployment (card-free, not yet done)
See `docs/DEPLOYMENT.md`. Route: Hugging Face Spaces (Docker, free tier)
using the included `Dockerfile`; the server binds `0.0.0.0` and honours
`$PORT`. Do NOT deploy to Render — it asks for a card even on free.
Live mode is switched on only with `QLOO_MODE=live` plus a real key in
the host's secrets (never in the repo); mock is the default.

**Current build runs in MOCK mode** (labelled in the UI). The mock catalog
is a small set of well-known cultural examples so the pipeline runs
end-to-end; it is NOT presented as live Qloo data. The real adapter is in
`src/real_qloo.py` and is not wired into the server until the live-key
check in `docs/QLOO-API-KEY.md` passes. The hosted demo required by the
hackathon must be the **live** version — a local-only submission does not
qualify, so deployment is a blocking remaining step (see
`docs/SUBMISSION-CHECKLIST.md`).

## Files

- `src/agent.py` — parse → seed → recommend → critic → plan
- `src/mock_qloo.py` — deterministic mock Qloo client + catalog
- `src/real_qloo.py` — real Qloo adapter (env key only, endpoint to confirm)
- `src/server.py` — stdlib HTTP server + JSON API
- `public/index.html` — demo UI
- `tests/test_agent.py` — agent tests
- `docs/DEMO-SCRIPT.md` — ≤3-min walkthrough script (video NOT required
  by this hackathon; the required deliverable is a live hosted demo)
- `docs/DEVPOST-DRAFT.md` — draft submission text
- `docs/SUBMISSION-CHECKLIST.md` — evidence-based pre-submit checklist

## License

MIT — see `LICENSE` (must stay visible in the repo's About section).
