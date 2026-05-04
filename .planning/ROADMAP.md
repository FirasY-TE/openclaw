# Roadmap — OpenClaw Personal AI System Phase 4+

## Milestone 1: Unified Inbox & Proactive Agent

### Phase 1: Telegram Forum Topics + Channel Architecture

**Goal:** Stand up Telegram Forum Topics and migrate all delivery to topic-based routing so every subsequent feature has a clean, separated delivery surface.

**Requirements:**

- Create Telegram Forum group with distinct topics (Urgent, Triage Digest, Beeper, Hospitable, System/Auth)
- Migrate morning brief delivery from DM to appropriate topic
- Migrate auth health alerts to System/Auth topic
- Build topic-routing utility that all agents/scripts can call
- Keep DM as fallback for real-time urgent alerts or when Forum delivery fails
- Document topic IDs and routing rules for future phases

**Success criteria:**

- Morning brief and auth alerts delivered to Forum Topics (not DM)
- Topic routing callable from existing cron scripts and future agents
- DM fallback works if Forum delivery fails

**UAT:**

- [ ] Forum group exists with all defined topics
- [ ] Morning brief arrives in correct topic
- [ ] Auth alert arrives in System/Auth topic
- [ ] DM fallback tested by simulating Forum delivery failure

**Plans:** 2 plans
Plans:

- [ ] `01-01-PLAN.md` - Establish canonical topic route contract and fallback delivery wrapper
- [ ] `01-02-PLAN.md` - Migrate auth/digest routing and publish operator migration plus UAT runbooks

---

### Phase 2: End-of-Day Triage + On-Demand Command

**Goal:** Daily 4:30 PM CST triage digest covering Gmail + Hospitable guest messages, with categorization, draft-response offers, and an on-demand `/triage` command.

**Requirements:**

- Triage engine that pulls day's Gmail (personal + rental) and Hospitable guest messages
- Categorize each item: urgent / needs attention / needs reply
- Format digest and deliver to Triage Digest topic
- For "needs reply" items, offer to draft a response (trigger approval flow)
- Cron job at 4:30 PM CST (22:30 UTC)
- On-demand command (e.g. `openclaw triage` or Telegram `/triage`)
- Beeper messages added to triage in Phase 3

**Success criteria:**

- Digest delivered daily at 4:30 PM CST with categorized items
- On-demand triage produces same output
- Draft-response offers work for email items via Telegram approval buttons

**UAT:**

- [ ] Cron fires at 4:30 PM CST and digest lands in Triage topic
- [ ] On-demand triage covers same data sources
- [ ] Each item visibly categorized as urgent / attention / reply
- [ ] "Draft response" button triggers reply generation for an email item
- [ ] Approval/edit/send flow works end-to-end for email reply

**Plans:** 1/2 plans executed
Plans:

- [x] `02-01-PLAN.md` — Triage digest bin script, pytest fixtures, architecture doc update
- [x] `02-02-PLAN.md` — Host cron + runbooks, `openclaw triage` CLI, Telegram `/triage`, Gmail draft callbacks
- [~] `02-03-PLAN.md` — Interactive agent-powered draft loop (**superseded by Phase 02.1 — Plan C pivot**)

---

### Phase 02.1: Triage Simplification (Plan C pivot)

**Goal:** Pivot from the patched-openclaw-core + auto-router + draft-agent-script stack built in `02-03-PLAN.md` to a simpler architecture where Bella's main agent handles drafting via normal topic conversation and a lightweight `tdr` CLI handles finalization.

**Why:** A 2026-04-13 test session revealed the patched core wasn't reliably staying installed, and Bella's vanilla main agent was (unknowingly) picking up the slack to produce usable drafts anyway. Simpler is better. Full rationale in `02-1-CONTEXT.md`.

**Requirements:**

