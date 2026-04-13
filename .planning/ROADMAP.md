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

| Phase | Status | Notes |
|-------|--------|-------|
| 1 | Not started | Foundation — all other phases depend on this |
| 2 | Not started | Depends on Phase 1 topic routing |
| 3 | Not started | Prior Beeper design work available |
| 4 | Not started | API investigation needed early |
| 5 | Not started | After Phases 2-4 stabilize |

---
*Last updated: 2026-04-08*
