# Areas of Concern

**Analysis Date:** 2026-04-02

## Scale and Complexity

- **Large monorepo** — Thousands of files under `src/` alone; changes to shared routing, pairing, or allowlists must consider **all** built-in and extension channels (per `AGENTS.md`).
- **Many Vitest configs** — Easy to run the wrong suite locally; verify CI-equivalent commands when debugging failures.

## Correctness and State

- **Gateway / plugin startup** — `src/gateway/server-plugins.ts` notes that startup snapshots can become stale if runtime config changes (TODO in source).
- **Agent compaction** — `src/agents/pi-embedded-runner/compact.ts` carries issue-linked TODOs for future injection of snapshots/summaries around compaction.

## Security

- **Secrets** — Never commit tokens, phone numbers, or live config; docs and tests use placeholders.
- **Webhook and auth ordering** — Custom lint `lint:webhook:no-low-level-body-read` exists to prevent auth/body-order bugs.
- **Pairing / auth scope** — Dedicated checks: `lint:auth:no-pairing-store-group`, `lint:auth:pairing-account-scope`.

## Dependency and Build

- **pnpm patches** — Patched dependencies require exact versions and explicit approval to change.
- **Native / heavy deps** — `pnpm-workspace.yaml` `onlyBuiltDependencies` lists packages needing native builds (canvas, crypto, baileys, etc.) — CI and local dev can fail if toolchains are missing.

## Platform-Specific

- **macOS app** — Gateway lifecycle tied to menubar app in common setups; debugging docs warn against ad-hoc tunnels and assumptions about launchd labels.

## Documentation Drift

- **i18n** — `docs/zh-CN/**` is generated; editing English first avoids divergence.

## Extension Ecosystem

- **npm vs workspace** — Extensions must not use `workspace:*` in published `dependencies`; runtime resolves `openclaw/plugin-sdk` via documented patterns.

---

*Concerns analysis: 2026-04-02*
