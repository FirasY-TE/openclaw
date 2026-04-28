import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { loadConfig } from "../config/config.js";
import { buildTelegramMessageContextForTest } from "./bot-message-context.test-harness.js";

const { defaultRouteConfig } = vi.hoisted(() => ({
  defaultRouteConfig: {
    agents: {
      list: [{ id: "main", default: true }, { id: "zu" }],
    },
    channels: { telegram: {} },
    messages: { groupChat: { mentionPatterns: [] } },
  },
}));

vi.mock("../config/config.js", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../config/config.js")>();
  return {
    ...actual,
    loadConfig: vi.fn(() => defaultRouteConfig),
  };
});

describe("buildTelegramMessageContext triage digest snapshot injection", () => {
  const prevEnv = process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH;

  beforeEach(() => {
    vi.mocked(loadConfig).mockReturnValue(defaultRouteConfig as never);
  });

  afterEach(() => {
    if (prevEnv === undefined) {
      delete process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH;
    } else {
      process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH = prevEnv;
    }
  });

  function buildForumMessage(threadId = 9) {
    return {
      message_id: 12,
      chat: {
        id: -1001234567890,
        type: "supergroup" as const,
        title: "Forum",
        is_forum: true,
      },
      date: 1700000000,
      text: "summary",
      message_thread_id: threadId,
      from: { id: 42, first_name: "Alice" },
    };
  }

  it("prepends digest markdown when topic opts in and file exists", async () => {
    const dir = mkdtempSync(join(tmpdir(), "triage-inject-"));
    const digestPath = join(dir, "latest.md");
    try {
      writeFileSync(digestPath, "## Needs\n- item A", "utf8");
      process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH = digestPath;

      const ctx = await buildTelegramMessageContextForTest({
        message: buildForumMessage(9),
        options: { forceWasMentioned: true },
        resolveGroupActivation: () => true,
        resolveTelegramGroupConfig: () => ({
          groupConfig: { requireMention: false },
          topicConfig: { triageDigestSnapshot: true },
        }),
      });

      expect(ctx?.ctxPayload.BodyForAgent).toContain("Canonical triage digest snapshot");
      expect(ctx?.ctxPayload.BodyForAgent).toContain("item A");
      expect(ctx?.ctxPayload.BodyForAgent).toContain("summary");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("injects explicit unavailable line when snapshot file is missing", async () => {
    process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH = join(tmpdir(), "missing-triage-md-xyz.md");

    const ctx = await buildTelegramMessageContextForTest({
      message: buildForumMessage(9),
      options: { forceWasMentioned: true },
      resolveGroupActivation: () => true,
      resolveTelegramGroupConfig: () => ({
        groupConfig: { requireMention: false },
        topicConfig: { triageDigestSnapshot: true },
      }),
    });

    expect(ctx?.ctxPayload.BodyForAgent).toContain("triage digest snapshot unavailable");
    expect(ctx?.ctxPayload.BodyForAgent).toContain("file missing");
  });

  it("does not inject when triageDigestSnapshot is false", async () => {
    const ctx = await buildTelegramMessageContextForTest({
      message: buildForumMessage(9),
      options: { forceWasMentioned: true },
      resolveGroupActivation: () => true,
      resolveTelegramGroupConfig: () => ({
        groupConfig: { requireMention: false },
        topicConfig: { triageDigestSnapshot: false },
      }),
    });

    expect(ctx?.ctxPayload.BodyForAgent).not.toContain("Canonical triage digest snapshot");
  });

  it("does not inject when topic config omits triageDigestSnapshot", async () => {
    const ctx = await buildTelegramMessageContextForTest({
      message: buildForumMessage(9),
      options: { forceWasMentioned: true },
      resolveGroupActivation: () => true,
      resolveTelegramGroupConfig: () => ({
        groupConfig: { requireMention: false },
        topicConfig: { systemPrompt: "x" },
      }),
    });

    expect(ctx?.ctxPayload.BodyForAgent).not.toContain("Canonical triage digest snapshot");
  });
});