- Remove the custom auto-router + draft-agent stack (4+ files, patched core, custom env vars)
- Keep the digest pipeline + body-summary extraction + `tdr` finalization CLI
- Render each "needs reply" item with its token visible so the operator / main agent can invoke `/bash tdr send-now <token>`
- Fold in the rule-based classifier fix for "Response Required" subjects (currently slip through as `DraftNeeded: no`)
- Add a runbook prompt file so triage behavior is tuned via markdown, not bash

**Success criteria:**

- Patched openclaw workflow retired; running vanilla upstream openclaw in the container
- Digest renders with tokens inline (no buttons) and finalization works via `tdr` commands
- "Response Required"-type emails land in the needs-reply bucket with a token
- Operator can iterate on drafts by replying in-thread; Bella produces useful text

**UAT:**

- [ ] Digest cron produces a digest with zero inline buttons and per-item tokens
- [ ] Operator replies conversationally in topic → Bella produces a usable draft response
- [ ] `/bash tdr send-now <token>` actually sends email (has `To:` header)
- [ ] Rule-based classifier escalates "Response Required" subjects into needs-reply
- [ ] Container has no `OPENCLAW_TRIAGE_DRAFT_*` env vars, no `openclaw-gws-triage-draft-agent` script, no patched core tarball

**Plans:** 2 plans

Plans:

- [x] `02-1-01-PLAN.md` — Remove triage auto-router/callback stack and preserve digest + `tdr` finalization baseline
- [x] `02-1-02-PLAN.md` — Add classifier/token/runbook simplification layer and patched-core retirement checks

---

### Phase 02.1.1: Triage Digest Context & Rendering Fixes (Plan C gap closure)

**Goal:** Close the two live-UAT gaps from Phase 02.1 that prevent the simplified Plan C flow from actually working: (1) Hospitable digest lines leak raw Python dict repr, and (2) the main agent has no email body context when asked to draft in-thread.

**Why:** Phase 02.1 passed automated verification but failed live operator testing on 2026-04-23. Bella correctly responded _"I can draft it, but I don't actually see the email content in this thread"_ because the digest only surfaces a truncated BodySummary. Decision locked 2026-04-23: inline the full email body in the digest (Option A) rather than add a `tdr show` subcommand (Option B), because Option A eliminates the soft-dependency failure class that 02.1 was created to remove.

**Requirements:**

- Hospitable digest lines render a readable guest name + preview (never raw Python dict repr)
- Needs-reply digest items include the full email body inline as a Markdown blockquote beneath summary + token + finalize lines
- Main agent, when asked to draft in-thread, has all context in the thread (no external fetch, no `tdr show`, no paste)
- Digest includes a single italic header-line affordance at the top of the Needs-attention section listing the operator verbs Bella recognizes in-thread (`draft <name>`, `ignore <name>`, `summary`) — text only, never a callback/button, never per-item
- Every plan mirrors changes into `openclaw-ops/vps/scripts/` and verifies live VPS behavior before completing — closing the ops-mirror process gap from Phase 02.1-02

**Success criteria:**

- Telegram digest contains zero `{'` substrings in Hospitable section
- Needs-reply Gmail items show a `> `-prefixed blockquote with real email body in the digest
- Operator can ask Bella to draft in-thread and get usable text with no "I don't see the email" responses
- Source tree (`openclaw/scripts/deploy/`) and ops tree (`openclaw-ops/vps/scripts/`) are byte-identical for changed files after each plan

**UAT:**

- [ ] Digest renders `[Hospitable] Jaclyn Yacoub (res ...): <preview>` style, never a raw dict repr
- [ ] A real "Response Required" test email produces a digest with a Markdown blockquote containing the full email body
- [ ] Digest includes exactly one italic line at the top of Needs-attention listing `draft <name>`, `ignore <name>`, `summary` verbs
- [ ] Operator asks Bella to draft in-thread; Bella produces a usable reply using only thread context (no paste, no tool calls)
- [ ] Operator says "ignore <name>" and Bella acknowledges without minting a draft
- [ ] `/bash tdr send-now <token>` still delivers a real email end-to-end
- [ ] `diff -q scripts/deploy/lib/triage_digest_build.py ../openclaw-ops/vps/scripts/lib/triage_digest_build.py` returns empty after final plan

