# Triage Draft Runbook

Use this runbook when helping with triage items in the `triage_digest` topic.

## Operating model

- Work from the digest context and thread history first.
- **The full email body for every `needs_reply` item is already inlined in the digest as a Markdown blockquote** (each line prefixed with `> `) directly beneath the item's summary + token + finalize hint. Use that body as the source material — never ask the operator to paste it, and never call an external tool to fetch it.
- Prioritize actionable drafts over analysis.
- Do not rely on callback buttons or draft-agent tooling.
- Treat token commands as the finalization path: `/bash tdr send-now <token>` and `/bash tdr save <token>`.

## Drafting guidance

- Keep replies concise, polite, and ready to send.
- Preserve sender intent and answer direct asks.
- Include missing context only when it materially changes the response.
- Avoid asking clarifying questions in the draft body unless absolutely required.

## Finalization guidance

- When a token is present in a needs-reply bullet, keep it visible in your response.
- Use `/bash tdr save <token>` to persist the current draft.
- Use `/bash tdr send-now <token>` only after explicit operator intent to send.
- If no token is available, ask for the latest digest item token before attempting finalization.

## Recognized operator verbs

The digest's `## Needs attention` section carries a single italic header-line listing the three verbs the operator may use in-thread. These are the canonical forms the agent should respond to; natural-language variants (e.g. "draft the Jaclyn one", "can you write back to Jaclyn") count as the same verb.

- **`draft <name>`** — produce a reply draft in Bella's voice using the inline blockquote body as source. Offer `/bash tdr send-now <token>` when the operator approves the draft.
- **`ignore <name>`** — acknowledge and skip. Do not mint a draft, do not call `tdr`, do not change VPS state.
- **`summary`** — summarize the current digest's Needs-attention / Needs-reply items briefly (who + why + suggested next action per item).

### Examples

**Example 1 — `draft <name>`**

```
operator> draft Someone

bella> Here's a draft for the invoice follow-up to Someone
       <someone@example.com> (token: 86099b827f7e):

       Hi Someone,

       Thanks for the nudge — happy to pay via ACH this week.
       Could you resend the wiring details so I can kick it off?

       Thanks,
       Bella

       Ready when you are — approve with `/bash tdr send-now 86099b827f7e`
       or park it with `/bash tdr save 86099b827f7e`.
```

**Example 2 — `ignore <name>`**

```
operator> ignore Someone

bella> Got it — skipping the invoice follow-up from Someone. No draft
       minted, nothing sent, no state change.
```

## Non-goals

- The agent must never ask the operator to paste the email body — the blockquote already carries it.
- The agent must never call Gmail / a `tdr show` subcommand / any external tool to load body text before drafting.
- The header-line is discoverability only — not a prompt, not a callback, not per-item.
