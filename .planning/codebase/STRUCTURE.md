# Repository Structure

**Analysis Date:** 2026-04-02

## Top Level

| Path | Role |
|------|------|
| `src/` | Primary TypeScript source for CLI, gateway, agents, channels, config, infra |
| `extensions/` | Workspace plugin packages (channels, memory, tooling) |
| `packages/` | Additional workspace packages |
| `ui/` | Web UI package (tests/build separate from root Vitest defaults) |
| `apps/` | Native apps: `macos/`, `ios/`, `android/` |
| `docs/` | Mintlify documentation (English source; `docs/zh-CN/` often generated) |
| `scripts/` | Build, release, test harnesses, codegen |
| `test/` | Shared test helpers or legacy test entrypoints (see also colocated `*.test.ts`) |
| `dist/` | Build output (gitignored for dev builds) |
| `skills/` | Shipped skill assets referenced by product |
| `.github/` | CI workflows, templates, labeler |

## `src/` Layout (conceptual)

- `src/cli/` — CLI commands and wiring
- `src/gateway/` — Gateway server and protocol
- `src/agents/` — Agent loop, tools, Pi runner, compaction
- `src/config/` — Configuration and sessions
- `src/web/`, `src/telegram/`, `src/discord/`, `src/slack/`, `src/signal/`, `src/imessage/` — Channel implementations
- `src/channels/`, `src/routing/` — Shared channel abstractions and routing
- `src/auto-reply/` — Auto-reply orchestration (with channel-specific subtrees)
- `src/media/`, `src/media-understanding/` — Media pipeline
- `src/plugin-sdk/` — Plugin SDK implementation and exports
- `src/plugins/` — Core plugin runtime
- `src/infra/`, `src/logging.ts`, `src/process/` — Infrastructure
- `src/wizard/` — Onboarding wizard flows
- `src/tui/` — Terminal UI for interactive flows
- `src/browser/` — Browser-side routes/helpers
- `src/canvas-host/` — Canvas/A2UI host assets
- `src/version.ts` — Version constants

Tests are **colocated** as `*.test.ts`, `*.e2e.test.ts` next to sources.

## `extensions/`

Each subfolder is typically `extensions/<name>/` with `package.json`, `src/`, and optional tests. Channel extensions align with `src/plugin-sdk` subpath exports in root `package.json`.

## Configuration Files (root)

- `package.json` — Scripts, dependencies, `exports` map for `openclaw` and `openclaw/plugin-sdk/*`
- `pnpm-workspace.yaml` — Workspace members
- `tsconfig.json` — Strict TS, path aliases for `openclaw/plugin-sdk`
- `vitest.*.config.ts` — Split test pipelines
- `oxlint` / `oxfmt` — Lint and format
- `knip.config.ts` — Unused code analysis

## Naming Conventions

- **Modules** — ESM `.ts` / `.js` suffix in imports per NodeNext
- **Tests** — `feature.test.ts`, `feature.e2e.test.ts`
- **CLI** — Command modules under `src/commands/` (referenced from `src/cli/`)

---

*Structure analysis: 2026-04-02*
