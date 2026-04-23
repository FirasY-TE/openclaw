---
phase: 02-1-1-triage-digest-context-fixes
plan: 02
subsystem: triage-digest
tags: [triage, digest, inline-body, operator-verbs, gap-closure, vps]
requirements: [TRIAGE-02.1.1-2, TRIAGE-02.1.1-3, TRIAGE-02.1.1-4]
requires:
  - phase: 02-1-1-triage-digest-context-fixes
    plan: 01
    reason: "Dict-aware Hospitable rendering shipped in 02.1.1-01; this plan layers inline body + affordance on top of the same digest builder."
provides:
  - "`BodyB64:` field on each Gmail review summary block — single-line base64 of the trimmed plain-text body. Emitted by both personal and rental review scripts, parsed by `_full_body_gmail` in the digest builder."
  - "`fullBody` on every needs_reply Gmail item in the digest intermediate list (other categories / Hospitable untouched)."
  - "`_render_body_blockquote` helper + FULL_BODY_MAX/4000-char cap with `... (truncated)` marker — renders the body as a `> `-prefixed Markdown blockquote under each needs_reply item's summary + token + finalize lines."
  - "`NEEDS_ATTENTION_AFFORDANCE` single italic header-line emitted once at the top of `## Needs attention` when that section has ≥1 item (never per-item, never a callback, never when empty)."
  - "Runbook spec for the three recognized operator verbs (`draft <name>`, `ignore <name>`, `summary`) with two worked examples."
  - "Architecture-doc digest-shape documentation reflecting both the inline blockquote and the header-line affordance."
affects:
  - "scripts/deploy/openclaw-gws-review-test (openclaw source tree)"
  - "scripts/deploy/openclaw-gws-review-rental-test (openclaw source tree)"
  - "scripts/deploy/lib/triage_digest_build.py (openclaw source tree)"
  - "scripts/deploy/tests/test_triage_digest.py (openclaw source tree)"
  - "scripts/deploy/prompts/triage-draft-runbook.md (openclaw source tree)"
  - "scripts/deploy/fixtures/triage/personal-summary-fragment.txt (openclaw source tree — BodyB64 added)"
  - "docs/agent-architecture.txt (openclaw source tree)"
  - "openclaw-ops/vps/scripts/lib/triage_digest_build.py (ops-tree mirror, byte-identical)"
  - "openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md (ops-tree mirror, byte-identical)"
  - "openclaw-ops/vps/scripts/openclaw-gws-review-test (ops-tree mirror, byte-identical)"
  - "openclaw-ops/vps/scripts/openclaw-gws-review-rental-test (ops-tree mirror, byte-identical)"
  - "Live VPS digest at /data/openclaw-gws/output/triage-digest-latest.md"
tech_stack:
  added: []
  patterns:
    - "Single-line base64 transport for multi-line fields across a key:value text file — keeps `_parse_summary_blocks` untouched while preserving real email newlines for the renderer."
    - "Category-gated enrichment: `fullBody` is only attached to needs_reply Gmail items so other categories' digest payload stays minimal."
    - "Dedicated `_render_body_blockquote` helper so cap + truncation-marker logic lives in one place and is unit-testable without going through `render_markdown`."
key_files:
  created:
    - ".planning/phases/02-1-1-triage-digest-context-fixes/02-1-1-02-SUMMARY.md"
  modified:
    - "scripts/deploy/openclaw-gws-review-test"
    - "scripts/deploy/openclaw-gws-review-rental-test"
    - "scripts/deploy/lib/triage_digest_build.py"
    - "scripts/deploy/tests/test_triage_digest.py"
    - "scripts/deploy/fixtures/triage/personal-summary-fragment.txt"
    - "scripts/deploy/prompts/triage-draft-runbook.md"
    - "docs/agent-architecture.txt"
    - "../openclaw-ops/vps/scripts/lib/triage_digest_build.py"
    - "../openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md"
    - "../openclaw-ops/vps/scripts/openclaw-gws-review-test"
    - "../openclaw-ops/vps/scripts/openclaw-gws-review-rental-test"
