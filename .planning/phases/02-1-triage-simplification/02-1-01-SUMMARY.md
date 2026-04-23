---
phase: 02-1-triage-simplification
plan: 01
subsystem: infra
tags: [telegram, triage, digest, vps, decommission]
requires:
  - phase: 02-end-of-day-triage-on-demand-command
    provides: triage digest and token-state baseline
provides:
  - Telegram triage path without custom auto-router/callback stack
  - Digest token-state path without callback/button coupling
  - Ops deploy/runtime decommission of patched-core triage artifacts
affects: [02-1-02, triage runtime operations]
tech-stack:
  added: []
  patterns: [token-only finalization flow, vanilla telegram handler routing]
key-files:
  created: [.planning/phases/02-1-triage-simplification/02-1-01-SUMMARY.md]
  modified:
    - scripts/deploy/lib/triage_digest_build.py
    - scripts/deploy/tests/test_triage_digest.py
key-decisions:
  - "Keep triage draft state path canonical and remove OPENCLAW_TRIAGE_DRAFT_STATE override from digest generation."
  - "Treat Telegram triage auto-router/callback removal as already-satisfied in source tree and enforce boundary via verification + decommission checks."
patterns-established:
  - "Digest output and token-state remain sufficient for tdr finalization without inline callback/button payloads."
  - "VPS ops source-of-truth removes patched-core triage lifecycle and draft-agent runtime wiring."
requirements-completed: [TRIAGE-02.1-1, TRIAGE-02.1-2]
duration: 43 min
completed: 2026-04-23
---

# Phase 02.1 Plan 01: Triage Simplification Decommission Summary

**Removed patched-core and callback-oriented triage draft runtime while preserving digest token-state and `tdr` finalization behavior.**

## Performance

- **Duration:** 43 min
- **Started:** 2026-04-23T03:24:00Z
- **Completed:** 2026-04-23T04:07:35Z
- **Tasks:** 4
- **Files modified:** 12

## Accomplishments

- Verified Telegram triage auto-router/callback modules and handler hooks were already absent in `src/telegram`.
- Removed digest builder env fallback to retired `OPENCLAW_TRIAGE_DRAFT_STATE` path while keeping token-state schema for `tdr`.
- Expanded digest regression coverage to enforce required token metadata and prevent callback payload regressions.
- Decommissioned VPS ops patched-core workflow, triage draft-agent binary, and retired triage env template keys; deployed updated scripts and verified runtime absence.

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove Telegram triage auto-router and callback integration** - `41f5336031` (chore)
2. **Task 2: Remove draft-agent/button code paths but keep token->tdr pipeline** - `aabf0a1d31` (fix)
3. **Task 3: Add anti-regression coverage for simplification boundary** - `bfbbb5004f` (test)
4. **Task 4: Execute ops-side decommission for patched-core and draft-agent runtime** - `023506f` (chore, in `openclaw-ops`)

## Files Created/Modified

- `.planning/phases/02-1-triage-simplification/02-1-01-SUMMARY.md` - plan execution summary
- `scripts/deploy/lib/triage_digest_build.py` - removed triage draft state env override fallback
- `scripts/deploy/tests/test_triage_digest.py` - strengthened token-state and no-callback regression checks
- `../openclaw-ops/vps/deploy.sh` - removed `--with-core` deployment path
- `../openclaw-ops/vps/README.md` - removed patched-core runbook instructions
- `../openclaw-ops/vps/compose/.env.example` - removed retired triage draft env keys
- `../openclaw-ops/vps/scripts/lib/triage_digest_build.py` - removed callback/button generation paths
- `../openclaw-ops/vps/scripts/openclaw-gws-triage-digest` - removed button payload send path
- `../openclaw-ops/vps/scripts/openclaw-gws-triage-reply` - fixed state path to canonical location
- `../openclaw-ops/vps/.openclaw-version` - removed
- `../openclaw-ops/vps/build-patched-openclaw.sh` - removed
- `../openclaw-ops/vps/patches/0001-telegram-triage-auto-route.patch` - removed
- `../openclaw-ops/vps/scripts/openclaw-gws-triage-draft-agent` - removed

## Decisions Made

- Kept digest token state deterministic to the canonical path and removed retired env override dependency.
- Accepted existing codebase state for Telegram auto-router/callback removal, validated with grep-based acceptance checks instead of reintroducing/deleting non-existent files.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Git commit identity unavailable in executor shell**

- **Found during:** Task 2 commit
- **Issue:** Direct `git commit` failed with unknown author identity.
- **Fix:** Used repo-standard `scripts/committer` workflow to create scoped commits without manual git config mutation.
- **Files modified:** none (process-only fix)
- **Verification:** task commits succeeded and hashes recorded.
- **Committed in:** `aabf0a1d31`, `bfbbb5004f`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep; deviation only affected commit transport mechanism.

## Authentication Gates

None.

## Issues Encountered

- The plan’s Task 1 verify command references `src/telegram/bot-handlers.test.ts`, but test files are located under `src/line/`; acceptance was validated via direct reference checks and full build.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Decommission baseline is complete; architecture boundary is regression-tested and deployed on VPS scripts runtime.
- Ready for Plan `02-1-02` follow-up work.

## Self-Check: PASSED

- FOUND: `.planning/phases/02-1-triage-simplification/02-1-01-SUMMARY.md`
- FOUND: `41f5336031`
- FOUND: `aabf0a1d31`
- FOUND: `bfbbb5004f`
- FOUND: `023506f`

---

_Phase: 02-1-triage-simplification_
_Completed: 2026-04-23_
