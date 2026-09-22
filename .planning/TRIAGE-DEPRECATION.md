# Triage digest — DEPRECATED (2026-09-21)

**Status:** End-of-day triage digest job and related OpenClaw patches are **deprecated**. Do not extend or invest in this stack.

## Why deprecated

1. **Drift from original vision** — Operator wanted a daily summary of **all** emails and messages, with important items highlighted and actions (calendar, reminder, respond). What shipped was a narrow end-of-day digest with token/`tdr` finalization, poor Telegram UX, and strict filters that missed real items.
2. **OpenClaw upgrade friction** — Digest-in-thread behavior required a **patched OpenClaw core** (`OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_*`, `openclaw-ops/vps/patches/0001-telegram-triage-digest-snapshot.patch`, `deploy.sh --with-core`). Vanilla upstream upgrades are blocked or risky while this patch is required.
3. **Low operator value** — Batch digest in the Triage Digest topic overlapped morning brief delivery surface without delivering a scannable unified inbox.

## Original vision (successor work)

Captured in backlog **Phase 999.5**:

- One daily (or on-demand) **unified summary** across Gmail, Hospitable, later Beeper
- **All** items visible; importance highlighted (not silently dropped)
- Per-item actions: **add to calendar**, **reminder/task**, **respond** (draft + approve)
- Built on **prepared pipeline files** + **OpenClaw cron agent** (morning-brief pattern) — **no patched core**

## What to turn off (VPS — `openclaw-ops`)

Source of truth: `~/openclaw-ops/vps/`. Reconcile any hot-edits back to the repo.

### 1. Host cron — triage digest

In `vps/cron/openclaw-gws`, **comment out or remove** the block:

```cron
# DEPRECATED 2026-09-21 — end-of-day triage digest
# 30 16 * * *
# CRON_TZ=America/Chicago
# ... openclaw-gws-triage-digest ...
```

Deploy: `cd ~/openclaw-ops/vps && ./deploy.sh --cron`

**Or run the all-in-one script** (cron + live `.env` cleanup + vanilla npm upgrade + recreate):

```bash
cd ~/openclaw-ops/vps && ./deprecate-triage-and-upgrade-vanilla.sh
```

### 2. Compose env — digest snapshot patch hooks

Remove or comment in `vps/compose/.env` (and `.env.example` notes):

- `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID`
- `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID`
- `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH` (if set)

Redeploy compose; **next OpenClaw upgrade can use vanilla npm** without `--with-core` for triage snapshot.

### 3. Optional — stop shipping patched core for triage only

If no other patches remain on `vps/patches/`, drop `0001-telegram-triage-digest-snapshot.patch` and pin to stock OpenClaw on VPS (`deploy.sh` without `--with-core`).

### 4. Do not remove yet (reuse in 999.5)

- Gmail review / action scripts (`openclaw-gws-review*`, `openclaw-gws-act*`)
- `openclaw-gws-triage-reply` (`tdr`) — Gmail send/draft finalization
- `ROUTE_TRIAGE_DIGEST_TARGET` — still used by **morning brief** and **evening reset** (topic name is legacy; routing still valid)
- Hospitable fetch, rental merge, morning brief cron

## Deprecated in this repo (keep for reference; no new work)

| Asset                      | Location                                                       |
| -------------------------- | -------------------------------------------------------------- |
| Digest builder             | `scripts/deploy/lib/triage_digest_build.py`                    |
| Digest cron script         | `scripts/deploy/openclaw-gws-triage-digest`                    |
| CLI                        | `src/cli/triage-cli.ts`, `src/gws-triage/run-triage-digest.ts` |
| Telegram `/triage`         | `src/telegram/bot-native-commands.ts`                          |
| Digest snapshot (upstream) | `src/telegram/triage-topic-digest-snapshot.ts`                 |
| Runbook                    | `scripts/deploy/prompts/triage-draft-runbook.md`               |
| Backlog 999.1–999.3        | Digest-only improvements — **obsolete**                        |

## Verification after shutdown

```bash
# No triage digest cron firing
ssh openclaw-vps "grep -i triage /etc/cron.d/openclaw-gws || true"

# Morning brief still works (uses same topic route name)
ssh openclaw-vps "docker exec openclaw-ridl-openclaw-1 openclaw cron run ce3cf461-3e58-49f0-8e64-e0b2b7b873bb --timeout 180000"
```

---

_Deprecated: 2026-09-21. Successor: ROADMAP backlog Phase 999.5._
