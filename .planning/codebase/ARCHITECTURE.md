# Architecture

**Analysis Date:** 2026-04-02

## Product Shape

**OpenClaw** is a **multi-channel AI gateway**: a CLI and long-running services connect messaging surfaces to agent/LLM workflows, with optional desktop and mobile apps for control and delivery.

## Major Components

**CLI and entrypoint**

- `src/index.ts` — Bootstraps env, logging, runtime guard, then `buildProgram()` from `src/cli/program.ts`.
- `src/cli/` — Command registration, deps injection (`createDefaultDeps`), progress UI (`src/cli/progress.ts`), gateway/agent/canvas commands.

**Gateway**

- `src/gateway/` — Server, protocol, sessions, and gateway-specific behavior (large surface area; see `src/gateway/server-plugins.ts` and related modules).

**Agents and execution**

- `src/agents/` — Agent runtime, Pi-related embedding, compaction, tool use, sessions.
- `src/auto-reply/` — Pipelines tying inbound messages to replies (channel-specific glue in subfolders, e.g. `src/web/auto-reply/`).

**Configuration and state**

- `src/config/` — Config load/merge, sessions store paths.
- **Sessions** — `src/config/sessions.ts` and on-disk layout documented in product docs.

**Media**

- `src/media/` and `src/media-understanding/` — Ingest, transforms, provider-specific understanding.

**Plugins**

- `src/plugins/runtime/` — Plugin host wiring.
- `src/plugin-sdk/` — SDK consumed by `extensions/*` packages (published as `openclaw/plugin-sdk` subpaths).

**Web and browser**

- `src/browser/` — Routes and helpers for embedded/web surfaces where applicable.

**Cross-cutting**

- `src/infra/` — Ports, env, binaries, errors, dotenv.
- `src/routing/` — Message routing and policy.
- `src/terminal/` — Tables, palette, CLI presentation.

## Data Flow (high level)

1. **Inbound** — Channel adapter (e.g. `src/web/inbound/`, `src/telegram/`) receives message → routing / auth / allowlists → agent or auto-reply pipeline → **outbound** reply on same or paired channel.
2. **Gateway** — Clients (apps, local tools) may use gateway protocol over configured transports; see `src/gateway/protocol/`.
3. **Config** — Loaded at startup; sensitive values from env and credential stores, not from this repo.

## Build and Deliverables

- **TypeScript** sources compile/bundle to `dist/` for the published package.
- **Extensions** are separate workspace packages; some ship to npm as `@openclaw/*` per release docs.
- **Apps** — `apps/macos`, `apps/ios`, `apps/android` consume gateway/protocol and ship as native bundles.

## Extension Model

- Extensions implement channel or feature plugins using `openclaw/plugin-sdk` path aliases from `tsconfig.json`.
- Core must remain channel-agnostic where shared behavior (routing, pairing, allowlists) applies; see repo guidelines when changing shared logic.

---

*Architecture analysis: 2026-04-02*
