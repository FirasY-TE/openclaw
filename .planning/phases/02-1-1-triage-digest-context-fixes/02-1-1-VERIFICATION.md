---
phase: 02-1-1-triage-digest-context-fixes
verified: 2026-04-23T00:00:00Z
status: human_needed
score: 4/4 code-backed must-haves verified
requirements:
  - TRIAGE-02.1.1-1
  - TRIAGE-02.1.1-2
  - TRIAGE-02.1.1-3
  - TRIAGE-02.1.1-4
human_verification:
  - test: "Operator asks Bella to draft in-thread for the current needs_reply item (e.g. 'draft Fred')"
    expected: "Bella produces a usable reply in her voice using only inline blockquote body — no paste request, no tool call, no 'I don't see the email' response — and offers `/bash tdr send-now <token>` for finalization"
    why_human: "Requires live LLM turn + real operator interaction inside the Telegram triage topic; can't verify programmatically from static source"
  - test: "Operator asks Bella to ignore a needs_attention item (e.g. 'ignore Rachel')"
    expected: "Bella acknowledges and skips without minting a draft, without calling `tdr`, and without changing VPS state"
    why_human: "Runtime agent behavior against live verb; requires a real Telegram turn"
  - test: "Operator uses `summary` verb in triage topic"
    expected: "Bella summarizes the current digest's Needs-attention / Needs-reply items (who + why + suggested next action per item)"
    why_human: "Runtime agent behavior; requires a real Telegram turn"
  - test: "Operator invokes `/bash tdr send-now <token>` after an approved draft"
    expected: "A real email is delivered end-to-end via Gmail; token is consumed"
    why_human: "ROADMAP 02.1.1 UAT item explicitly requires a live send through Gmail; carryover gate from Phase 02.1, not code-verifiable"
---

# Phase 02.1.1: Triage Digest Context & Rendering Fixes — Verification Report

**Phase Goal:** Close the two live-UAT gaps from Phase 02.1 that prevent Plan C from actually working — (1) Hospitable dict-repr leak in digest, (2) agent has no email body context when asked to draft in-thread — plus a single operator-verb header-line affordance and a process-level ops-mirror guarantee.

**Verified:** 2026-04-23
**Status:** human_needed (all automated checks pass; 4 items require live operator UAT on Telegram)
**Re-verification:** No — initial verification.

## Goal Achievement

### Observable Truths

| #   | Truth                                                                                                                                                                            | Status     | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Hospitable digest lines never leak raw Python dict repr; render a real guest name + readable preview                                                                             | ✓ VERIFIED | `scripts/deploy/lib/triage_digest_build.py:200-249` — `_hospitable_guest_name`/`_hospitable_preview`/`_coerce_str` replace the old `str(dict)` path; 3 regression tests (`test_hospitable_dict_sender_*`, `test_hospitable_slice_digest_has_no_dict_repr_leak`) all pass; live VPS post-deploy `grep -c "{'" /data/openclaw-gws/output/triage-digest-latest.md` = 0 (02-1-1-01-SUMMARY.md)                                                                                                           |
| 2   | Needs-reply Gmail items include full email body inline as `> `-prefixed Markdown blockquote beneath summary + token + finalize hint, capped at 4000 chars with truncation marker | ✓ VERIFIED | `scripts/deploy/lib/triage_digest_build.py:458-466` (renderer appends blockquote after finalize hint) + `scripts/deploy/lib/triage_digest_build.py:474-491` (`_render_body_blockquote` cap + marker); `_full_body_gmail` decodes `BodyB64` at lines 169-185; 3 tests (`test_needs_reply_fixture_renders_full_body_blockquote_under_token_lines`, `test_long_body_truncates_with_marker`, `test_short_body_blockquote_has_no_truncation_marker`); live VPS `grep -c '^> '` = 6 (02-1-1-02-SUMMARY.md) |
| 3   | Digest includes single italic header-line affordance at top of `## Needs attention`, once, only when items exist, never as a callback/button                                     | ✓ VERIFIED | `scripts/deploy/lib/triage_digest_build.py:34-37` (constant) + `:421-422` (emitted once inside the category loop, which only enters populated buckets); 2 tests (`test_header_line_affordance_present_once_when_needs_attention_has_items`, `test_header_line_affordance_absent_when_needs_attention_empty`); regression test `test_inline_body_render_has_no_callback_payloads` confirms no `tgd:` / `callback_data`; live VPS `grep -c 'Reply in this topic'` = 1                                  |
| 4   | Source-tree changes and ops-tree mirror stay in sync; changes deployed + verified on VPS before plan completes                                                                   | ✓ VERIFIED | `diff -q` returns empty for all 4 mirrored files (triage_digest_build.py, triage-draft-runbook.md, openclaw-gws-review-test, openclaw-gws-review-rental-test); both plan SUMMARYs record deploy.sh → `docker exec ... openclaw-gws-triage-digest` with captured Telegram message IDs (131 for plan 01, 132 for plan 02) and post-deploy grep counts                                                                                                                                                  |

