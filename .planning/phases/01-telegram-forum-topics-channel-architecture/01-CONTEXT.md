# Phase 1: Telegram Forum Topics + Channel Architecture - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up a Telegram Forum supergroup with topic-based routing for automation delivery, migrate existing DM-based operational deliveries to topic targets, preserve DM fallback on failures, and document canonical topic routing for future phases.

</domain>

<decisions>
## Implementation Decisions

### Forum + Topic Layout
- **D-01:** Use a Telegram Forum supergroup (topics enabled). DM-only mode is insufficient because Telegram topics do not exist in DMs.
- **D-02:** Create and keep this topic set: `Urgent`, `Triage Digest`, `Beeper`, `Hospitable`, `System/Auth`.
- **D-03:** In Phase 1, pre-create all topics, but migrate active delivery for operational digests first; other topics can remain ready for later phases.
- **D-04:** Route both the morning brief and nightly reset to the same topic: `Triage Digest` (explicitly changeable later if needed).

### DM Fallback Policy
- **D-05:** Forum topic delivery is primary; DM remains active as fallback.
- **D-06:** On topic-delivery failure, retry once, then send to DM target (`telegram:1460581318`) with fallback context.
- **D-07:** Do not add parallel "always DM urgent" behavior in Phase 1; keep scope to fallback behavior only.

### Routing Utility Contract
- **D-08:** Define one canonical logical-route-to-target mapping that all scripts and agents use.
- **D-09:** Use Telegram target format that supports topics (for example, `chatId:topic:topicId`) instead of scattered hardcoded IDs.
- **D-10:** Keep runtime live IDs in VPS config/env and keep repo docs as the canonical routing reference for operators and future phases.

### Migration and Operator Workflow
- **D-11:** Add an operator-facing migration checklist in existing docs that are already used operationally.
- **D-12:** Checklist includes: create forum, enable topics, add bot, create topics, capture topic IDs, configure routing map, migrate morning brief/nightly reset/auth alert routing, and validate DM fallback.
- **D-13:** Route auth health alerts to `System/Auth`.

### Claude's Discretion
- Exact wrapper/script shape for shared routing utility.
- Whether to represent routing map as environment variables, generated config, or a small checked-in template + runtime override.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Intent
- `.planning/ROADMAP.md` — Phase 1 goal, requirements, success criteria, and UAT checks for forum topics and routing.
- `.planning/PROJECT.md` — Product-level constraints and current architecture baseline.

### Current Runtime Delivery and Scheduling
- `docs/cron-jobs.txt` — Current live cron schedules and DM delivery targets, including evening reset and morning brief delivery configuration.
- `docs/morning-brief.txt` — Morning brief execution chain and current Telegram delivery target behavior.
- `docs/agent-architecture.txt` — Operational chain and current delivery model used in production notes.
- `docs/project-state.txt` — Current state snapshot including Telegram delivery status.

### Telegram Targeting and Topic-Capable Delivery
- `src/telegram/targets.ts` — Target parsing/format conventions that support chat/topic routing.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/telegram/targets.ts`: Already parses topic-capable target forms; this can be reused by the new routing utility and migration logic.

### Established Patterns
- Existing operational jobs currently deliver via explicit Telegram target strings in cron/job configs, so a central mapping utility should preserve this ops pattern while replacing DM-only targets.

### Integration Points
- Delivery target definitions currently reflected in ops docs (`docs/cron-jobs.txt`, `docs/morning-brief.txt`) and cron/job configuration on VPS.
- Auth health alert and morning/evening automation scripts are immediate integration points for topic routing in this phase.

</code_context>

<specifics>
## Specific Ideas

- Keep DM useful as a safety net; topics become primary delivery surface.
- Morning brief and nightly reset should remain colocated in one topic for easier daily scanning.
- "Triage Digest for now; can change later if needed" is an intentional reversible decision.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-telegram-forum-topics-channel-architecture*
*Context gathered: 2026-04-13*
