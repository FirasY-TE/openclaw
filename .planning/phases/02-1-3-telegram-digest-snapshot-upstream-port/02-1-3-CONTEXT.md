---
phase: "02.1.3"
title: "Port digest-snapshot TS to upstream extensions/telegram + ship patch pipeline"
status: implemented
opened: "2026-04-28"
---

## Why

Phase 02.1.2 added a digest-snapshot injection feature (`src/telegram/triage-topic-digest-snapshot.ts` + edits to `bot-message-context.session.ts`) intended to provide Bella with a 32 KB-capped canonical digest from `/data/openclaw-gws/output/triage-digest-latest.md`, sidestepping Telegram's 4096-char per-message cap.

During UAT cleanup on **2026-04-28** we discovered:

1. Upstream `openclaw/openclaw` at **`v2026.4.12` (`1c0672b`)** has restructured Telegram code into a workspace package at **`extensions/telegram/src/`**, importing from `openclaw/plugin-sdk/*` paths.
2. Our 02.1.2 code lives at the **old path `src/telegram/`** with the **old relative imports** (`../config/types.js`).
3. When we rebuilt the openclaw tarball from a fresh upstream `v2026.4.12` worktree (`/tmp/oc-2026`), the build picked up upstream's `extensions/telegram/` files and **silently ignored** our `src/telegram/` additions.
4. The deployed binary on the VPS therefore contains **no digest-injection runtime code** — confirmed by grepping for `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID`, `DEFAULT_TRIAGE_DIGEST_SNAPSHOT_PATH`, `readTriageDigestSnapshot`, `Canonical triage digest snapshot`, `triage-digest-latest.md` — none present in `/data/.npm-global/lib/node_modules/openclaw/`.

UAT still passed because today's digest is **1079 chars** (well under 4096), so Bella reads it as a normal Telegram message in the topic conversation history. **This breaks as soon as Backlog 999.3 broadens inclusion** — `send_with_topic_fallback` posts the whole digest as a single message and offers no chunking; at >4096 chars Telegram returns `message is too long` and the whole digest **fails to send entirely** (verified by reading `vps/scripts/lib/telegram-topic-routing.sh`).

## Goal

Port the 02.1.2 TS code so the deployed binary actually contains the digest-snapshot injection runtime, and stand up the `openclaw-ops/vps/patches/` + `build-patched-openclaw.sh` pipeline that's documented in `vps/README.md` but doesn't exist yet.

## Scope

- Rewrite the snapshot module + tests for upstream's `extensions/telegram/src/` layout (imports → `openclaw/plugin-sdk/*`).
- Find the right hook in upstream's `extensions/telegram/src/bot-message-context.session.ts` (`buildTelegramInboundContextPayload`, line 79 in `v2026.4.12`) and apply the digest-injection there.
- Re-locate config schema additions in upstream's split structure (`TelegramTopicConfig`, Zod schema).
- Write `openclaw-ops/vps/patches/0001-telegram-triage-digest-snapshot.patch` against pinned `vps/.openclaw-version=1c0672b`.
- Add `openclaw-ops/vps/build-patched-openclaw.sh` (clone upstream at SHA → apply patches → `pnpm install && pnpm build && npm pack`).
- Optional `--with-core` flag for `vps/deploy.sh` to scp + `npm install -g` the tarball.
- Re-run live UAT with a forced large digest fixture (>4096 chars) to confirm Bella still grounds correctly via the file path, not topic history.

## Out of scope

- Changes to `triage_digest_build.py` (digest content / inclusion / formatting). Those live in Backlog 999.1/999.2/999.3.
- Upstream PR to `openclaw/openclaw`. The env-fallback hack (`OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID/_TOPIC_ID`) is specifically a workaround for the channel-plugin JSON Schema rejecting custom topic-config keys — that should be addressed before any upstream PR.

## When to land

Before Backlog **999.3** ships (broaden inclusion). Earlier is fine — this purely adds a safety net and changes no observable behavior at current digest sizes.

## Reference artifacts

- 02.1.2 TS code (current location, old structure): `~/openclaw/src/telegram/triage-topic-digest-snapshot.ts`, `~/openclaw/src/telegram/triage-topic-digest-snapshot.test.ts`, `~/openclaw/src/telegram/bot-message-context.session.ts`, `~/openclaw/src/telegram/bot-message-context.triage-digest-snapshot.test.ts`, `~/openclaw/src/config/types.telegram.ts`, `~/openclaw/src/config/zod-schema.providers-core.ts`.
- Upstream target: `extensions/telegram/src/bot-message-context.session.ts` (439 lines in `v2026.4.12`).
- Pinned SHA: `1c0672b` (= `v2026.4.12`).

## Self-Check

Open phase. To plan: `/gsd-plan-phase 02.1.3`.