**Score:** 4/4 code-backed must-haves verified.

### Required Artifacts

| Artifact                                                      | Expected                                                                                                                       | Status     | Details                                                                                                                                           |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/deploy/lib/triage_digest_build.py`                   | Dict-aware Hospitable extractors; `_full_body_gmail`; `_render_body_blockquote`; `NEEDS_ATTENTION_AFFORDANCE`; renderer wiring | ✓ VERIFIED | All five units present at cited line ranges; 21/21 unit tests pass                                                                                |
| `scripts/deploy/tests/test_triage_digest.py`                  | Regression tests for dict-leak, inline body, truncation, header-line presence/absence, no-callback                             | ✓ VERIFIED | 21 tests, including the 9 net-new phase 02.1.1 tests                                                                                              |
| `scripts/deploy/prompts/triage-draft-runbook.md`              | Agent instructed to use inline body, no paste, no tool calls; documents 3 verbs with 2 examples                                | ✓ VERIFIED | Sections "Operating model", "Recognized operator verbs" (with `draft <name>`, `ignore <name>`, `summary` + examples), and "Non-goals" all present |
| `docs/agent-architecture.txt`                                 | Triage section reflects `BodyB64` summary input + digest shape (inline blockquote + header-line)                               | ✓ VERIFIED | Lines 102-114 describe `BodyB64` per item + needs_reply blockquote shape + single italic header-line                                              |
| `../openclaw-ops/vps/scripts/lib/triage_digest_build.py`      | Byte-identical mirror                                                                                                          | ✓ VERIFIED | `diff -q` empty                                                                                                                                   |
| `../openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md` | Byte-identical mirror                                                                                                          | ✓ VERIFIED | `diff -q` empty                                                                                                                                   |
| `../openclaw-ops/vps/scripts/openclaw-gws-review-test`        | Byte-identical mirror (emits `BodyB64:`)                                                                                       | ✓ VERIFIED | `diff -q` empty                                                                                                                                   |
| `../openclaw-ops/vps/scripts/openclaw-gws-review-rental-test` | Byte-identical mirror (emits `BodyB64:`)                                                                                       | ✓ VERIFIED | `diff -q` empty                                                                                                                                   |

### Key Link Verification

| From                                                        | To                                                            | Via                                       | Status | Details                                                                                                                                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------------- | ----------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/deploy/lib/triage_digest_build.py`                 | `../openclaw-ops/vps/scripts/lib/triage_digest_build.py`      | manual mirror + `vps/deploy.sh`           | WIRED  | `diff -q` empty; SUMMARYs record successful `./deploy.sh` tarball push to `openclaw-ridl-openclaw-1:/data/openclaw-gws/bin/`                                                                    |
| `scripts/deploy/prompts/triage-draft-runbook.md`            | `../openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md` | manual mirror + `vps/deploy.sh`           | WIRED  | `diff -q` empty                                                                                                                                                                                 |
| `scripts/deploy/openclaw-gws-review-test` (BodyB64 emitter) | `_full_body_gmail` in `triage_digest_build.py`                | summary-file `BodyB64:` key               | WIRED  | Review script emits `BodyB64:`; `_parse_summary_blocks` captures it; `_full_body_gmail` base64-decodes it; `build_items` attaches `fullBody` on needs_reply items only (lines 322-327, 347-352) |
| Renderer                                                    | needs_reply blockquote                                        | `_render_body_blockquote(it["fullBody"])` | WIRED  | Lines 458-466 guard on `cat == "needs_reply"`, `src in personal_gmail/rental_gmail`, and non-empty string body                                                                                  |
| Renderer                                                    | header-line affordance                                        | `NEEDS_ATTENTION_AFFORDANCE` constant     | WIRED  | Line 421-422 inside category loop; only runs for populated `needs_attention` bucket                                                                                                             |