**Plans:** 2 plans

Plans:

- [x] `02-1-1-01-PLAN.md` — Fix Hospitable dict-leak in digest; mirror to openclaw-ops and deploy
- [x] `02-1-1-02-PLAN.md` — Inline full email body as blockquote for needs_reply items; update runbook; mirror to openclaw-ops and deploy

---

### Phase 02.1.2: Triage Topic Agent Context + ByteRover In-Container (Plan C gap closure)

**Goal:** Make Plan C end-to-end: when the operator types in the **Triage Digest** Forum topic, Bella receives the canonical digest markdown (`triage-digest-latest.md`) in her inbound agent context — not hypothetical thread scrolling she cannot access. Separately, align ByteRover / `brv` authentication so Bella’s memory tools succeed **inside `openclaw-ridl-openclaw-1`** (same cwd she uses).

**Why:** Live UAT (April 2026) showed Bella could not summarize or draft from digest content she had just posted (“paste or forward the digest”), while session traces showed fallback `byterover` / `memory_search` paths failing authentication or returning empty hits. Digest rendering from 02.1.1 is correct; consumption by the inbound agent layer was not wired.

**Requirements:**

- Configurable Telegram Forum `(chatId, topic thread id)` predicate that injects bounded digest Markdown into Bella’s inbound envelope (explicit match; no heuristic)
- Oversized snapshot truncation + clear labeling so the operator message + digest snapshot boundaries are obvious to the model
- VPS: `brv` works locally inside `openclaw-ridl-openclaw-1` (provider already on Google Gemini, `brv search` returns real results); ByteRover _cloud_ account is **optional** and only needed for push/pull sync
- Core Telegram changes follow upstream PR in `openclaw/` plus `openclaw-ops/vps/` patch/deploy for production container (per VPS rules)

**Success criteria:**

- `summary`, `draft <name>`, `ignore <name>` exercised in triage topic **without paste** — Bella cites grounded digest lines/items
- No agent-side `brv search`/memory failures during normal reply turns; the misleading `brv providers connect byterover` runbook step is removed (cloud login is optional, not required for memory)
- `pnpm build` + targeted Telegram tests pass for injection logic

**UAT:**

- [x] Digest posted to Telegram; operator sends "summary" in same topic → Bella listed Hospitable AC-thread items (Judy + Jaclyn) consistent with `/data/openclaw-gws/output/triage-digest-latest.md` without requesting paste (UAT 2026-04-28)
- [x] Operator invokes a draft for a visible needs_attention item ("draft a reply to Judy") → Bella drafted from inline body + agreed to send the reply via `tdr send-now` for the Modern Forms thread on operator request (UAT 2026-04-28)
- [x] Inside `openclaw-ridl-openclaw-1`, `brv providers` shows `Google Gemini (google)` connected and `brv search "triage digest"` returns real hits from the on-disk context tree (verified Apr 2026; cloud login intentionally skipped — optional)

**Plans:** 2 plans

Plans:

- [x] `02-1-2-01-PLAN.md` — Telegram triage topic: inject bounded `triage-digest-latest.md` into inbound agent context; tests + docs; VPS patch/deploy
- [x] `02-1-2-02-PLAN.md` — Ops: wire ByteRover / `brv` non-interactive auth in compose; verify connect + smoke in-container

---

### Phase 02.1.3: Telegram digest-snapshot upstream port + ops patch pipeline

**Goal:** Port the Phase 02.1.2 digest-snapshot TypeScript into upstream's restructured `extensions/telegram/src/` layout and stand up the `openclaw-ops/vps/patches/` + `build-patched-openclaw.sh` pipeline so the running VPS binary actually contains the snapshot-injection runtime.

