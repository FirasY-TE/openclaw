---
status: partial
phase: 02-1-1-triage-digest-context-fixes
source: [02-1-1-VERIFICATION.md]
started: 2026-04-23T05:15:00Z
updated: 2026-04-23T05:15:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Operator asks Bella to draft in-thread using the inline blockquote body

expected: Bella produces a usable reply in her voice using only the inline blockquote body — no paste request, no tool call, no "I don't see the email" response — and offers `/bash tdr send-now <token>` for finalization.
result: [pending]

### 2. Operator asks Bella to ignore a needs_attention item

expected: Bella acknowledges and skips without minting a draft, without calling `tdr`, and without changing VPS state.
result: [pending]

### 3. Operator uses the `summary` verb in the triage topic

expected: Bella summarizes the current digest's Needs-attention / Needs-reply items (who + why + suggested next action per item).
result: [pending]

### 4. Operator invokes `/bash tdr send-now <token>` after an approved draft

expected: A real email is delivered end-to-end via Gmail; token is consumed from state.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