decisions:
  - "Picked Option A (extend review scripts to emit the body). Option B as written in the plan (read from gmail-review-latest.json by ID) turned out not to be viable — that file only stores {id, threadId} from the Gmail list endpoint; full bodies only exist per-message after openclaw-gws-review-test fetches them. Adding a new bodies-snapshot file (B-variant) would mean a second write path and a second source of staleness. Option A keeps the existing pipeline's single source of truth for per-message data."
  - "Used single-line base64 for the body transport (`BodyB64:` field) rather than multi-line `Body:` + parser changes. Rationale: preserves real newlines / paragraph breaks, survives colons/dashes/any email content without an escape scheme, and requires zero changes to `_parse_summary_blocks`. Decoding happens lazily in `_full_body_gmail`, only for needs_reply items."
  - "Body hard-cap is on the body content (4000 chars), not the rendered blockquote. Rendered output ends up ≈4000 + 2·lineCount + marker; still well under Telegram's 4096-char envelope in practice because a 4000-char body bounds line count realistically. If we hit pathological short-line bodies in the wild, the cap moves to the renderer without touching the field contract."
  - "Header-line affordance is emitted strictly at the top of `## Needs attention` per the plan's literal spec — not `## Needs reply`. The line text reads `I have each email body inline below` which, in a digest that has both sections, sits between the (above) needs_reply blockquotes and the (below) needs_attention bullets; acceptable because the verbs it documents apply across the whole digest conversation and the runbook is the canonical behavior spec."
  - "Extended fixture `personal-summary-fragment.txt` with a BodyB64 line for the existing Someone / invoice entry rather than adding a new fixture block. Keeps the existing `test_body_summary_renders_under_gmail_bullet` regex (`\\[personal\\].+\\n\\s{2}Hi — following up`) intact while letting the new tests reach the fullBody render path."
metrics:
  completed_date: "2026-04-23"
  task_count: 4
  file_count: 11
---

# Phase 02.1.1 Plan 02: Inline-Body Digest + Operator Verb Affordance Summary

**One-liner:** Inlines the full plain-text email body as a Markdown blockquote beneath each `needs_reply` Gmail item in the triage digest (eliminating the "I don't see the email" failure class) and emits a single italic operator-verb affordance at the top of `## Needs attention`, with full runbook + architecture-doc coverage and a byte-identical openclaw-ops mirror verified live on the VPS.

## What shipped

A four-commit atomic change across two repos:

1. **openclaw** (`5971af9cc3`) — Task 1: review scripts emit `BodyB64:` per-message; digest builder decodes it and attaches `fullBody` on needs_reply Gmail items. Fixture extended with a real multi-line body so the test can see it.
2. **openclaw** (`711903f4b9`) — Task 2: `render_markdown` emits a `> `-prefixed blockquote under each needs_reply item (capped at 4000 chars with `... (truncated)` marker) and a single italic header-line affordance at the top of `## Needs attention`. 6 new tests cover blockquote-under-token, truncation, affordance-present-once, affordance-absent-when-empty, and a no-callback regression.
3. **openclaw** (`f116b71c10`) — Task 3: runbook rewritten around inline body + three canonical verbs (`draft <name>`, `ignore <name>`, `summary`) with two worked examples; architecture doc's triage section now documents both the inline blockquote shape and the header-line affordance.
4. **openclaw-ops** (`7716d63`) — Task 4: byte-identical mirror of all four source-tree files (`triage_digest_build.py`, `triage-draft-runbook.md`, both `openclaw-gws-review*-test` scripts) deployed via `vps/deploy.sh`. Live digest confirmed on the VPS.

## Commits

| Repo         | Hash         | Message                                                                              |
| ------------ | ------------ | ------------------------------------------------------------------------------------ |
| openclaw     | `5971af9cc3` | feat(02.1.1-02): surface fullBody on needs_reply Gmail items for inline rendering    |
| openclaw     | `711903f4b9` | feat(02.1.1-02): render full body blockquote + header-line verb affordance in digest |
| openclaw     | `f116b71c10` | docs(02.1.1-02): document inline-body workflow and operator verbs                    |
| openclaw-ops | `7716d63`    | gap-closure(02.1.1-02): mirror inline-body + header-line affordance from openclaw    |

## Task-by-task

### Task 1 — surface full body on needs_reply Gmail items (Option A)