**Why:** During 02.1.2 close-out (2026-04-28) we discovered the deployed binary (`v2026.4.12 / 1c0672b`) contains **none** of our 02.1.2 runtime code — upstream restructured Telegram into a workspace package and our `src/telegram/` files were silently ignored at build time. UAT passed only because today's digest is small enough (~1 KB) to fit in one Telegram message and Bella reads it from topic conversation history. `send_with_topic_fallback` doesn't chunk; at >4096 chars Telegram rejects the message and the digest **fails to send entirely** — a near-certain outcome once Backlog 999.3 (broaden inclusion) lands. The 32 KB file-snapshot path is the safety net for that.

**Requirements:**

- Snapshot module + tests rewritten for upstream `openclaw/plugin-sdk/*` imports.
- Digest-injection hook applied to upstream `extensions/telegram/src/bot-message-context.session.ts` (`buildTelegramInboundContextPayload`).
- Config schema additions re-located in upstream's split structure.
- `vps/patches/0001-telegram-triage-digest-snapshot.patch` against pinned `vps/.openclaw-version=1c0672b`.
- `vps/build-patched-openclaw.sh` (clone upstream at SHA → apply patches → `pnpm build && npm pack`).
- Optional `vps/deploy.sh --with-core` for tarball install.
- Live UAT with a forced large digest (>4096 chars) confirms Bella still grounds via the file path.

**Success criteria:**

- `grep -rl OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID /data/.npm-global/lib/node_modules/openclaw/dist/` matches at least one runtime `.js` after deploy.
- A >4096-char digest fixture produces (a) a chat message that may be summarized/truncated and (b) a Bella reply that still cites items the chat message could not include.
- `openclaw-ops` self-contained: clone, run `build-patched-openclaw.sh` on a clean machine, get the same tarball.

**UAT:**

- [x] Force-large digest fixture posted to topic 9; Bella's `summary` reply cites items only present in the file (not the truncated chat message). _(2026-05-03 — `UAT_SENTINEL_TAIL_20260503` in reply.)_
- [x] `vps/.openclaw-version` SHA bump-and-rebuild loop is repeatable from a fresh clone. _(Verified: `build-patched-openclaw.sh` + `deploy.sh --with-core`; grep smoke on `dist`.)_

**Plans:** 2 plans — wave 1 (**openclaw** patch authoring at `1c0672b` in `/tmp` clone) then wave 2 (**openclaw-ops** pipeline)

Plans:

- [x] `02-1-3-01-PLAN.md` — Port snapshot module + hook + Vitest under `extensions/telegram/src/` at SHA `1c0672b`; export checked `0001-*.patch`
- [x] `02-1-3-02-PLAN.md` — Ops: `vps/.openclaw-version`, `vps/patches/0001-telegram-triage-digest-snapshot.patch`, `build-patched-openclaw.sh`, `deploy.sh --with-core`, README grep/UAT

Artifacts: `.planning/phases/02-1-3-telegram-digest-snapshot-upstream-port/02-1-3-RESEARCH.md`, `02-1-3-VALIDATION.md`.

See `.planning/phases/02-1-3-telegram-digest-snapshot-upstream-port/02-1-3-CONTEXT.md`.

---

### Phase 02.2: Version Alignment + Upgrade Stabilization (Local + VPS + Mac GUI)

**Goal:** Align OpenClaw versions across local CLI/runtime, VPS runtime, and Mac GUI app after the 02.1 simplification rollout, with explicit health gates and rollback checkpoints.

**Why:** Keeping architecture cleanup and version upgrades as separate phases reduces debugging ambiguity and gives cleaner rollback boundaries if any regression appears.

**Requirements:**

- Upgrade local OpenClaw CLI/runtime to the target release and verify probes.
- Upgrade VPS OpenClaw runtime via `openclaw-ops` source-of-truth deploy flow (no ad-hoc VPS edits).
- Upgrade OpenClaw Mac GUI app to the same target version family and restart gateway through normal app flow.
- Capture pre/post version snapshots across local, VPS, and Mac surfaces.
- Run post-upgrade triage smoke and Phase 02.1 critical-path checks.
- Document rollback checkpoints and exact revert path for version-only rollback.

