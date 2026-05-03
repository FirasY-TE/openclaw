---
phase: 02.1.3
slug: telegram-digest-snapshot-upstream-port
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-03
---

# Phase 02.1.3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property               | Value                                                                                                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Framework**          | Vitest (TypeScript)                                                                                                                                                    |
| **Config file**        | `vitest.config.ts`                                                                                                                                                     |
| **Quick run command**  | `pnpm exec vitest run extensions/telegram/src/triage-topic-digest-snapshot.test.ts extensions/telegram/src/bot-message-context.session.triage-digest-snapshot.test.ts` |
| **Full suite command** | `pnpm build && pnpm test`                                                                                                                                              |
| **Estimated runtime**  | ~120–600 seconds (machine dependent)                                                                                                                                   |

---

## Sampling Rate

- **After every task commit:** Run the quick vitest command (or narrower file scope if only one module touched).
- **After every plan wave:** `pnpm build` + `pnpm exec vitest run extensions/telegram/src/` (adjust glob to match added tests).
- **Before `/gsd-verify-work`:** Full suite command green locally (or documented CI surrogate).
- **Max feedback latency:** 600 seconds on full gate.

---

## Per-Task Verification Map

| Task ID      | Plan | Wave | Requirement                       | Test Type        | Automated Command                                                                                         | File Exists   | Status     |
| ------------ | ---- | ---- | --------------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------- | ------------- | ---------- |
| 02.1.3-01-T1 | 01   | 1    | TRIAGE-02.1.3-1                   | unit/manual prep | Confirm `git show 1c0672b:extensions/telegram/src/bot-message-context.session.ts` exists                  | ✅            | ⬜ pending |
| 02.1.3-01-T2 | 01   | 1    | TRIAGE-02.1.3-2                   | unit             | `pnpm exec vitest run extensions/telegram/src/triage-topic-digest-snapshot.test.ts`                       | ❌ W0 adds    | ⬜ pending |
| 02.1.3-01-T3 | 01   | 1    | TRIAGE-02.1.3-2 (session asserts) | integration      | `pnpm exec vitest run extensions/telegram/src/bot-message-context.session.triage-digest-snapshot.test.ts` | ❌ W0 adds    | ⬜ pending |
| 02.1.3-01-T4 | 01   | 1    | TRIAGE-02.1.3-4 (vite tests pass) | unit             | `pnpm exec vitest run …` combined files                                                                   | ❌ W0 adds    | ⬜ pending |
| 02.1.3-01-T5 | 01   | 1    | TRIAGE-02.1.3-4 (patch export)    | smoke            | `git apply --check` on `/tmp/0001-…patch`                                                                 | ❌ artifact   | ⬜ pending |
| 02.1.3-02-T1 | 02   | 2    | TRIAGE-02.1.3-5                   | script           | `"$HOME/openclaw-ops/vps/build-patched-openclaw.sh"` exits 0                                              | ❌ ops        | ⬜ pending |
| 02.1.3-02-T2 | 02   | 2    | TRIAGE-02.1.3-6                   | grep             | Pack output / installed `dist` contains `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID`                         | manual on VPS | ⬜ pending |

_Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky_

---

## Wave 0 Requirements

- [x] Vitest infra — existing monorepo
- [ ] `extensions/telegram/src/triage-topic-digest-snapshot.ts` — created by Plan 01
- [ ] `extensions/telegram/src/triage-topic-digest-snapshot.test.ts` — created by Plan 01
- [ ] Session snapshot test module — created by Plan 01
- [ ] Ops `build-patched-openclaw.sh` + `0001-*.patch` — created by Plan 02 (`openclaw-ops`)

---

## Manual-Only Verifications

| Behavior                       | Requirement       | Why Manual               | Test Instructions                                                                                                                                              |
| ------------------------------ | ----------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bella cites lines only on disk | TRIAGE-02.1.3-UAT | Model + Telegram surface | Populate digest >4096 chars; truncate chat-visible portion; prompt `summary` in triage topic; confirm agent cites footer-only anchors present in markdown file |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no three consecutive tasks without automated verify (session UAT bounded by vitest/grep pair)
- [ ] Wave 0 covers all test file references
- [ ] No watch-mode flags in scripted commands
- [ ] Feedback latency target met on development machine used for gate
- [ ] `nyquist_compliant: true` retained in frontmatter after execution proof

**Approval:** pending
