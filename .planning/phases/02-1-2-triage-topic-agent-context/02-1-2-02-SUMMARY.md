---
phase: 02-1-2-triage-topic-agent-context
plan: "02"
status: completed
completed: "2026-04-29"
---

## Outcome

- **`BYTEROVER_API_KEY`** documented in `vps/compose/.env.example` with placeholder-only value (`REPLACE_ME_*`). Live keys stay in `/docker/openclaw-ridl/.env` on the VPS.
- **`vps/README.md`** runbook: load `.env`, `brv login --api-key` + `brv providers connect byterover` as `runuser -u node` with stable `HOME=/data/.openclaw/workspace`; smoke command for regressions.

## ByteRover / compose inventory (April 2026)

| Item            | Observation                                                                                                 |
| --------------- | ----------------------------------------------------------------------------------------------------------- |
| `brv` binary    | Present at `/data/.brv-cli/bin/brv` inside `openclaw-ridl-openclaw-1`                                       |
| Compose         | `docker-compose.yml` uses `env_file: .env` — vars from deployed `.env` map into the container automatically |
| Pre-login probe | `brv providers connect byterover` prints `ByteRover Provider requires authentication` until login succeeds  |

## Operator follow-up

- Set `channels.telegram.groups.<chatId>.topics.<triage_digest_thread>.triageDigestSnapshot: true` in OpenClaw config on the VPS (thread id aligns with `ROUTE_TRIAGE_DIGEST_TARGET` routing).
- Add real `BYTEROVER_API_KEY` to VPS compose `.env`, recreate, execute README login/connect block once.

## Self-Check

## Self-Check: PASSED
