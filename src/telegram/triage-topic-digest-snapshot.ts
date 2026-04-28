import { existsSync, readFileSync } from "node:fs";
import type { TelegramTopicConfig } from "../config/types.js";

/** Default path on VPS where `openclaw-gws-triage-digest` writes the latest digest. */
export const DEFAULT_TRIAGE_DIGEST_SNAPSHOT_PATH =
  "/data/openclaw-gws/output/triage-digest-latest.md";

/** Cap digest bytes passed into the agent envelope (UTF-8 characters). */
export const TRIAGE_DIGEST_SNAPSHOT_MAX_CHARS = 32_768;

const SNAPSHOT_HEADER = "## Canonical triage digest snapshot (not user message)";

export function resolveTriageDigestSnapshotPath(override?: string): string {
  const trimmed = override?.trim();
  if (trimmed) {
    return trimmed;
  }
  const fromEnv = process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_PATH?.trim();
  if (fromEnv) {
    return fromEnv;
  }
  return DEFAULT_TRIAGE_DIGEST_SNAPSHOT_PATH;
}

export type TriageDigestReadResult =
  | { kind: "ok"; text: string; truncated: boolean; path: string }
  | { kind: "missing"; path: string }
  | { kind: "empty"; path: string };

export function readTriageDigestSnapshot(path: string): TriageDigestReadResult {
  if (!existsSync(path)) {
    return { kind: "missing", path };
  }
  let raw: string;
  try {
    raw = readFileSync(path, "utf8");
  } catch {
    return { kind: "missing", path };
  }
  if (!raw.trim()) {
    return { kind: "empty", path };
  }
  const truncated = raw.length > TRIAGE_DIGEST_SNAPSHOT_MAX_CHARS;
  const text = truncated
    ? `${raw.slice(0, TRIAGE_DIGEST_SNAPSHOT_MAX_CHARS)}\n\n... (truncated)`
    : raw;
  return { kind: "ok", text, truncated, path };
}

export function formatTriageDigestSnapshotSection(result: TriageDigestReadResult): string {
  if (result.kind === "missing") {
    return `${SNAPSHOT_HEADER}\n\n_(triage digest snapshot unavailable: file missing at ${result.path})_`;
  }
  if (result.kind === "empty") {
    return `${SNAPSHOT_HEADER}\n\n_(triage digest snapshot unavailable: file empty at ${result.path})_`;
  }
  return `${SNAPSHOT_HEADER}\n\n${result.text}`;
}

export function shouldInjectTriageDigestSnapshot(params: {
  isForum: boolean;
  chatId: number | string;
  resolvedThreadId: number | undefined;
  topicConfig: TelegramTopicConfig | undefined;
}): boolean {
  if (!params.isForum || typeof params.resolvedThreadId !== "number") {
    return false;
  }
  if (params.topicConfig?.triageDigestSnapshot === true) {
    return true;
  }
  /** VPS/ops opt-in when channel JSON Schema cannot list custom topic keys (AJV footprint). */
  const envChat = process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID?.trim();
  const envTopic = process.env.OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_TOPIC_ID?.trim();
  if (!envChat?.length || !envTopic?.length) {
    return false;
  }
  return String(params.chatId) === envChat && String(params.resolvedThreadId) === envTopic;
}
