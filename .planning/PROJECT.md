# OpenClaw Personal AI System — Phase 4+

## What This Is

An expansion of the existing OpenClaw personal AI system from a scheduled email/task automation pipeline into a proactive, multi-source unified inbox with intelligent triage, draft-and-approve messaging workflows, and Hospitable guest intelligence. The system runs on a Hostinger VPS (primary brain) with a paired macOS node for local Beeper/iMessage operations, and delivers through Telegram.

## Core Value

One inbox that cuts through the noise across all communication sources — surfacing what needs attention, drafting responses, and acting on approvals — so nothing important falls through the cracks.

## Requirements

### Validated

- ✓ Gmail review and classification (personal + rental) — existing, Phase 1-3
- ✓ Google Tasks creation and lifecycle tracking — existing
- ✓ Hospitable booking/reservation/message fetch — existing
- ✓ Rental signal merge and compound risk detection — existing
- ✓ Morning brief with dual-account data — existing
- ✓ Evening reset / next-day prep — existing
- ✓ Auth health monitoring with Telegram alerts — existing
- ✓ Appointment-to-calendar detection and confirmation — existing
- ✓ Cron-based scheduling infrastructure — existing
- ✓ Telegram DM delivery and inline button support — existing
- ✓ Paired macOS node for local operations — existing

### Active

- [ ] End-of-day triage digest (4:30 PM CST daily + on-demand command)
- [ ] Triage covers Gmail (personal + rental), Beeper messages, and Hospitable guest messages
- [ ] Triage categorizes items as urgent / needs attention / needs reply
- [ ] Triage offers to draft responses for items that need reply
- [ ] Beeper integration — fetch messages via Mac node (Desktop API / MCP / read-only skill)
- [ ] Beeper — surface urgent messages via Telegram
- [ ] Beeper — draft replies with Telegram approval workflow (Replace + Confirm Send)
- [ ] Beeper — send approved messages via Beeper Desktop API on Mac node
- [ ] Beeper — create Google Tasks from messages using existing task framework
- [ ] Hospitable knowledge base — built from historical guest conversations
- [ ] Hospitable — draft guest responses using knowledge base context
- [ ] Hospitable — auto-send for defined safe categories (e.g. standard check-in info, door codes)
- [ ] Hospitable — approval-required responses for sensitive categories (complaints, refunds, etc.)
- [ ] Hospitable — surface urgent guest messages via Telegram
- [ ] Hospitable — query bookings, earnings, pricing, and calendar availability
- [ ] Proactive agent — surface unread/unresponded items after configurable time thresholds
- [ ] Proactive agent — unified view across all communication sources
- [ ] Multi-agent architecture — orchestrator + domain-specific subagents
- [ ] Channel architecture — Telegram Forum Topics for separated delivery (triage, approvals, hospitable, urgent)
- [ ] On-demand triage command (run triage outside of scheduled time)

### Out of Scope

- Full auto-send for all Beeper messages — always require approval for non-Hospitable channels
- Replacing the morning brief — the triage is complementary (end-of-day backward-looking vs. morning forward-looking)
- Direct Airbnb/VRBO API integration — Hospitable API is the unified source for bookings
- Voice/phone call handling — text-based channels only for now
- Building a custom web dashboard — Telegram (with Forum Topics) is the primary UI
- Auto-responding to personal/rental email — draft-only for email, approval required

## Context

### Current System (Phase 3 complete)

The VPS runs a pipeline of 9 specialized scripts under cron that handle Gmail review, classification, task creation, Hospitable fetch, rental signal merge, task lifecycle sync, auth health monitoring, and morning brief assembly. Data flows through JSON/text files in `/data/openclaw-gws/output/`. The morning brief is delivered via Telegram at 7:00 AM weekdays. An evening reset runs Sun-Thu at 9:15 PM.

See `docs/agent-architecture.txt` for the full live agent chain and data flow.
See `docs/project-state.txt` for system state through Phase 3.
See `docs/cron-jobs.txt` for all scheduled jobs.

### Runtime Architecture

