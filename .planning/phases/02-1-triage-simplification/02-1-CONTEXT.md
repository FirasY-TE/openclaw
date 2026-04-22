# Phase 02.1 — Triage Simplification (Plan C)

**Inserted:** 2026-04-13 after Phase 02 testing surfaced architectural issues
**Goal:** Strip the triage draft loop down to Bella's main agent + a lightweight finalization CLI. Remove the patched-openclaw-core + auto-router + draft-agent-script + token-state stack built in `02-03-PLAN.md` — it's high-complexity, high-maintenance, and a test session proved the simpler path works better.

---

## Why we're pivoting

Phase 02 (specifically `02-03-PLAN.md`) built an agent-powered draft loop with:

- A patched fork of the `openclaw` npm package adding a `maybeRouteTriageDraftFeedback` hook in `extensions/telegram/src/bot-handlers.runtime.ts`
- A new `src/telegram/triage-draft-auto-route.ts` helper (parse target, match topic, read active token, exec script)
- A `openclaw-gws-triage-draft-agent` bash wrapper that holds email context, renders inline buttons, persists `lastDraftText` / `lastActive` in JSON state, and runs `openclaw agent` per turn
- Custom `tgd:*` callback_data for buttons (no handler in vanilla openclaw — buttons tap-but-do-nothing)

Testing over several sessions hit, in order:

1. Agent stored in DM instead of triage topic → fixed via `ROUTE_TRIAGE_DIGEST_TARGET`
2. Agent lost draft across turns → fixed via state persistence
3. Agent asked a question in the draft body → fixed via prompt hardening
4. "Send Now" silently created a draft, didn't send → fixed `drafts.send` body shape
5. Sent email had no `To:` header → fixed `build_reply_raw`
6. Typed feedback bypassed agent entirely → built the auto-router to catch it
7. Agent hit `plan-only` loop on revision → diagnosed as stale session id; fix = fresh session per call

**Final test (2026-04-13, 01:49 AM):** user typed a free-text edit in the triage topic. A clean, useful draft came back in the topic. Good outcome — but `grep` of the running container confirmed **the patched openclaw core isn't actually installed**. The reply came from Bella's vanilla main agent reading the thread context, not the auto-router → draft-agent pipeline.

Implication: the entire custom stack was fighting to replicate what the main agent does natively. The patch we thought was deployed last session got reverted (likely by a compose recreate or npm install during the deploy script), and we never noticed because the vanilla agent was picking up the slack.

---

## What changes (Plan C scope)

### Remove

- `src/telegram/triage-draft-auto-route.ts` and `src/telegram/triage-draft-callback.ts` (and their `.test.ts`)
- The `maybeRouteTriageDraftFeedback` hook in `src/telegram/bot-handlers.ts`
- `scripts/deploy/openclaw-gws-triage-draft-agent` and the `tdr-agent` shim
- Patched-openclaw workflow: `openclaw-ops/vps/build-patched-openclaw.sh`, `openclaw-ops/vps/patches/0001-telegram-triage-auto-route.patch`, `.openclaw-version` pin, `deploy.sh --with-core` path
- Custom `tgd:*` callback buttons from `scripts/deploy/lib/triage_digest_build.py build_draft_buttons_and_state` (keep token minting, drop inline keyboard)
- Container env vars: `OPENCLAW_TRIAGE_TG_TARGET`, `OPENCLAW_TRIAGE_DRAFT_AGENT_SCRIPT`, `OPENCLAW_TRIAGE_DRAFT_STATE`
- `lastActive` / `lastDraftText` fields in `triage-draft-tokens.json` schema (keep token → gmail metadata mapping for the CLI)

### Keep

- `openclaw-gws-triage-digest` + cron — produces the digest
- `triage_digest_build.py` — minus the buttons and `lastActive` concerns
- `openclaw-gws-review-test` / `openclaw-gws-review-rental-test` — including today's body-summary extraction
- `bodySummary` rendering under each "needs reply" bullet (already deployed, working)
- `openclaw-gws-triage-reply` (`tdr` CLI) — this is the finalization surface: `save`, `send-now`
- `triage-draft-tokens.json` — token → {gmailMessageId, account, threadId, subject, sender, date, bodySummary} mapping