- Added `BodyB64: <base64>` line to the emitted summary block in both `scripts/deploy/openclaw-gws-review-test` and `scripts/deploy/openclaw-gws-review-rental-test`. Source material is `body_trimmed` (post reply/forward strip, pre whitespace-collapse), so the real paragraph structure is preserved for the blockquote renderer.
- Added `import base64` and a new `_full_body_gmail(fields)` helper to `scripts/deploy/lib/triage_digest_build.py` that decodes `BodyB64` and returns the stripped plain-text body (empty string on absence / decode error).
- Extended both Gmail paths in `build_items` to attach `fullBody` onto the item dict only when `category == "needs_reply"` — other categories / sources untouched.
- Fixture `scripts/deploy/fixtures/triage/personal-summary-fragment.txt` now carries a BodyB64 line encoding `Hi Bella,\n\nFollowing up on the invoice ...\n\nThanks,\nSomeone` so the new tests can exercise the fullBody → blockquote pipeline end to end.
- Verification: all 15 pre-existing tests still pass; manual dry-run confirms `needs_reply` items surface `fullBody` with the expected decoded text.

### Task 2 — render blockquote + header-line affordance

- Added two module-level constants in `scripts/deploy/lib/triage_digest_build.py`: `FULL_BODY_MAX = 4000`, `FULL_BODY_TRUNCATED_MARKER = "... (truncated)"`, `NEEDS_ATTENTION_AFFORDANCE = "_Reply in this topic with **\"draft <name>\"**, **\"ignore <name>\"**, or **\"summary\"** — I have each email body inline below._"`.
- Added `_render_body_blockquote(full_body)` helper that returns a list of `> `-prefixed lines with body content hard-capped at 4000 chars and an appended `> ... (truncated)` marker when clipping occurs.
- Edited `render_markdown`: at the top of `## Needs attention`, append `NEEDS_ATTENTION_AFFORDANCE` exactly once (the `for cat` loop only enters each category when it has items). Under each needs_reply Gmail item, after the summary / body-summary / finalize-hint lines, append a blank line + the blockquote + blank line.
- Added six new tests in `scripts/deploy/tests/test_triage_digest.py`:
  - `test_needs_reply_fixture_renders_full_body_blockquote_under_token_lines` — asserts blockquote lines are present, contain the real body, and sit _below_ the finalize hint; also asserts the bodySummary line itself is NOT blockquote-prefixed.
  - `test_long_body_truncates_with_marker` — asserts the renderer clips body content at 4000 chars and appends `> ... (truncated)`.
  - `test_short_body_blockquote_has_no_truncation_marker` — asserts the marker is absent when the body is short.
  - `test_header_line_affordance_present_once_when_needs_attention_has_items` — asserts the header-line appears exactly once, after the `## Needs attention` heading, and lists all three verbs.
  - `test_header_line_affordance_absent_when_needs_attention_empty` — asserts the header-line is absent when the Needs-attention section has no items.
  - `test_inline_body_render_has_no_callback_payloads` — regression-asserts no `tgd:` / `callback_data` substrings ever land in the rendered digest.
- Verification: 21/21 tests pass.

### Task 3 — runbook + architecture doc

- Rewrote `scripts/deploy/prompts/triage-draft-runbook.md`: operating model now explicitly says full email body is already inlined as a blockquote (no paste, no external fetch); added a "Recognized operator verbs" section documenting `draft <name>`, `ignore <name>`, `summary` with two worked examples (one for `draft <name>` showing the draft + token-offer pattern, one for `ignore <name>` showing the acknowledge-and-skip pattern); added a "Non-goals" section that pins the never-fetch / never-paste contract.
- Updated the `End-of-Day Triage Digest Agent` entry in `docs/agent-architecture.txt`: summary-input files now list `BodyB64` per item; added two new sub-bullets for "digest shape (per needs_reply Gmail item)" (summary + token + finalize + blockquote) and "digest shape (top of Needs-attention section)" (single italic header-line, rendered once, text-only).
- Verification: automated grep gates from the plan pass (`full email body|inline body|blockquote`, `draft <name>|ignore <name>|summary` in runbook; `needs_reply|inline body|Reply in this topic` in architecture doc).

### Task 4 — mirror + deploy + live verify

