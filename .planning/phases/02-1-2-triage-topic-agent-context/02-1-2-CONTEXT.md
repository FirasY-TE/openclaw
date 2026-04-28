# Phase 02.1.2 — Triage Topic Agent Context + ByteRover In-Container

**Parent phases:** 02.1 (Plan C pivot), 02.1.1 (digest rendering + inline body)

**Opened:** gap closure after live-UAT surfaced that **inline markdown in the digest does not reliably reach Bella’s inbound agent context** in the Telegram Forum triage topic. Session evidence (VPS `topic-9` JSONL):

- Bella reported “I don’t have the digest items in this chat history” despite the digest landing in the same topic minutes earlier — **Plan C’s conversational thesis fails at runtime**.
- Fallback tools (`byterover`, `brv providers connect`, `memory_search`) returned **auth failures or empty hits** (`ByteRover Provider requires authentication`, `results: []`), so the agent could not hydrate context from secondary memory instead of Telegram history.
- A separate nuisance: duplicate processing of the same `message_id` produced repeated drafts and triggered watchdog “plan-only turns” termination — tracked as follow-up QA, not prerequisite for fixing context injection.

Phase 02.1.2 closes the loop with **two parallel concerns**:

1. **Deterministic digest context:** inject the canonical digest markdown (same file the digest script writes) into the agent-facing inbound envelope when the Telegram message resolves to the configured triage Forum topic thread (`topic_id`).
2. **Healthy ByteRover in-container:** ensure `brv` / ByteRover provider auth works **inside the same OpenClaw container and workspace cwd** Bella uses, so auxiliary memory tooling stops failing loudly (not a substitute for (1)).

## Requirements

- **TRIAGE-02.1.2-1**: For inbound Telegram Forum messages whose resolved thread maps to the **Triage Digest** topic (per config/env), the assembled inbound context Bella receives MUST include bounded content read from `/data/openclaw-gws/output/triage-digest-latest.md` (or config override path). Document cap (chars), ordering (system vs appended user preamble), and behavior when file missing/outdated.
- **TRIAGE-02.1.2-2**: Inside `openclaw-ridl-openclaw-1`, `brv providers connect byterover` (from `/data/.openclaw/workspace` or documented cwd) exits success; optional smoke query validates retrieval. Credentials stored only via compose secrets / vault, never committed.
- **TRIAGE-02.1.2-3 (process):** Intended-for-VPS execution follows openclaw-ops canonical flow: upstream-friendly TypeScript lands in **this repo** (`openclaw/`); VPS deployment rolls through `openclaw-ops/vps/` patch + `./deploy.sh --with-core --restart` when touching core Telegram wiring (per `.cursor/rules/vps-ssh-openclaw.mdc`).

## Success criteria

- Operator asks `summary`, `draft <name>`, or `ignore <name>` in the triage topic **without pasting digest** → Bella cites items from **the same digest markdown** surfaced in-context (verbatim subject lines acceptable).
- `memory_search` / ByteRover may still augment context but MUST NOT be the only source of digest truth.
- `brv` no longer emits “ByteRover Provider requires authentication” for the canonical connect path Bella’s tools use after login is applied in-container.

## Not in scope

- Replacing inline digest format from 02.1.1 (keep as-is unless this phase discovers a sizing bug).
- Fixing Telegram duplicate-delivery watchdog edge as a blocker (optional follow-up if still reproducible after context injection).