### Add

- **Per-bullet token visibility.** Each "needs reply" item renders with its token inline so you (or the main agent) can act: `` `[personal] Subject — sender (token: 3eb07e41f08d)` `` or similar. No buttons.
- **Footer hint** per draftable item: `_Reply in this topic to iterate with Bella; when ready: `/bash tdr send-now <token>`or`/bash tdr save <token>`._`
- **Main agent awareness.** Minor: ensure `tools.elevated.allowFrom.telegram` in `openclaw.json` lists the triage group so Bella can invoke shell/tdr when the operator asks "send the draft."

---

## Fix backlog (carried from Phase 02 discussion)

Ranked for Phase 02.1 planning. Each is a candidate plan under this phase.

### High priority (fold into Phase 02.1 scope)

1. **Rule-based classifier miss for "Response Required" subjects.** `openclaw-gws-review-test` / `-rental-test` don't escalate `DraftNeeded: maybe` for external senders with subjects like "Response Required", "Please reply", "Let me know", "Please advise". Result: legit reply-needed emails land as `DraftNeeded: no` and never appear in the "Needs reply" bucket. Fix = add a subject-keyword escalation clause. ~10 lines per script.
2. **Button removal & finalization vocabulary.** Core of Plan C. Drop inline-keyboard rendering from digest + agent paths; keep `tdr send-now / save / done` as shell-text commands.
3. **Runbook prompt file** (Apple-Tools lesson). Single `openclaw-ops/vps/prompts/triage-draft-runbook.md` that Bella reads for triage context. Locks behavior consistency; edit markdown not code when tuning.

### Medium priority (optional plans under 02.1 or defer)

4. **Tone sampling.** Before drafting, fetch 3 recent `from:me to:<recipient>` messages and include as voice samples. Biggest lever on draft quality.
5. **`done` / `dismiss` keyword.** If operator types `done` (or taps nothing for N hours), mark the item handled in `triage-draft-tokens.json` so the next digest skips it. Useful for "I already replied from my phone."
6. **YAML policy file.** Extract VIP senders, priority keywords, skip patterns from review scripts into `openclaw-ops/vps/config/triage-policy.yaml`. Lets you tune without shell edits.

### Explicitly deferred

- ~~Two-turn send-gate~~ — operator said overkill; not pursuing.
- ~~Button dispatcher registration in openclaw core~~ — buttons are being removed entirely.

---

## Decision log

- **2026-04-13 01:49 AM CT — Free-text edit test "worked" but for the wrong reason.** Vanilla openclaw produced the response; our patched core was never installed. Confirmed by `grep -rln maybeRouteTriageDraftFeedback /usr/local/lib/node_modules/openclaw/dist` returning zero matches.
- **2026-04-13 — Pivot approved.** Operator chose Plan C over re-diagnosing + re-deploying the patched core.

---

## Open questions for plan phase

1. How to surface `token` per digest item without being ugly? (Inline code span? Zero-width footer? Only in `--verbose` digest?)
2. Does `tdr save / send-now / done` need a quick confirmation message back in the topic? (Probably yes, one-line `✅ Saved draft` / `✉️ Sent to <sender>` / `☑️ Dismissed`.)
3. Does Bella need a special-cased system prompt when she detects she's in the triage topic? Or can we rely on the runbook prompt file being loaded through the normal agent workspace?
4. Tokens are random hex — durable across digest regenerations? (They need to be, for `/bash tdr send-now <token>` to survive a repeat digest run. Currently `build_draft_buttons_and_state` mints new tokens each run.)

---

## References

- Phase 02 parent: `.planning/phases/02-end-of-day-triage-on-demand-command/`
- Deployment source of truth: `~/openclaw-ops/vps/` (see `.cursor/rules/vps-ssh-openclaw.mdc`)
- Today's testing conversation: single chat thread, `85db8787-cb06-4622-8d05-19a38c0d74c2`
