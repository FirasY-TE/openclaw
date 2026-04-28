import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  DEFAULT_TRIAGE_DIGEST_SNAPSHOT_PATH,
  TRIAGE_DIGEST_SNAPSHOT_MAX_CHARS,
  formatTriageDigestSnapshotSection,
  readTriageDigestSnapshot,
  resolveTriageDigestSnapshotPath,
  shouldInjectTriageDigestSnapshot,
} from "./triage-topic-digest-snapshot.js";

describe("triage-topic-digest-snapshot", () => {
  const prevEnv = process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH;

  afterEach(() => {
    if (prevEnv === undefined) {
      delete process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH;
    } else {
      process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH = prevEnv;
    }
  });

  it("resolveTriageDigestSnapshotPath prefers topic override, then env, then default", () => {
    delete process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH;
    expect(resolveTriageDigestSnapshotPath("/tmp/a.md")).toBe("/tmp/a.md");
    expect(resolveTriageDigestSnapshotPath("  /tmp/b.md  ")).toBe("/tmp/b.md");
    process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH = "/env/path.md";
    expect(resolveTriageDigestSnapshotPath()).toBe("/env/path.md");
    delete process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH;
    expect(resolveTriageDigestSnapshotPath()).toBe(DEFAULT_TRIAGE_DIGEST_SNAPSHOT_PATH);
  });

  it("readTriageDigestSnapshot returns ok with optional truncation", () => {
    const dir = mkdtempSync(join(tmpdir(), "triage-digest-"));
    const p = join(dir, "digest.md");
    try {
      writeFileSync(p, "hello digest", "utf8");
      const ok = readTriageDigestSnapshot(p);
      expect(ok.kind).toBe("ok");
      if (ok.kind !== "ok") {
        throw new Error("expected ok");
      }
      expect(ok.text).toBe("hello digest");
      expect(ok.truncated).toBe(false);

      const big = "x".repeat(TRIAGE_DIGEST_SNAPSHOT_MAX_CHARS + 500);
      writeFileSync(p, big, "utf8");
      const cut = readTriageDigestSnapshot(p);
      expect(cut.kind).toBe("ok");
      if (cut.kind !== "ok") {
        throw new Error("expected ok");
      }
      expect(cut.truncated).toBe(true);
      expect(cut.text).toContain("... (truncated)");
      expect(cut.text.length).toBeLessThanOrEqual(TRIAGE_DIGEST_SNAPSHOT_MAX_CHARS + 80);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("readTriageDigestSnapshot handles missing and empty files", () => {
    expect(readTriageDigestSnapshot(join(tmpdir(), "nope-absent-123.md")).kind).toBe("missing");

    const dir = mkdtempSync(join(tmpdir(), "triage-digest-empty-"));
    const p = join(dir, "empty.md");
    try {
      writeFileSync(p, "   \n  ", "utf8");
      expect(readTriageDigestSnapshot(p).kind).toBe("empty");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("formatTriageDigestSnapshotSection preserves sentinel wording", () => {
    const tmp = mkdtempSync(join(tmpdir(), "snap-fmt-"));
    const absent = "/no/such/path/triage.md";
    expect(formatTriageDigestSnapshotSection({ kind: "missing", path: absent })).toContain(absent);

    expect(formatTriageDigestSnapshotSection({ kind: "empty", path: join(tmp, "e.md") })).toContain(
      "file empty",
    );

    const p = join(tmp, "d.md");
    writeFileSync(p, "# Title\nBody", "utf8");
    const ok = readTriageDigestSnapshot(p);
    if (ok.kind !== "ok") {
      throw new Error("expected ok");
    }
    const section = formatTriageDigestSnapshotSection(ok);
    expect(section).toContain("Canonical triage digest snapshot");
    expect(section).toContain("# Title");

    rmSync(tmp, { recursive: true, force: true });
  });

  const sampleChat = "-1003943940218";

  it("shouldInjectTriageDigestSnapshot is opt-in via topic config or VPS env match", () => {
    expect(
      shouldInjectTriageDigestSnapshot({
        isForum: true,
        chatId: sampleChat,
        resolvedThreadId: 9,
        topicConfig: { triageDigestSnapshot: true },
      }),
    ).toBe(true);
    expect(
      shouldInjectTriageDigestSnapshot({
        isForum: false,
        chatId: sampleChat,
        resolvedThreadId: 9,
        topicConfig: { triageDigestSnapshot: true },
      }),
    ).toBe(false);
    expect(
      shouldInjectTriageDigestSnapshot({
        isForum: true,
        chatId: sampleChat,
        resolvedThreadId: undefined,
        topicConfig: { triageDigestSnapshot: true },
      }),
    ).toBe(false);
    expect(
      shouldInjectTriageDigestSnapshot({
        isForum: true,
        chatId: sampleChat,
        resolvedThreadId: 9,
        topicConfig: {},
      }),
    ).toBe(false);
  });

  it("shouldInjectTriageDigestSnapshot matches OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID and _TOPIC_ID", () => {
    const prevChat = process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID;
    const prevTopic = process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID;
    try {
      process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID = sampleChat;
      process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID = "9";
      expect(
        shouldInjectTriageDigestSnapshot({
          isForum: true,
          chatId: Number(sampleChat),
          resolvedThreadId: 9,
          topicConfig: {},
        }),
      ).toBe(true);
      expect(
        shouldInjectTriageDigestSnapshot({
          isForum: true,
          chatId: "-100111",
          resolvedThreadId: 9,
          topicConfig: {},
        }),
      ).toBe(false);
    } finally {
      if (prevChat === undefined) {
        delete process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID;
      } else {
        process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID = prevChat;
      }
      if (prevTopic === undefined) {
        delete process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID;
      } else {
        process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID = prevTopic;
      }
    }
  });
});
