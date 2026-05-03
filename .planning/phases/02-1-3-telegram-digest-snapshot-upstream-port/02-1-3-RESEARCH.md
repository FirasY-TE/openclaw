# Phase 02.1.3 — Technical research

## RESEARCH COMPLETE

**Research date:** 2026-05-03  
**Pinned upstream baseline:** `1c0672b` (documented as `v2026.4.12` in phase CONTEXT)

## Problem statement (verified)

Production VPS installs OpenClaw from an **upstream-shaped npm tarball** built from **`extensions/telegram`** (Telegram workspace plugin). At `1c0672b`, `buildTelegramInboundContextPayload` lives in:

- `extensions/telegram/src/bot-message-context.session.ts`

It imports Telegram config types from `openclaw/plugin-sdk/config-runtime` — not from legacy `src/telegram/` paths.

A separate line of experimentation in some forks targeted **`src/telegram/bot-message-context.session.ts`**. That implementation does **not** ship in the Telegram extension bundle consumed by builds that compile only/along-side the **`extensions/telegram`** tree for release packaging — producing a **silent gap** where VPS `grep` finds no snapshot symbols in `dist/`.

**Operational trigger:** Telegram **4096** character ceiling on a single Bot API message. Digest posting uses topic send without guaranteed chunking; once digest length exceeds the cap (**Backlog 999.3 broadens inclusion**), delivery fails outright unless the agent still receives **`triage-digest-latest.md`** via the **bounded file-read injection** path (**32 768 chars** tail-truncated with explicit marker).

## Target architecture at `1c0672b`

| Area                                  | Location at `1c0672b`                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------------------------ |
| Inbound Telegram context assembly     | `extensions/telegram/src/bot-message-context.session.ts`                                   |
| Telegram plugin registration          | `extensions/telegram/` (`channel.ts`, `runtime.ts`, `index.ts`)                            |
| `TelegramTopicConfig` type definition | Core `src/config/types.telegram.ts` (re-exported through plugin SDK for extension imports) |

**Observation:** At `1c0672b`, `TelegramTopicConfig` includes **no** `triageDigestSnapshot` / path fields yet. OPS CONTEXT explicitly allows **environment-based** `(chatId, topicId)` pairing when strict channel JSON Schema / AJV disallow custom topic keys.

## Port blueprint (minimal viable patch)

1. **New module:** `extensions/telegram/src/triage-topic-digest-snapshot.ts`
   - Port logic from contemporary reference: `src/telegram/triage-topic-digest-snapshot.ts` **on this branch** (`DEFAULT_TRIAGE_DIGEST_SNAPSHOT_PATH`, `TRIAGE_DIGEST_SNAPSHOT_MAX_CHARS = 32768`, read/truncate/format/sentinel text, **`## Canonical triage digest snapshot (not user message)`** header).
   - Replace `TelegramTopicConfig` import with the same source `bot-message-context.session.ts` uses at `1c0672b`: `openclaw/plugin-sdk/config-runtime`.
   - **Injection predicate:** `shouldInjectTriageDigestSnapshot` must support:
     - `topicConfig?.triageDigestSnapshot === true` **only if** types + Zod eventually allow it (optional wave); and
     - **always** the env fallback: `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID` + `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID` (both required for env path), plus `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH` override for file path.
2. **Hook site:** In `buildTelegramInboundContextPayload`, after computing `body` / before composing `combinedBody`, mirror the reference behavior:
   - `resolveTriageDigestSnapshotPath(topicConfig?.triageDigestSnapshotPath)` — omit call if type lacks field until schema extended; gate on env-only branch first.
   - If `shouldInjectTriageDigestSnapshot(...)`, prepend `formatTriageDigestSnapshotSection(readTriageDigestSnapshot(path))` to both the envelope body used for **`Body`** and the plain prefix for **`BodyForAgent`** (same semantics as reference in `src/telegram/bot-message-context.session.ts` on this workspace).
3. **Tests:** Add colocated Vitest beside other `extensions/telegram/src/*.test.ts` patterns:
   - Unit tests for snapshot read/format/truncate/env predicate (mirroring `src/telegram/triage-topic-digest-snapshot.test.ts` intent).
   - Session integration test exercising `Body`/`BodyForAgent` when env matches (**no** Telegram network).