**Success criteria:**

- Local CLI/runtime, VPS runtime, and Mac GUI are on the intended target version family.
- `openclaw channels status --probe` passes on local and VPS after upgrade.
- Triage flow from topic conversation + token finalization still works end-to-end.
- No reintroduction of 02.1 retired artifacts (`OPENCLAW_TRIAGE_DRAFT_*`, draft-agent script, patched-core path).

**UAT:**

- [x] Local `openclaw --version` matches planned target. _(Deferred — align to **2026.5.2** when convenient; not blocking closure.)_
- [x] VPS `docker exec … sh -lc 'which openclaw && openclaw -v'` matches **2026.5.2** / **`8b2a6e5`** (npm-global install).
- [x] Mac GUI reports/operates on matching target version family and gateway restarts cleanly. _(Deferred per D-09/D-10 — Sparkle may trail VPS; gateway healthy.)_
- [x] Local + VPS `openclaw channels status --probe` succeed post-upgrade. _(VPS probe path exercised during rollout.)_
- [x] Manual triage run produces digest with inline tokens and no callback buttons.
- [x] `/bash tdr send-now <token>` still sends correctly for a test item.
- [x] Runtime checks show no `OPENCLAW_TRIAGE_DRAFT_*` vars and no `openclaw-gws-triage-draft-agent` binary.

_Closure **2026-05-04**: Phase goals met for **VPS + ops + triage path**; Local + Mac alignment left as non-blocking convenience (see `02.2-VERSION-TARGET.md`)._

**Plans:**

- `.planning/phases/02-2-version-alignment-upgrade-stabilization-local-vps-mac-gui/02.2-01-PLAN.md`
- `.planning/phases/02-2-version-alignment-upgrade-stabilization-local-vps-mac-gui/02.2-02-PLAN.md`
- `.planning/phases/02-2-version-alignment-upgrade-stabilization-local-vps-mac-gui/02.2-03-PLAN.md`
- `.planning/phases/02-2-version-alignment-upgrade-stabilization-local-vps-mac-gui/02.2-04-PLAN.md`

**Formal UAT record:** `.planning/phases/02-2-version-alignment-upgrade-stabilization-local-vps-mac-gui/02.2-UAT.md` (status **complete**, 2026-05-04).

---

### Phase 3: Beeper Integration

**Goal:** Fetch Beeper messages via Mac node, surface urgent items through Telegram, and enable draft/approve/send workflow with Google Tasks creation.

**Requirements:**

- Mac node Beeper message fetch (Desktop API or MCP)
- Surface urgent/important messages in Beeper topic
- Telegram draft/replace/confirm-send approval workflow (short tokens, server-side chat ID map)
- Send approved messages via Beeper Desktop API on Mac node
- Create Google Tasks from Beeper messages using existing task framework + hex fingerprint dedupe
- Add Beeper messages to triage digest (Phase 2 extension)
- Proactive surfacing of unread/unresponded Beeper items after configurable threshold

**Success criteria:**

- Beeper messages fetched and displayed in Telegram Beeper topic
- Full draft → edit → approve → send loop works via Telegram
- Tasks created from Beeper messages appear in Google Tasks with dedupe
- Triage digest includes Beeper messages

**UAT:**

- [ ] Beeper messages from Mac node appear in Beeper topic
- [ ] Draft reply shown with Replace / Confirm Send buttons
- [ ] Edited reply sent via Beeper Desktop API
- [ ] Google Task created from a Beeper message with hex fingerprint
- [ ] Triage digest includes Beeper items
- [ ] Unread Beeper item surfaced after threshold exceeded

---

### Phase 4: Hospitable Intelligence

**Goal:** Build a guest knowledge base from historical communications, enable auto-send for safe categories, approval-required responses for sensitive ones, and booking/earnings queries.

