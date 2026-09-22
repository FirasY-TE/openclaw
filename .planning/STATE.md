---
gsd_state_version: 1.0
milestone: v2026.4.12
milestone_name: milestone
status: **`openclaw-ops`** pinned **2026.5.2** (`8b2a6e57`); VPS live CLI under **`/data/.npm-global`** when `PATH` prefers it; **`openclaw-gws-triage-reply`** escape fix deployed. Local npm + Mac Sparkle alignment **deferred** (D-09/D-10).
stopped_at: Backlog 999.5 — proactive reply approval pivot (02.3–02.5 demoted)
last_updated: "2026-07-08T04:14:00Z"
last_activity: 2026-07-07
progress:
  total_phases: 15
  completed_phases: 6
  total_plans: 17
  completed_plans: 16
  percent: 85
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-08)

**Core value:** One inbox that cuts through noise across communication sources — triage, drafts, and approvals so nothing important is missed.
**Current focus:** **Triage digest deprecated (2026-09-21)** — shut down VPS cron + snapshot patch per `TRIAGE-DEPRECATION.md`. **Backlog 999.5** — unified daily inbox (original vision). Next milestone when ready: **Phase 3 — Beeper**.

## Current Position

Phase: **Triage shutdown + backlog 999.5** (unified daily inbox). Phase 2 triage **deprecated**. Then **Phase 3 — Beeper** when promoted. **02.2** — **COMPLETE** (`02.2-UAT.md`, `02.2-VERIFICATION.md`).
Plan: 02.2 plans 01–04 executed; formal **UAT** six-for-six (`02.2-UAT.md`).
Status: **`openclaw-ops`** pinned **2026.5.2** (`8b2a6e57`); VPS live CLI under **`/data/.npm-global`** when `PATH` prefers it; **`openclaw-gws-triage-reply`** escape fix deployed. Local npm + Mac Sparkle alignment **deferred** (D-09/D-10).
Last activity: 2026-05-04

Progress: [█████████░] 85%

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
- **[Phase 02.2, closed 2026-05-04]:** VPS + `openclaw-ops` aligned to **2026.5.2** (`8b2a6e57`); document **two OpenClaw installs** in container (`/usr/local` vs `/data/.npm-global`); triage digest + `tdr` UAT in Telegram; `openclaw-gws-triage-reply` normalizes literal `\\n` from argv.
- **[2026-07-07]:** Operator pivot — end-of-day triage digest not delivering value. **999.5** backlog item opened.
- **[2026-09-21]:** **Triage digest deprecated** — drift from original vision (unified daily summary + calendar/reminder/respond actions); OpenClaw upgrade blocked by digest-snapshot patch. **999.5** reframed as unified daily inbox on morning-brief pattern (no patched core). See `TRIAGE-DEPRECATION.md`.

### Blockers/Concerns

- `openclaw-ops/vps/patches/0001-telegram-triage-auto-route.patch` was not reliably staying installed across compose recreates. Rather than fix, we are removing the patch entirely under Phase 02.1.
- Triage items classified as `DraftNeeded: no` for external senders with "Response Required"-style subjects — **addressed in 02.1-02 source tree, now fixed on VPS as of 2026-04-23 mirror deploy**.
- **Plan C conversational triage:** unblocked 2026-04-28 — digest snapshot now reaches the inbound agent for the configured triage Forum topic; live UAT passed.
- **Triage digest:** deprecated 2026-09-21 — VPS shutdown checklist in `TRIAGE-DEPRECATION.md`.
- **Backlog 999.4:** fold into **999.5** when promoted. **999.1–999.3:** obsolete with digest deprecation.

## Session Continuity

**Last session:** 2026-07-08
**Stopped At:** Triage digest deprecated — VPS shutdown + 999.5 discuss
**Resume File:** `.planning/TRIAGE-DEPRECATION.md`
**Resume hint:** (1) Disable triage cron + snapshot env on VPS (`openclaw-ops`). (2) `/gsd-discuss-phase 999.5` for unified daily inbox. (3) Delete obsolete **999.1–999.3** when ready.
