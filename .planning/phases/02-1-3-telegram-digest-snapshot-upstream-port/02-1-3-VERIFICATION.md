---
status: passed
phase: 02.1.3 — Telegram digest-snapshot upstream port + ops patch pipeline
verified: "2026-05-03"
---

## Automated

- **Upstream patch tree:** Working changes applied on `extensions/telegram` at OpenClaw `1c0672b74f66038fd4ee76fbf1c21715887149d8` (`/tmp/openclaw-patch-02-1-3` scratch clone). Commands:
  - `pnpm exec vitest run extensions/telegram/src/triage-topic-digest-snapshot.test.ts extensions/telegram/src/bot-message-context.session.triage-digest-snapshot.test.ts` → **Test Files 2 passed (2)** with **Tests 9 passed**.
  - `pnpm build` at repo root → exit 0.
- **Patch hygiene:** `git apply --check` on clean checkout at pinned SHA succeeds for `/tmp/0001-telegram-triage-digest-snapshot.patch`; copy stored at `~/openclaw-ops/vps/patches/0001-telegram-triage-digest-snapshot.patch` (17073 bytes; contains `triage-topic-digest-snapshot`, `extensions/telegram/src/bot-message-context.session.ts`).
- **`openclaw-ops`:**
  - `bash -n vps/deploy.sh`, `bash -n vps/build-patched-openclaw.sh` → OK.
  - `./build-patched-openclaw.sh` (from `~/openclaw-ops/vps`) → exit 0; prints tarball path ending in `openclaw-2026.4.12.tgz`.
  - Patched tarball contains env strings (`OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID` / `_PATH`) in emitted `dist` JS bundles (confirmed under `dist/bot-*.js` in scratch build workspace).
- **`deploy.sh`:** Header documents `--with-core` and `docker exec` for tarball install path.

## Human / live (defer to operator)

- **Reproducibility:** Running `./build-patched-openclaw.sh` twice should be compared with `shasum -a 256` on both tarballs once cache is warmed; one sample hash recorded in `02-1-3-02-SUMMARY.md`.
- **VPS grep:** Run README smoke (`grep -rl OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID .../openclaw/dist`) after `OPENCLAW_PACK_TGZ=... ./deploy.sh --with-core --restart`.
- **Large-digest UAT:** Sentinel past **4096** chars in fixture per README.

## Requirement trace

| ID                           | Satisfied                                                                                                   |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| TRIAGE-02.1.3-1..4 (Plan 01) | Digest module + injection + Vitest under `extensions/telegram/src/`; sentinel on missing file; patch export |
| TRIAGE-02.1.3-5..7 (Plan 02) | Pinned `.openclaw-version`, patch in ops, `build-patched-openclaw.sh`, `--with-core` + README runbook       |

## Self-check

Passed automated gates listed above.
