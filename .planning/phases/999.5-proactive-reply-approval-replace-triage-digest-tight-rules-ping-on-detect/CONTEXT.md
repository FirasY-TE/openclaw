# Phase 999.5 — Unified daily inbox (successor to deprecated triage digest)

**Captured:** 2026-09-21  
**Status:** Backlog — discuss before planning

## Operator intent (restored original vision)

One daily (and on-demand) view that:

1. **Summarizes all emails and messages for the day** (Gmail personal + rental, Hospitable guest messages; Beeper later) — nothing silently dropped; promos/newsletters demoted, not hidden.
2. **Highlights items of specific importance** — urgent, needs reply, needs attention, with clear rules (tight classification policy).
3. **Enables actions per item:**
   - **Calendar** — add event / appointment confirm (reuse appointment-confirm path where applicable)
   - **Reminder** — Google Task (reuse existing task lists + dedupe)
   - **Respond** — draft + explicit approve + send (`tdr` or successor; no auto-send for email)

## Constraints (learned from triage digest failure)

- **No patched OpenClaw core** for delivery UX — use vanilla upstream; prepared JSON/text files + OpenClaw cron agent composition (same pattern as morning brief).
- **Telegram is delivery**, not a full inbox UI — keep messages scannable; chunk if needed; separate Approvals topic for respond flow if needed.
- **Reuse GWS pipeline outputs** — do not re-fetch APIs at send time.
- **Start small** — one source or one mailbox first; prove classification rules before multi-source.

## Not in scope for first promote

- End-of-day batch digest markdown builder (`triage_digest_build.py`)
- Digest snapshot injection (`OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_*`)
- Token-inline `/bash tdr` discovery UX in a wall of text

## Related backlog

- **999.4** — explicit send confirmation before Gmail send
- **999.1–999.3** — obsolete (digest-only); delete when operator confirms

## Deprecation

See `.planning/TRIAGE-DEPRECATION.md` for VPS shutdown checklist.