- **VPS (brain):** Docker container `openclaw-ridl-openclaw-1`, OpenClaw `2026.3.28`, persistent state at `/data/.openclaw/`, automation scripts at `/data/openclaw-gws/bin/`
- **Mac (local node):** Paired macOS node for Beeper Desktop API access (iMessage, SMS, chat networks), local CLI operations
- **Telegram:** DM with bot for delivery and approvals (Telegram user ID: 1460581318)
- **Google Workspace:** Two accounts (personal + rental) via `gws-personal` / `gws-rental` wrappers with isolated auth
- **Hospitable:** PAT-based API access, fetches properties/reservations/messages

### Beeper Integration (prior exploration)

Extensive design work done in a prior Cursor session covering: read-only skill (`KrauseFx/beeper`), Beeper Desktop API endpoints (focus, send, list chats), Mac node execution via `openclaw nodes run`, Telegram inline button approval flow (callback_data ≤ 64 chars), draft/replace/confirm UX, and MCP setup. Key decisions directional but open for refinement in discuss phase.

Reference: `/Users/bellabot/Downloads/cursor_beeper_integration_with_openclaw.md`

### Hospitable Knowledge Base (to be built)

3 years of guest communication history exists in Hospitable. API depth for historical messages needs investigation. Knowledge base will capture common guest questions and proven responses to enable auto-send for safe categories and faster drafting for complex ones. Implementation approach (RAG, vector DB, or structured document) to be determined based on data volume and query patterns.

### Channel Architecture (to be discussed)

Current: single Telegram DM handles all delivery. Planned: Telegram Forum Topics to separate triage digests, messaging approvals, Hospitable alerts, and urgent notifications into distinct threads. Keeps one app, adds necessary separation. DM may be retained for real-time urgent items. To be finalized in discuss phase.

### Multi-Agent Architecture (incremental adoption)

Current scripts are effectively single-purpose agents. The expansion naturally splits into domain-specific subagents (Gmail intelligence, Beeper, Hospitable, Triage) coordinated by an orchestrator that owns the Telegram conversation and approval workflows. OpenClaw's existing subagent framework (`src/agents/`) supports this. Migration will be incremental — start with orchestrator pattern, move capabilities into dedicated subagents as each stabilizes.

## Constraints

- **Beeper locality:** Beeper Desktop API only accessible on the Mac (localhost:23373). All Beeper read/write operations must route through the paired Mac node.
- **Telegram callback_data:** ≤ 64 characters enforced by OpenClaw. Approval tokens must be short; full Beeper chat IDs stored server-side.
- **Hospitable API:** Messages accessed via `/v2/reservations/{id}/messages` (per-reservation, not top-level). Historical depth unknown — needs investigation.
- **Google Tasks dedupe:** Existing pipeline uses hex `Message ID:` in task notes for dedup. Beeper/Hospitable items must generate compatible hex fingerprints.
- **Container permissions:** Gateway runs as `node` user. All credential files and scripts must be node-owned.
- **Auth fragility:** Google Workspace tokens can expire from revocation or drift. Auth health check runs every 30 min with Telegram alerting.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| VPS stays as primary brain | Established infrastructure, persistent state, cron system | ✓ Good |
| Mac node for Beeper operations | Beeper Desktop API is localhost-only; iMessage requires macOS | ✓ Good |
| Telegram as primary delivery UI | Already configured, inline buttons work, user is there | ✓ Good |
| Telegram Forum Topics for channel separation | Keeps one app, adds topic-based routing to avoid noisy single DM | — Pending |
| Google Tasks as unified task/reminder system | Existing pipeline, dedupe logic, two task lists already configured | ✓ Good |
| Hospitable API as booking data source | Aggregates Airbnb + VRBO + pricing app | ✓ Good |
| Incremental multi-agent migration | Avoid big-bang rewrite; orchestrator first, subagents as domains stabilize | — Pending |
| Draft-first for email and Beeper | Safety; auto-send only for defined Hospitable categories | — Pending |
| Knowledge base approach for Hospitable | RAG/vector DB vs structured docs — depends on data volume investigation | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-08 after initialization*
