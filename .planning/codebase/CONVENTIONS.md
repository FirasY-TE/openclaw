# Coding Conventions

**Analysis Date:** 2026-04-02

## Language and Style

- **TypeScript** — Strict mode; avoid `any`; do not add `@ts-nocheck` or disable `no-explicit-any` without fixing root cause (per `AGENTS.md`).
- **ESM** — `"type": "module"`; prefer `import`/`export`; dynamic import guardrails apply (no mixing static and dynamic import of the same module in production paths without a `*.runtime.ts` boundary).
- **Formatting** — **Oxfmt** for TS/JS; run `pnpm format` / `pnpm format:check`.
- **Linting** — **Oxlint** with type-aware rules: `pnpm lint`; custom guard scripts in `package.json` (`lint:tmp:*`, `lint:plugins:*`, etc.) enforce architectural boundaries.

## Naming

- Product name in docs: **OpenClaw**; CLI binary and package: `openclaw`.
- Files: match existing patterns (`kebab-case` for scripts, `camelCase`/`PascalCase` for TS identifiers per context).

## Patterns and Architecture Rules

- **No prototype mutation** for sharing class behavior — use composition or explicit inheritance (repo guideline).
- **Tests** — Prefer per-instance stubs over mutating `SomeClass.prototype` unless documented.
- **CLI** — Reuse `createDefaultDeps`, `src/cli/progress.ts` for spinners, `src/terminal/table.ts` and `src/terminal/palette.ts` for status tables and colors.
- **Tool schemas** — Avoid `Type.Union` / OpenAPI `anyOf`-style constructs where validators reject them; use string enums per project rules.

## Error Handling

- Central helpers in `src/infra/errors.ts` and related; normalize failures for CLI output.

## Documentation

- Markdown in `docs/` follows Mintlify linking rules (root-relative, no `.md` in links); generic examples (no personal hostnames).

## Commits

- Prefer `scripts/committer` for scoped commits when following maintainer workflow; conventional commit style for messages.

## Swift / Kotlin / Other

- **Swift** — SwiftFormat, SwiftLint configs at repo and app roots.
- **Android** — ktlint via Gradle tasks in `scripts` (`android:lint`, `android:format`).

---

*Conventions analysis: 2026-04-02*