### Data-Flow Trace (Level 4)

| Artifact                                           | Data Variable                        | Source                                                                                                             | Produces Real Data                                                                                            | Status    |
| -------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- | --------- |
| `triage_digest_build.py::render_markdown`          | `it["fullBody"]` (needs_reply items) | `_full_body_gmail` decoding `BodyB64` from `gmail-review-summary-latest.txt` written by `openclaw-gws-review-test` | ✓ — live VPS run produced `^> ` blockquote count of 6 against real `Response Required` email (Message ID 132) | ✓ FLOWING |
| `triage_digest_build.py::_summary_line_hospitable` | `guest`, `prev`, `rid`               | Hospitable API payload written to `hospitable-events-latest.json`, extracted via dict-aware helpers                | ✓ — live VPS run rendered 5 Hospitable lines with real guest names and reservation UUIDs, no dict repr        | ✓ FLOWING |
| `triage_digest_build.py::render_markdown`          | `NEEDS_ATTENTION_AFFORDANCE`         | Module constant, gated by populated bucket                                                                         | ✓ — live VPS digest has exactly 1 occurrence of `Reply in this topic`                                         | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior                                                          | Command                                                                                                                    | Result                                                                    | Status |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------ |
| All digest tests pass                                             | `python3 -m pytest scripts/deploy/tests/test_triage_digest.py -q`                                                          | `21 passed in 0.17s`                                                      | ✓ PASS |
| Ops-tree and source-tree `triage_digest_build.py` byte-identical  | `diff -q scripts/deploy/lib/triage_digest_build.py ../openclaw-ops/vps/scripts/lib/triage_digest_build.py`                 | empty                                                                     | ✓ PASS |
| Ops-tree and source-tree runbook byte-identical                   | `diff -q scripts/deploy/prompts/triage-draft-runbook.md ../openclaw-ops/vps/scripts/prompts/triage-draft-runbook.md`       | empty                                                                     | ✓ PASS |
| Ops-tree and source-tree review scripts byte-identical            | `diff -q scripts/deploy/openclaw-gws-review{,-rental}-test ../openclaw-ops/vps/scripts/openclaw-gws-review{,-rental}-test` | empty × 2                                                                 | ✓ PASS |
| No `tgd:` callback payloads reintroduced in production            | `rg -n "tgd:" scripts/deploy` (ignoring negative-assertion test)                                                           | only `scripts/deploy/tests/test_triage_digest.py:342` (regression-assert) | ✓ PASS |
| `maybeRouteTriageDraftFeedback` still absent from `src/telegram/` | `rg -n "maybeRouteTriageDraftFeedback" src/telegram`                                                                       | no matches                                                                | ✓ PASS |

### Requirements Coverage

| Requirement     | Source Plan                           | Description                                                                                                                                     | Status      | Evidence                                                                                                                                            |
| --------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| TRIAGE-02.1.1-1 | 02-1-1-01-PLAN.md                     | Hospitable digest lines render readable guest name + preview, never raw dict repr                                                               | ✓ SATISFIED | Truth #1 above; live VPS `grep -c "{'"` = 0; commits `7e204d280e` + `425c666bf4`                                                                    |
| TRIAGE-02.1.1-2 | 02-1-1-02-PLAN.md                     | Needs-reply items include full email body inline as Markdown blockquote                                                                         | ✓ SATISFIED | Truth #2 above; live VPS blockquote count = 6 against real needs_reply email; commits `5971af9cc3` + `711903f4b9` + `f116b71c10`                    |
| TRIAGE-02.1.1-3 | 02-1-1-01-PLAN.md + 02-1-1-02-PLAN.md | Source tree and ops tree kept in sync; deployed + verified live before plan closes                                                              | ✓ SATISFIED | Truth #4 above; `diff -q` empty on all 4 mirrored files; commits `a1b97c6` + `7716d63` in openclaw-ops                                              |
| TRIAGE-02.1.1-4 | 02-1-1-02-PLAN.md                     | Single italic header-line affordance listing `draft <name>`, `ignore <name>`, `summary`, text-only, emitted only when Needs-attention has items | ✓ SATISFIED | Truth #3 above; live VPS `grep -c 'Reply in this topic'` = 1; runbook documents the verbs; 2 dedicated tests cover present-once + absent-when-empty |

