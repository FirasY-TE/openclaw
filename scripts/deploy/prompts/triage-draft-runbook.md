# Triage Draft Runbook

Use this runbook when helping with triage items in the `triage_digest` topic.

## Operating model

- Work from the digest context and thread history first.
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