**Requirements:**

- Investigate Hospitable API message history depth
- Ingest historical guest messages into searchable knowledge base (RAG / vector DB / structured docs — approach TBD based on data volume)
- Define auto-send categories (standard check-in info, door codes, Wi-Fi, house rules)
- Define approval-required categories (complaints, refunds, policy exceptions, damage)
- Draft guest responses using knowledge base + current reservation context
- Auto-send for safe categories; route others through Telegram approval in Hospitable topic
- Surface urgent guest messages in Urgent topic
- Booking query interface: earnings (per-booking, per-period), nightly pricing, calendar availability
- Hospitable messages fully integrated into triage digest

**Success criteria:**

- Knowledge base populated and searchable
- Auto-send works for defined safe categories
- Approval workflow works for sensitive categories
- Booking/earnings queries return accurate data
- Urgent guest messages surface within minutes

**UAT:**

- [ ] Knowledge base answers a known guest FAQ correctly
- [ ] Auto-send delivers a check-in message without approval
- [ ] Complaint message routed to approval, not auto-sent
- [ ] Booking earnings query returns correct numbers vs. Hospitable dashboard
- [ ] Calendar availability query returns accurate dates
- [ ] Urgent guest message appears in Urgent topic promptly

---

### Phase 5: Orchestrator + Multi-Agent Migration

**Goal:** Extract an orchestrator pattern and migrate domain capabilities into dedicated subagents for cleaner separation, concurrent execution, and unified proactive surfacing.

**Requirements:**

- Orchestrator agent owns Telegram conversation, approval dispatch, and cross-domain coordination
- Domain subagents: Gmail Intelligence, Beeper, Hospitable, Triage
- Each subagent has isolated context and can run concurrently
- Unified proactive surfacing with configurable per-source time thresholds
- Orchestrator aggregates subagent outputs for triage digest
- Graceful degradation if a subagent fails (other domains continue)
- Migration is incremental — existing scripts continue working during transition

**Success criteria:**

- Orchestrator dispatches to subagents and aggregates results
- Subagents run concurrently without interference
- Proactive surfacing thresholds configurable per source
- Single subagent failure does not break other domains

**UAT:**

- [ ] Orchestrator dispatches triage to all subagents in parallel
- [ ] One subagent intentionally errored; others deliver normally
- [ ] Proactive threshold changed; surfacing timing adjusts accordingly
- [ ] End-to-end triage works with new architecture (same user experience)

---

## Status

| Phase  | Status                                 | Notes                                                                                                                                                                                 |
| ------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1      | Completed                              | Foundation — topic routing live                                                                                                                                                       |
| 2      | Partial                                | Plans 02-01 and 02-02 completed; 02-03 superseded by 02.1                                                                                                                             |
| 02.1   | Implementation done; UAT surfaced gaps | Plan C pivot — simplify triage draft surface; live UAT blocked by 02.1.1 gaps                                                                                                         |
| 02.1.1 | Complete                               | Plan 01 (dict-leak fix) + Plan 02 (inline body + header-line) shipped + verified live                                                                                                 |
| 02.1.2 | Complete                               | Live UAT 2026-04-28 PASSED — Bella grounded on `triage-digest-latest.md`; summary, draft (Judy), ignore (Jaclyn) all worked; operator-driven send-now of Modern Forms reply succeeded |
| 02.1.3 | Complete                               | Patched digest snapshot + ops pipeline; UAT 2026-05-03 (tail sentinel); deploy + grep verified                                                                                        |
| 02.2   | **Complete** (closed 2026-05-04)       | VPS **2026.5.2** (`8b2a6e5`) via `openclaw-ops`; triage UAT + `tdr` send; Local/Mac optional alignment noted in `02.2-VERSION-TARGET.md`                                              |
| 3      | Not started                            | Prior Beeper design work available                                                                                                                                                    |
| 4      | Not started                            | API investigation needed early                                                                                                                                                        |
| 5      | Not started                            | After Phases 2-4 stabilize                                                                                                                                                            |