4. **Schema / types:** **Deferred past Phase 02.1.3** (planned follow-up). ROADMAP bullet _“Config schema additions re-located…”_ is satisfied for production by **env-only** activation until custom `triageDigestSnapshot` keys survive channel JSON Schema validation. Phase 02.1.3 plans explicitly scope out Zod/types edits; add them only in a later phase after upstream schema allows custom topic keys.

## openclaw-ops deliverables

Per `.cursor/rules/vps-ssh-openclaw.mdc` and ROADMAP:

| Artifact                                                 | Purpose                                                                                                                          |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `vps/.openclaw-version` pinning `1c0672b`                | Stable patch baseline                                                                                                            |
| `vps/patches/0001-telegram-triage-digest-snapshot.patch` | Applies TypeScript delta on clean upstream checkout                                                                              |
| `vps/build-patched-openclaw.sh`                          | `git checkout`/`clone` pinned SHA → `git apply` or `patch -p1` → `pnpm install` → `pnpm build` → `npm pack` reproducible tarball |
| `deploy.sh --with-core` (or equivalent documented flag)  | Installs tarball into `/data/.npm-global` (or compose-documented target)                                                         |

**Regression guard after deploy:**

```bash
grep -rl OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID /data/.npm-global/lib/node_modules/openclaw/dist/*.js
```

must return ≥1 match (exact path suffix may vary by npm layout).

## Risks / decisions

| Risk                               | Mitigation                                                                                                                                      |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Patch context drift vs future SHAs | Keep `0001-*.patch` strictly relative to `vps/.openclaw-version`; bump SHA only with manual rebase                                              |
| Schema rejects new topic keys      | Ship env-based activation first (already required in CONTEXT)                                                                                   |
| Large digest UAT                   | Artificial fixture >4096 chars in `triage-digest-latest.md` on VPS; confirm Bella cites lines **only** present past Telegram-visible truncation |

## Validation Architecture

### Test Framework

| Property           | Value                                                                                                                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framework          | Vitest (monorepo `pnpm test` / targeted `pnpm exec vitest run …`)                                                                                                                                    |
| Config file        | `vitest.config.ts` (repo root)                                                                                                                                                                       |
| Quick run command  | `pnpm exec vitest run extensions/telegram/src/triage-topic-digest-snapshot.test.ts extensions/telegram/src/bot-message-context.session.triage-digest-snapshot.test.ts` (paths **after** files exist) |
| Full suite command | `pnpm build` then `pnpm test` (or CI-equivalent)                                                                                                                                                     |

### Phase requirements → test map

| Behavior                                        | Test type   | Automated command                                           |
| ----------------------------------------------- | ----------- | ----------------------------------------------------------- |
| Snapshot read + truncate + sentinel             | unit        | vitest on `triage-topic-digest-snapshot.test.ts`            |
| Env-gated injection predicate                   | unit        | vitest cases for env match / non-match                      |
| `Body` / `BodyForAgent` receive digest preamble | integration | vitest importing session builder with harness               |
| Patched tarball contains snapshot strings       | grep smoke  | Run **after** pack in build script CI section or manual UAT |
| Bella cites file-only rows                      | manual UAT  | ROADMAP UAT checklist                                       |

### Sampling rate

- After each substantive TS edit: targeted vitest files above
- Before ops handoff: `pnpm build` + full test or nightly-equivalent subset for `extensions/telegram`
- After VPS deploy: `grep` proof + Telegram large-digest scenario

### Wave 0 gaps

- None for Vitest infra (already canonical in repo)
- **Manual-only:** Telegram human UAT large-digest thread
- Optional: automate `unpack pack && rg` smoke inside `build-patched-openclaw.sh`

## Sources (confidence)

### High

- `.planning/phases/02-1-3-telegram-digest-snapshot-upstream-port/02-1-3-CONTEXT.md`
- `.planning/ROADMAP.md` Phase 02.1.3 section
- `git show 1c0672b:extensions/telegram/src/bot-message-context.session.ts` (imports + layering)
- `git show 1c0672b:src/config/types.telegram.ts` (`TelegramTopicConfig` fields)
- `src/telegram/triage-topic-digest-snapshot.ts` + `bot-message-context.session.ts` (**reference semantics** — adapt paths/imports only)

### Medium

- Current shortened `extensions/telegram/` layout on **`main`/HEAD newer than `1c0672b`** — **do not assume HEAD matches patch base**; always validate against **`1c0672b`** when generating `0001` patch

## Metadata

**Valid until:** 2026-06-03
