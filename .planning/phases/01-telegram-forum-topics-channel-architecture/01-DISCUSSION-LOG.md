# Phase 1: Telegram Forum Topics + Channel Architecture - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-13
**Phase:** 1-telegram-forum-topics-channel-architecture
**Areas discussed:** Forum + topic layout, DM fallback policy, routing utility contract, migration/operator workflow

---

## Forum + Topic Layout

| Option | Description | Selected |
|--------|-------------|----------|
| `Triage Digest` for morning brief | Group digest-style operational summaries in one dedicated topic; simplifies scanning | ✓ |
| `General` for morning brief | Keep morning brief in forum general stream and reserve triage topic for later EOD usage | |
| Other custom arrangement | Alternate topic naming/routing split | |

**User's choice:** Use `Triage Digest` for morning brief now.
**Notes:** User confirmed they currently only have DM and accepted forum group creation as required for topics. User further clarified nightly reset and morning brief should be in the same place. Final decision: both morning brief and nightly reset route to `Triage Digest` "for now" and may be changed later.

---

## DM Fallback Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Keep DM as failure fallback only | Topic routing primary; fallback to DM when topic delivery fails | ✓ |
| Dual-deliver always to DM and topic | Send all operational updates to both channels | |
| Urgent-only parallel DM | Always DM urgent items in addition to topic stream | |

**User's choice:** Keep DM and use it as fallback after topic migration.
**Notes:** User asked whether DM becomes useless; clarified DM remains useful as fallback/safety channel.

---

## Routing Utility Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Canonical route map + shared utility | Central route-to-target map consumed by scripts/agents; avoids hardcoded duplication | ✓ |
| Per-script hardcoded targets | Each script maintains its own target IDs | |
| Agent-only dynamic routing | Runtime-only logic with no operator-facing canonical map | |

**User's choice:** Accepted canonical centralized mapping approach.
**Notes:** Use topic-capable Telegram target format and keep live IDs runtime-configurable.

---

## Migration / Operator Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Documented checklist in current ops docs | Explicit runbook for forum creation, bot setup, topic IDs, migration, fallback tests | ✓ |
| Minimal ad hoc migration | Manual changes without a durable checklist | |
| Full automation before migration | Script everything before any routing change | |

**User's choice:** Accepted checklist-driven migration in existing operational docs.
**Notes:** Auth alerts should route to `System/Auth`.

---

## Claude's Discretion

- Specific script layout and naming for routing helper wrappers.
- Exact configuration storage shape for topic ID mapping (env keys vs generated map file) as long as docs remain canonical.

## Deferred Ideas

- None.
