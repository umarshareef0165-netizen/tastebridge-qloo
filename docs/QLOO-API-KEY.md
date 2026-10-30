# Real Qloo API key — RECEIVED 2026-10-29 22:28 PDT, stored in .env only

Status: **KEY RECEIVED 2026-10-29 22:28 PDT by email from the Qloo Hackathon
team (subject: "Your Qloo API Access for the Agentic Hackathon"). The key
value is NOT written in this doc, in chat, in memory, or in git — it lives
only in the local `.env` file (gitignored) and, once set, as a host secret
on the deployment host. Do NOT re-request.** Base URL confirmed from the
official hackathon developer guide: https://hackathon.api.qloo.com.

KNOWN LIMIT (2026-10-30, this VM): every request carrying an `X-Api-Key`
header stalls in this VM's network egress (proven: unauthenticated Qloo
calls return 401 in ~1s, while authenticated Qloo calls AND an
unrelated host with a dummy `X-Api-Key` header both time out with 0
bytes). So NO live Qloo call has completed from this VM yet, and the
key's validity is NOT yet proven from here. The first live call must
happen on the deployed host (Hugging Face Space), outside this VM's
egress. Do NOT work around the egress control by smuggling the header;
do NOT pass the key as a query parameter or Bearer token (the guide
forbids both).

Adapter correction (2026-10-30, from the official guide): `/v2/insights`
is a GET with query-string parameters (`filter.type`,
`signal.interests.entities`), NOT a POST with a JSON body. The adapter
in `src/real_qloo.py` was rewritten to match, with agent-domain mapping
dining -> place, place -> place, activity -> destination.

What the starter-kit email says (per registration context): an API key is
to be requested and a repo + harness are provided. The starter-kit
materials themselves were not available to this build, so:

1. Open the starter-kit email / harness and follow its exact key-request
   instructions (do not use a key-request form from a different Qloo
   hackathon edition — editions differ).
2. Put the key in a local `.env` file ONLY (never in chat, git, or docs):
   `QLOO_API_KEY=...` and confirm `QLOO_API_BASE` from the starter kit.
3. Run one live search + one live insights call with `src/real_qloo.py`
   and confirm the response field names match the adapter. Fix the
   adapter if they differ — do not ship a broken live claim.
4. Only then wire the real client into `src/server.py`, re-run the demo
   end-to-end, and remove the MOCK badge from the UI.
5. Deploy the live version to a public host (see SUBMISSION-CHECKLIST).
   A local-only demo does NOT qualify for this hackathon.