All 4 phase requirements are claimed by plans and verified in code + live VPS. No orphaned requirements.

### Anti-Patterns Found

| File              | Line | Pattern | Severity | Impact                                                                                                                                       |
| ----------------- | ---- | ------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| _(none detected)_ | —    | —       | —        | No TODO/FIXME/PLACEHOLDER in modified files; no empty returns; no hardcoded `[]` on user-facing code paths; all helpers are wired and tested |

### Human Verification Required

The following items from the ROADMAP 02.1.1 UAT checklist cannot be verified in code or static VPS output alone — they require a live operator turn in the Telegram triage topic or a real Gmail send round-trip:

#### 1. Operator drafts in-thread via `draft <name>` verb

**Test:** In the triage Telegram topic, pick a currently-live needs_reply item (e.g. a Rental Property Interest email) and send `draft Fred` (or natural-language equivalent).
**Expected:** Bella produces a usable reply draft in her voice using only the inline blockquote body — no paste request, no "I don't see the email", no external tool call — and offers `/bash tdr send-now <token>` or `/bash tdr save <token>` for finalization.
**Why human:** Requires live LLM turn against the digest context; agent behavior cannot be asserted from static source.

#### 2. Operator skips an item via `ignore <name>` verb

**Test:** In the triage topic, send `ignore Rachel` (for any current needs_attention Hospitable item).
**Expected:** Bella acknowledges the skip without minting a draft, without calling `tdr`, and without changing VPS state.
**Why human:** Runtime agent behavior; requires a real Telegram turn.

#### 3. Operator invokes `summary` verb

**Test:** In the triage topic, send `summary`.
**Expected:** Bella summarizes the current digest's Needs-attention / Needs-reply items briefly (who + why + suggested next action per item).
**Why human:** Runtime agent behavior; requires a real Telegram turn.

#### 4. `/bash tdr send-now <token>` end-to-end send

**Test:** Approve a draft produced in UAT #1, then run `/bash tdr send-now <token>` in the triage topic.
**Expected:** A real email is delivered through Gmail and the token is consumed / no longer usable.
**Why human:** ROADMAP 02.1.1 explicitly lists an end-to-end send gate; requires a live Gmail round-trip that must not be exercised from automated tests.

### Gaps Summary

No code-level gaps. All four phase requirements are satisfied in source code, covered by 21 passing tests, mirrored byte-identically into `openclaw-ops`, deployed via `vps/deploy.sh`, and verified on the live VPS via `grep` counts on the real digest (blockquote = 6, affordance = 1, dict-leak = 0). The remaining UAT gates — conversational operator turns on Telegram plus an end-to-end Gmail send — are runtime concerns that cannot be validated in code and have been lifted into `human_verification`.

## Commit Hygiene

Plan commits are scoped to 02.1.1 and follow the source-tree → ops-tree ordering:

| Repo         | Hash         | Scope                                       |
| ------------ | ------------ | ------------------------------------------- |
| openclaw     | `7e204d280e` | test(02.1.1-01): fixture + regression tests |
| openclaw     | `425c666bf4` | fix(02.1.1-01): Hospitable dict-leak fix    |
| openclaw-ops | `a1b97c6`    | gap-closure(02.1.1-01): mirror              |
| openclaw     | `5971af9cc3` | feat(02.1.1-02): surface fullBody           |
| openclaw     | `711903f4b9` | feat(02.1.1-02): blockquote + affordance    |
| openclaw     | `f116b71c10` | docs(02.1.1-02): runbook + architecture     |
| openclaw-ops | `7716d63`    | gap-closure(02.1.1-02): mirror (4 files)    |

Both SUMMARYs confirm the pre-existing `openclaw-ops/vps/.gitignore` working-tree edit was NOT bundled into the 02.1.1 mirror commits, consistent with multi-agent safety. No unrelated refactors detected in the phase commit set.

---

_Verified: 2026-04-23_
_Verifier: Claude (gsd-verifier)_
