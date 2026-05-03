---
phase_plan: "02-1-3-01-PLAN.md"
status: completed
completed: "2026-05-03"
---

## Objective

Telegram digest snapshot logic at upstream layout `extensions/telegram/src/` (SHA `v2026.4.12` `1c0672b*`): new module + `buildTelegramInboundContextPayload` wiring + Vitest + exportable unified diff for ops patch.

## Baseline

```bash
$ cd /tmp/openclaw-patch-02-1-3 && git rev-parse HEAD
1c0672b74f66038fd4ee76fbf1c21715887149d8

$ test -f extensions/telegram/src/bot-message-context.session.ts && echo ok
ok
```

Upstream baseline `extensions/telegram/src/bot-message-context.session.ts` (first lines) imports from `openclaw/plugin-sdk` channel/routing/command/config paths — no digest snapshot hooks before this change.

## Commands

```bash
cd /tmp/openclaw-patch-02-1-3
pnpm install
pnpm exec vitest run extensions/telegram/src/triage-topic-digest-snapshot.test.ts extensions/telegram/src/bot-message-context.session.triage-digest-snapshot.test.ts
pnpm build
```

Vitest snapshot: **Test Files 2 passed (2)**, **Tests 9 passed (9)**.

## Artifacts created (scratch clone)

| Path                                                                                                      |
| --------------------------------------------------------------------------------------------------------- |
| `extensions/telegram/src/triage-topic-digest-snapshot.ts`                                                 |
| `extensions/telegram/src/triage-topic-digest-snapshot.test.ts`                                            |
| `extensions/telegram/src/bot-message-context.session.triage-digest-snapshot.test.ts`                      |
| `extensions/telegram/src/bot-message-context.session.ts` (wired imports + envelope / BodyForAgent prefix) |

## Patch export

- Generated: `/tmp/0001-telegram-triage-digest-snapshot.patch`
- Canonical copy committed in ops: `~/openclaw-ops/vps/patches/0001-telegram-triage-digest-snapshot.patch`
- Verified: `git apply --check` from clean pinned SHA checkout.

## Decisions / notes

- `shouldInjectTriageDigestSnapshot`: `TelegramTopicConfig.triageDigestSnapshot` is consumed via `(topicConfig as Record<string,...>)` cast because JSON Schema/Zod additions are deferred — automated coverage focuses on **env** guards `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID` + `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID`.
- Session wiring uses `resolveTriageDigestSnapshotPath()` with **no** topic-level path argument (MVP; config field deferred).

## key-files.created

```yaml
created:
  - extensions/telegram/src/triage-topic-digest-snapshot.ts
  - extensions/telegram/src/triage-topic-digest-snapshot.test.ts
  - extensions/telegram/src/bot-message-context.session.triage-digest-snapshot.test.ts
modified:
  - extensions/telegram/src/bot-message-context.session.ts
```

## Self-check: PASSED