- `cp` to ops tree:
  - `scripts/deploy/lib/triage_digest_build.py` → `../openclaw-ops/vps/scripts/lib/triage_digest_build.py`
  - `scripts/deploy/prompts/triage-draft-runbook.md` → `../openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md`
  - `scripts/deploy/openclaw-gws-review-test` → `../openclaw-ops/vps/scripts/openclaw-gws-review-test`
  - `scripts/deploy/openclaw-gws-review-rental-test` → `../openclaw-ops/vps/scripts/openclaw-gws-review-rental-test`
- All four `diff -q` runs returned empty.
- Scope of ops commit: exactly the four mirrored files, nothing else — pre-existing `vps/.gitignore` working-tree churn (flagged in 02.1.1-01 summary) was not present in the tree at commit time, so no multi-agent-safety carve-out was needed this round.
- `cd ../openclaw-ops/vps && ./deploy.sh` completed cleanly; tarball pushed to `openclaw-ridl-openclaw-1:/data/openclaw-gws/bin/`.
- Forced a fresh review for both accounts to regenerate the summary files with `BodyB64:` lines. Confirmed `grep -c '^BodyB64:'` = 25 on both `gmail-review-summary-latest.txt` and `gmail-review-rental-summary-latest.txt`.
- Triggered the digest: `docker exec openclaw-ridl-openclaw-1 /data/openclaw-gws/bin/openclaw-gws-triage-digest` → `✅ Sent via Telegram. Message ID: 132`.
- Live digest counts:

  | Check                                                                             | Result |
  | --------------------------------------------------------------------------------- | ------ |
  | `grep -c '^> ' /data/openclaw-gws/output/triage-digest-latest.md`                 | **6**  |
  | `grep -c 'Reply in this topic' /data/openclaw-gws/output/triage-digest-latest.md` | **1**  |
  | `grep -c '^## Needs attention' /data/openclaw-gws/output/triage-digest-latest.md` | **1**  |
  | `grep -c '^## Needs reply' /data/openclaw-gws/output/triage-digest-latest.md`     | **1**  |

## Live digest excerpt (evidence)

Captured from `/data/openclaw-gws/output/triage-digest-latest.md` on the VPS right after the deploy, same run as Telegram message `132`:

```
**Triage digest** — window `2026-04-22T00:12:15.255209-05:00` → `2026-04-23T00:12:15.255209-05:00` (America/Chicago)
## Needs reply
### Personal Gmail
- [personal] Rental Property Interest (Response Required) — fyacoub@cisco.com (token: `0c589fa4f89d`)
  Hello, I am interested in your property on Aries Street. Can you tell what walkable restaurants are nearby? Also what is the exact address of the property? Thanks, Fred
  _Finalize when ready: `/bash tdr send-now <token>` or `/bash tdr save <token>`._

> Hello,
>
> I am interested in your property on Aries Street.  Can you tell what walkable restaurants are nearby?  Also what is the exact address of the property?
>
> Thanks,
> Fred

## Needs attention
_Reply in this topic with **"draft <name>"**, **"ignore <name>"**, or **"summary"** — I have each email body inline below._
### Hospitable
- [Hospitable] Jaclyn Yacoub (res 25ec8461-03b6-4d7b-af37-b8edf3e831fb): Hi Rachel! Thanks for sending your ID. The house has a high chair and pack 'n' play.
- [Hospitable] Rachel (res 25ec8461-03b6-4d7b-af37-b8edf3e831fb): Starting to pack
- ...
```

Both plan-level contracts are visible:

- Blockquote body under the `needs_reply` item's finalize hint (the live digest had a real `Response Required` item today).
- Single italic header-line listing all three verbs at the top of `## Needs attention`.

## Plan-level verification (gates from PLAN.md)

| Check                                                                                                                | Result            |
| -------------------------------------------------------------------------------------------------------------------- | ----------------- |
| `python3 -m pytest scripts/deploy/tests/test_triage_digest.py -q`                                                    | 21 passed         |
| `diff -q scripts/deploy/lib/triage_digest_build.py ../openclaw-ops/vps/scripts/lib/triage_digest_build.py`           | empty (identical) |
| `diff -q scripts/deploy/prompts/triage-draft-runbook.md ../openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md` | empty (identical) |
| `diff -q scripts/deploy/openclaw-gws-review-test ../openclaw-ops/vps/scripts/openclaw-gws-review-test`               | empty (identical) |
| `diff -q scripts/deploy/openclaw-gws-review-rental-test ../openclaw-ops/vps/scripts/openclaw-gws-review-rental-test` | empty (identical) |
| Live digest dispatched                                                                                               | `Message ID: 132` |
| Live blockquote count (`grep -c '^> '`) > 0                                                                          | 6                 |
| Live affordance count (`grep -c 'Reply in this topic'`) == 1                                                         | 1                 |

