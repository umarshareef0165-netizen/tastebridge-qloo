# Submission checklist — Qloo Agentic Hackathon

Deadline: **Oct 30, 2026, 11:45pm ET.** Submit well before the final hour;
after the deadline the submission locks.

- [x] Working app in mock mode, tests passing, README, MIT LICENSE
- [x] Devpost draft written (docs/DEVPOST-DRAFT.md)
- [x] Real Qloo API key requested via starter-kit instructions — DONE 2026-10-29 02:53 PDT (form: Umar Shareef, umarshareef0165@gmail.com, Devpost umarshareef0165, GitHub umarshareef0165-netizen, Pakistan, TasteBridge). Confirmation: key by email "within a few business days" — NOT the starter-kit email's usual one business day, so arrival by the Oct 30 8:45pm PT deadline is not guaranteed. No key received yet; do NOT re-request.
- [x] Real Qloo API key RECEIVED — DONE 2026-10-29 22:28 PDT (email from the Qloo Hackathon team). Stored in local `.env` ONLY (gitignored); value appears nowhere in chat, memory, docs, or git. Base URL confirmed from the official hackathon developer guide: https://hackathon.api.qloo.com.
- [ ] Live search + insights call passes; adapter field names confirmed — BLOCKED on this VM: every request carrying an `X-Api-Key` header stalls in this VM's network egress (unauthenticated calls return 401 in ~1s; authenticated calls time out with 0 bytes; same stall on an unrelated host with a dummy key header). Adapter was rewritten to the guide's GET + `filter.type` shape (see docs/QLOO-API-KEY.md); the first live call must run on the deployed host, not this VM. Key validity is therefore NOT yet proven.
- [x] Real client wired into server (QLOO_MODE=live imports RealQlooClient; fail-fast without a key); UI badge is now mode-aware (MOCK in mock mode, LIVE in live mode) — DONE 2026-10-30, local server health check reports live mode. Full live demo re-test still TODO, pending the deployed host's first live call.
- [ ] App deployed to a public host; demo URL tried end-to-end by a second person — TODO
      (local-only / private-access submissions do NOT qualify)
      Route: Hugging Face Spaces (Docker, free, NO card) — see
      docs/DEPLOYMENT.md. Do NOT use Render (it asks for a card even
      on the free plan). If any host asks for a card, STOP and report.
- [x] Public repo pushed; LICENSE visible in repo About — DONE 2026-10-29 (https://github.com/umarshareef0165-netizen/tastebridge-qloo, 9 files, 5 commits, no .env / key pushed)
- [ ] Devpost description finalised with the REAL demo URL and repo URL — TODO
- [ ] Final approval from Umar Shareef, then Devpost submit — TODO

Do NOT tick a box from memory. Every box needs a link, file, or live
result actually seen. Do NOT invent a key, demo URL, repo URL, or video link.
