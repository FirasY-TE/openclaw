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

**Plans:** 3 plans
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

**Plans:** TBD (run `/gsd-plan-phase` against this phase)

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

| Phase | Status           | Notes                                                     |
| ----- | ---------------- | --------------------------------------------------------- |
| 1     | Completed        | Foundation — topic routing live                           |
| 2     | Partial          | Plans 02-01 and 02-02 completed; 02-03 superseded by 02.1 |
| 02.1  | Context captured | Plan C pivot — simplify triage draft surface              |
| 3     | Not started      | Prior Beeper design work available                        |
| 4     | Not started      | API investigation needed early                            |
| 5     | Not started      | After Phases 2-4 stabilize                                |

---

_Last updated: 2026-04-13_
