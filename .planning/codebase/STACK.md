# Technology Stack

**Analysis Date:** 2026-04-02

## Languages

**Primary:**

- **TypeScript** — Application logic under `src/`, `extensions/*/src/`, `ui/`. Strict mode (`tsconfig.json`), ESM (`"type": "module"`), NodeNext resolution.

**Secondary:**

- **Swift** — macOS (`apps/macos/`), iOS (`apps/ios/`), shared kit (`apps/shared/OpenClawKit/`). SwiftFormat / SwiftLint in CI scripts.
- **Kotlin** — Android app (`apps/android/`).
- **Shell / Node scripts** — Build and test orchestration in `scripts/`.

## Runtime

**Environment:**

- **Node.js** — Target ES2023; repo docs specify Node **22+** for development and production CLI use.
- **Bun** — Supported for running scripts and tests (`bun`, `bunx`) alongside pnpm.

**Package Manager:**

- **pnpm** — Workspace root; lockfile `pnpm-lock.yaml`.
- **Workspace layout** — `pnpm-workspace.yaml` includes root `.`, `ui`, `packages/*`, `extensions/*`.

## Frameworks and Tooling

**Core:**

- **CLI** — Entry via `openclaw.mjs` and `scripts/run-node.mjs`; program built in `src/cli/program.ts` and related `src/cli/`.
- **Build** — `scripts/tsdown-build.mjs` (esbuild-based bundling to `dist/`), plugin SDK DTS generation, assorted post-build copy/write scripts in `package.json` `build` script.

**Lint / format:**

- **Oxlint** (`oxlint --type-aware`) — Primary linter.
- **Oxfmt** — Formatter (`oxfmt`); docs Markdown also formatted with oxfmt where scripted.

**Testing:**

- **Vitest** `^4.0.18` — Multiple configs: `vitest.unit.config.ts`, `vitest.gateway.config.ts`, `vitest.e2e.config.ts`, `vitest.channels.config.ts`, `vitest.extensions.config.ts`, `vitest.live.config.ts`, etc.
- **Coverage** — `@vitest/coverage-v8` with thresholds referenced in repo guidelines.

**UI (workspace package):**

- **`ui/`** — Separate package with its own `package.json` and Vitest config for browser/UI tests.

## Key Dependencies

**Critical (representative):**

- Channel and messaging libraries vary by integration (e.g. WhatsApp web stack under `src/web/`, other channels under `src/telegram`, `src/discord`, etc.).
- **Plugin system** — `src/plugin-sdk/` with many subpath exports in root `package.json` `exports` for extensions.

**Build / dev:**

- **TypeScript** — `noEmit: true` for typecheck; emit via tsdown for distribution.
- **tsx** — Script execution for many `node --import tsx` tooling scripts.

## Configuration

**Environment:**

- Dotenv loading via `src/infra/dotenv.ts` (called early from `src/index.ts`).
- User/runtime config under OpenClaw config paths (see docs); not duplicated here.

**Build:**

- `tsconfig.json`, `tsconfig.plugin-sdk.dts.json`, various Vitest configs, `knip.config.ts`, Swift/Xcode projects under `apps/`.

## Platform Requirements

**Development:**

- macOS emphasized for iOS/macOS apps and some gateway workflows; Linux common for CI and headless gateway.
- **Docker** — Used in scripted integration tests (`test:docker:*` scripts).

**Production:**

- **npm package** `openclaw` — CLI and gateway usage on user machines or servers; mobile apps distributed via respective store/build pipelines.

---

*Stack analysis: 2026-04-02*
