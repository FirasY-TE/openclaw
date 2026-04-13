# External Integrations

**Analysis Date:** 2026-04-02

This document summarizes categories of external systems the codebase talks to. Exact credentials and endpoints belong in user config and docs, not in this map.

## Messaging and Channels

**Built-in (core `src/`):**

- **Web / WhatsApp** — `src/web/` (session, login, QR, inbound/outbound, auto-reply pipeline).
- **Telegram** — `src/telegram/`.
- **Discord** — `src/discord/`.
- **Slack** — `src/slack/`.
- **Signal** — `src/signal/`.
- **iMessage** — `src/imessage/`.
- **Shared routing and plugins** — `src/channels/`, `src/routing/`, `src/channels/plugins/`.

**Extension packages (`extensions/`):**

Examples include `matrix`, `msteams`, `line`, `googlechat`, `irc`, `nostr`, `zalo`, `zalouser`, `voice-call`, `bluebubbles`, `nextcloud-talk`, `synology-chat`, `twitch`, `tlon`, `feishu`, `telegram`, `discord`, `slack`, `signal`, `imessage`, `whatsapp`, and supporting plugins (`memory-core`, `memory-lancedb`, `diagnostics-otel`, `copilot-proxy`, etc.). Each extension has its own `package.json` and implements the plugin SDK surface.

## AI / LLM Providers

- **Provider and model routing** — Centralized in areas such as `src/agents/`, `src/auto-reply/`, `src/media-understanding/` (multiple provider folders under `media-understanding/providers/`).
- **Web provider login** — `src/provider-web.ts` and credentials layout documented in repo guidelines (`~/.openclaw/credentials/`).

## Infrastructure and Tooling

- **Gateway protocol** — JSON schema and codegen: `scripts/protocol-gen.ts`, `dist/protocol.schema.json`, Swift models under `apps/macos/Sources/OpenClawProtocol/`.
- **Observability** — Optional OpenTelemetry-related extension (`extensions/diagnostics-otel`).
- **Canvas / A2UI** — Bundling via `scripts/bundle-a2ui.sh`, `pnpm canvas:a2ui:bundle`, hash in `src/canvas-host/a2ui/.bundle.hash`.

## Docs and Web

- **Mintlify** — Docs under `docs/`; local preview `pnpm docs:dev` (`cd docs && mint dev`).
- **Installers** — Referenced from repo guidelines as living in sibling `openclaw.ai` repo (not this tree).

## Third-Party APIs (conceptual)

- Channel-specific APIs (bot tokens, webhooks, OAuth) are configured per channel; implementation is spread across channel modules and extensions.
- **No secrets** should appear in this file; integration names and file areas are for navigation only.

---

*Integrations map: 2026-04-02*
