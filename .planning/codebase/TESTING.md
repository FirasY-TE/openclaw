# Testing

**Analysis Date:** 2026-04-02

## Framework

- **Vitest** `^4.0.18` — Primary unit, integration, e2e, and gateway tests.
- **Coverage** — `@vitest/coverage-v8`; thresholds enforced (see `AGENTS.md` for ~70% targets).

## Test Layout

- **Colocated tests** — `*.test.ts` beside source files; `*.e2e.test.ts` for end-to-end style suites.
- **Multiple configs** — Split by concern to keep CI fast and focused:
  - `vitest.unit.config.ts` — Broad unit/default
  - `vitest.gateway.config.ts` — Gateway (often `--pool=forks`)
  - `vitest.e2e.config.ts` — E2E
  - `vitest.channels.config.ts` — Channel-focused
  - `vitest.extensions.config.ts` — Extensions workspace
  - `vitest.live.config.ts` — Live tests (real keys; env-gated)

## Running Tests

| Command | Purpose |
|---------|---------|
| `pnpm test` | Parallel runner via `scripts/test-parallel.mjs` |
| `pnpm test:fast` | Unit config quick run |
| `pnpm test:coverage` | Coverage on unit config |
| `pnpm test:gateway` | Gateway suite |
| `pnpm test:e2e` | E2E config |
| `pnpm test:live` | Live tests (requires env flags) |
| `pnpm test:docker:*` | Docker-based integration scripts |

## Resource-Constrained Runs

- `OPENCLAW_TEST_PROFILE=low` and `OPENCLAW_TEST_SERIAL_GATEWAY=1` documented for memory pressure on smaller hosts.

## UI Package

- `ui/package.json` runs `vitest run --config vitest.config.ts` with optional Playwright browser tooling (`@vitest/browser-playwright`).

## Mobile

- **Android** — `./gradlew` tasks via `android:test` scripts.
- **iOS** — Xcode build/test via scripts in `package.json` (`ios:build`, etc.).

## Pre-Commit / CI

- `pnpm check` aggregates format, `tsgo`, lint, and custom guard scripts (see root `package.json`).
- `prek install` mentioned in docs for hook parity with CI.

---

*Testing analysis: 2026-04-02*
