---
gsd_state_version: 1.0
milestone: v2026.4.12
milestone_name: milestone
status: "`openclaw-ops/vps/` now ships `build-patched-openclaw.sh`, tarball patch apply, `deploy.sh --with-core --restart`; next: operator deploy + ROADMAP UAT bullets"
stopped_at: Phase 02.2 context gathered
last_updated: "2026-05-03T22:12:09.335Z"
last_activity: 2026-05-03
progress:
  total_phases: 13
  completed_phases: 5
  total_plans: 13
  completed_plans: 12
  percent: 82
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-08)

**Core value:** One inbox that cuts through noise across communication sources — triage, drafts, and approvals so nothing important is missed.
**Current focus:** Phase 02.1.2 closed — live UAT passed 2026-04-28. Discovered during close-out that the deployed binary on VPS is unmodified upstream `v2026.4.12 (1c0672b)` — UAT works because today's digest fits in one Telegram message and Bella reads it from topic conversation history. **Phase 02.1.3 planned** to port the 02.1.2 TS into upstream's `extensions/telegram` structure and ship the patch pipeline (`vps/patches/` + `build-patched-openclaw.sh`) — safety net before Backlog 999.3 broadens digest beyond 4096 chars. Three quality-of-life follow-ups captured as Backlog 999.1/999.2/999.3. Next active: 02.1.3, then 02.2 (version alignment).

## Current Position

Phase: 02.1.3 — **implementation complete** (automated gates in `02-1-3-VERIFICATION.md`; VPS live grep + >4096 UAT awaiting operator)
Plan: 02.1.3 plans 01–02 summarized (`02-1-3-01-SUMMARY.md`, `02-1-3-02-SUMMARY.md`)
Status: `openclaw-ops/vps/` now ships `build-patched-openclaw.sh`, tarball patch apply, `deploy.sh --with-core --restart`; next: operator deploy + ROADMAP UAT bullets
Last activity: 2026-05-03

Progress: [████████░░] 82%

## Accumulated Context

### Decisions

- Phase 1: Forum topics + Triage Digest delivery + DM fallback + routing contract (`01-CONTEXT.md`).
- Phase 2: Calendar-day CST window; all Hospitable guest messages in window; hybrid categorization; single primary bucket; digest shape and caps; Gmail-only draft approval; CLI + `/triage`; VPS `bin` + cron (`02-CONTEXT.md`).
- **Phase 02.1 (new, 2026-04-13):** Pivot away from the patched-openclaw-core + auto-router + draft-agent-script stack built in `02-03-PLAN.md`. Use Bella's main agent for drafting via normal topic conversation; keep only the `tdr` CLI for finalization (save / send-now / done). See `.planning/phases/02-1-triage-simplification/02-1-CONTEXT.md`.
- [Phase 02.1]: Kept triage draft state path canonical and removed OPENCLAW_TRIAGE_DRAFT_STATE override from digest generation.
- [Phase 02.1]: Accepted pre-removed Telegram auto-router/callback state and enforced via verification plus ops decommission checks.
- [Phase 02.1]: Escalate response-required subject phrases to DraftNeeded: maybe in both personal and rental review scripts.
- [Phase 02.1]: Render per-item digest tokens inline and standardize finalization hints on /bash tdr send-now <token> and /bash tdr save <token>.
- [Phase 02.1]: Use scripts/deploy/prompts/triage-draft-runbook.md as the canonical triage behavior tuning surface.
- **[Phase 02.1.1, 2026-04-23]:** Two live-UAT gaps identified after 02.1 completed: (1) Hospitable digest lines render raw Python dict repr because `sender` is a dict and `str(sender)` was used; (2) main agent has no email body context when asked to draft in-thread because digest only includes BodySummary. Decision: Option A — inline full email body as Markdown blockquote in digest for `needs_reply` items. Rejected Option B (`tdr show` subcommand) because it reintroduces soft-dependency failure class 02.1 was meant to remove.
- **[Phase 02.1.1 process lesson]:** Every plan now explicitly mirrors `openclaw/scripts/deploy/**` changes to `openclaw-ops/vps/scripts/**` and verifies live VPS deploy before completing. This closes the process gap from 02.1-02 where the ops mirror was missed and the classifier fix didn't go live.
- [Phase 02.1.1]: Hospitable digest: resolve dict sender via full_name→first_name→name helper chain; preview prefers body→preview→text; string-only coercion prevents Python dict repr leak in Telegram digest.
- [Phase 02.1]: Validated triage simplification boundary using build/tests plus VPS runtime decommission checks.
- [Phase 02-1-1-triage-digest-context-fixes]: Option A over Option B: extended review scripts to emit BodyB64 rather than adding a new bodies-snapshot file
- [Phase 02-1-1-triage-digest-context-fixes]: Single-line base64 transport for body keeps summary parser untouched and handles any email content safely
- [Phase 02-1-1-triage-digest-context-fixes]: Blockquote cap is 4000 body chars with '... (truncated)' marker; header-line affordance sits at top of '## Needs attention' when non-empty
- **[Phase 02.1.2, opened 2026-04-28]:** Live UAT showed Bella could not ground on the digest markdown already posted to the Telegram triage Forum topic (“paste or forward”). Session traces also showed failing `byterover` / `brv providers connect byterover` / empty `memory_search` in-agent. Decision: Phase 02.1.2 — inject canonical `triage-digest-latest.md` into Bella’s inbound Telegram context when routing matches the configured triage Forum thread; separately wire ByteRover auth in-container under `openclaw-ops` compose secrets + verify connect from `/data/.openclaw/workspace`.

### Blockers/Concerns

- `openclaw-ops/vps/patches/0001-telegram-triage-auto-route.patch` was not reliably staying installed across compose recreates. Rather than fix, we are removing the patch entirely under Phase 02.1.
- Triage items classified as `DraftNeeded: no` for external senders with "Response Required"-style subjects — **addressed in 02.1-02 source tree, now fixed on VPS as of 2026-04-23 mirror deploy**.
- **Plan C conversational triage:** unblocked 2026-04-28 — digest snapshot now reaches the inbound agent for the configured triage Forum topic; live UAT passed.
- **Backlog 999.1 (digest grouping/presentation), 999.2 (full-body fidelity + inline images), 999.3 (broaden inclusion vs strict response-required):** captured from 02.1.2 UAT findings; not blocking.

## Session Continuity

**Last session:** 2026-05-03T22:12:09.324Z
**Last Date:** 2026-05-03T22:12:09.324Z
**Stopped At:** Phase 02.2 context gathered
**Resume File:** .planning/phases/02-2-version-alignment-upgrade-stabilization-local-vps-mac-gui/02.2-CONTEXT.md
**Resume hint:** Run `~/openclaw-ops/vps/build-patched-openclaw.sh` → `OPENCLAW_PACK_TGZ=... ./deploy.sh --with-core --restart` → README grep smoke / large digest UAT; then `/gsd-discuss-phase 02.2` or `/gsd-review-backlog` for 999.x.