---

_Last updated: 2026-05-04 (Phase **02.2** closed — VPS + ops + triage UAT; Local/Mac alignment optional)_

---

## Backlog

Future-phase parking lot. Promote with `/gsd-review-backlog` when ready.

### Phase 999.1: Triage digest grouping and presentation (BACKLOG)

**Goal:** Improve digest readability by grouping messages logically (per-source section headings such as "Hospitable" / "Email"; per-thread sub-grouping such as "Judy ↔ Jaclyn (res …)"; consider table or chart format for the at-a-glance view).
**Why:** During 02.1.2 UAT (2026-04-28), Bella correctly grounded on the digest but the rendered list mixed messages from the same Hospitable thread without a clear sub-heading or thread roll-up. Clean grouping makes the operator scan + Bella's `summary` output dramatically faster.
**Requirements:** TBD (touchpoints: `scripts/deploy/lib/triage_digest_build.py`, mirrored to `~/openclaw-ops/vps/scripts/`; potentially the inbound `triageDigestSnapshot` header copy).
**Plans:** 0 plans

Plans:

- [ ] TBD (promote with `/gsd-review-backlog` when ready)

### Phase 999.2: Triage agent reply fidelity — full body + inline images (BACKLOG)

**Goal:** When the operator asks for the "full text" or "body" of an email, Bella returns the complete content rather than a `…`-truncated paraphrase, and surfaces inline images (or at least image references / OCR-able alt text) when present.
**Why:** During 02.1.2 UAT (2026-04-28), the Modern Forms email body came back partial with `...` even though Bella could summarize it; an inline image in the same email was not represented. Truncation is currently capped at 4000 body chars in the digest blockquote — sufficient for summary, insufficient for full-body asks.
**Requirements:** TBD (touchpoints: digest body cap in `triage_digest_build.py`; possible second-tier "full body" snapshot fetch path, or on-demand expansion via existing `tdr` token; image extraction/representation strategy).
**Plans:** 0 plans

Plans:

- [ ] TBD (promote with `/gsd-review-backlog` when ready)

### Phase 999.3: Triage inclusion — broaden inbox-of-today, exclude promotions/newsletters (BACKLOG)

**Goal:** Expand the digest's email inclusion rules so it shows everything received today (excluding promotions/newsletters, or at least demoting them under a separate sub-heading) rather than gating on the strict "Response Required" / `needs_reply` heuristic.
**Why:** During 02.1.2 UAT (2026-04-28), the Modern Forms support email was a real reply-needed item but didn't surface in the digest until the operator asked Bella directly — i.e., the response-required filter is too strict and missing genuine email today. Goal is "all today's email, with promos demoted/grouped, not silently dropped."
**Requirements:** TBD (touchpoints: classifier in `gws-personal` / review scripts; promo/newsletter heuristic; digest section ordering; mirror to `~/openclaw-ops/vps/scripts/`).
**Plans:** 0 plans

Plans:

- [ ] TBD (promote with `/gsd-review-backlog` when ready)

### Phase 999.4: Triage `tdr` explicit send confirmation gate (BACKLOG)

**Goal:** Require an unambiguous operator approval step before any Gmail send (`tdr send` / `send-now`), so conversational phrasing like “reply that …” cannot be interpreted as send consent.

**Why:** During 2026-05-03 live UAT, Bella sent immediately after a draft request; the runbook’s “explicit operator intent” line is soft enough that models skip the preview/approve beat. Optional hardening: remove `send-now`, split `draft` → `send`, and tighten `triage-draft-runbook.md`.

**Requirements:** TBD (touchpoints: `openclaw-gws-triage-reply`, `scripts/deploy/prompts/triage-draft-runbook.md`, operator UX in Telegram; mirror to `~/openclaw-ops/vps/scripts/`).

**Plans:** 0 plans

Plans:

- [ ] TBD (promote with `/gsd-review-backlog` when ready)