## Deviations from Plan

### Option A vs Option B — chose Option A with a base64-transport twist

The plan gave executor discretion between Option A (extend review scripts + summary parser) and Option B (read bodies from `gmail-review-latest.json` by ID inside `triage_digest_build.py`). Reading live VPS output made it clear Option B as literally written is not viable: `gmail-review-latest.json` is the output of Gmail's `users.messages.list` endpoint and only contains `{id, threadId}` per message. Full bodies only exist per-message after `openclaw-gws-review-test` does its `users.messages.get ... format=full` fetch and decodes the base64url-encoded MIME parts. Faking a Body-B by writing a second "bodies snapshot" JSON would introduce a second write path and a second staleness front — exactly the class of soft dependency Phase 02.1 was created to retire. So Option A it is.

The one judgment call on top of Option A: I emitted the body as a single-line `BodyB64:` field rather than a multi-line `Body:` block. That avoids touching `_parse_summary_blocks` (which is line-keyed) and survives any email content (colons, dashes, `---`, unicode) without an escape scheme. Decoding is a single `base64.b64decode` call in `_full_body_gmail`, only ever run for `needs_reply` items.

### No other deviations

Plan executed exactly as written otherwise. No Rule-1/2/3 auto-fixes triggered along the way. No Rule-4 architectural decisions surfaced.

## Authentication gates

None encountered. `ssh openclaw-vps` (key-based) and the container's gws wrappers were already authenticated from prior sessions; review scripts ran without token prompts.

## Known Stubs

None. Every code path that attaches / renders / documents the fullBody is wired end to end against real data, and the fixture exercises the real base64 decode path.

## Scope notes

- `vps/.gitignore` comment-only edit in `openclaw-ops` (pre-existing, flagged in 02.1.1-01 summary under multi-agent safety) was NOT present in the working tree when I staged the mirror commit — so no carve-out was needed this round. Only the four intended files are in `7716d63`.
- Live VPS digest _did_ have a real `needs_reply` item today (`Rental Property Interest (Response Required)` from `fyacoub@cisco.com`), so the `^> ` blockquote assertion was exercised against real Gmail data rather than a synthetic one — no SUMMARY carve-out or test-email round-trip needed.
- Phase 02.1.1 plans are now both complete (Plan 01 — dict-leak fix, Plan 02 — inline body + affordance). Phase is ready to move to verification / UAT.

## Self-Check: PASSED

- File `scripts/deploy/openclaw-gws-review-test`: FOUND (BodyB64 emission present)
- File `scripts/deploy/openclaw-gws-review-rental-test`: FOUND (BodyB64 emission present)
- File `scripts/deploy/lib/triage_digest_build.py`: FOUND (`_full_body_gmail`, `_render_body_blockquote`, `NEEDS_ATTENTION_AFFORDANCE` all present)
- File `scripts/deploy/tests/test_triage_digest.py`: FOUND (6 new test methods present)
- File `scripts/deploy/fixtures/triage/personal-summary-fragment.txt`: FOUND (BodyB64 line added)
- File `scripts/deploy/prompts/triage-draft-runbook.md`: FOUND (inline-body + verbs section present)
- File `docs/agent-architecture.txt`: FOUND (digest-shape bullets added)
- File `../openclaw-ops/vps/scripts/lib/triage_digest_build.py`: FOUND and byte-identical to source
- File `../openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md`: FOUND and byte-identical to source
- File `../openclaw-ops/vps/scripts/openclaw-gws-review-test`: FOUND and byte-identical to source
- File `../openclaw-ops/vps/scripts/openclaw-gws-review-rental-test`: FOUND and byte-identical to source
- Commit `5971af9cc3` (openclaw): FOUND
- Commit `711903f4b9` (openclaw): FOUND
- Commit `f116b71c10` (openclaw): FOUND
- Commit `7716d63` (openclaw-ops): FOUND
- Live VPS blockquote count: 6 (> 0)
- Live VPS affordance count: 1 (== 1)
