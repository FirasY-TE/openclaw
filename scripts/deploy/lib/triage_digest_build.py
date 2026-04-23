#!/usr/bin/env python3
"""
Build end-of-day triage digest JSON + Markdown from prepared VPS pipeline outputs.

Window: rolling 24-hour lookback from run time (America/Chicago).
See docs/agent-architecture.txt for input paths.

Optional: TRIAGE_LLM_REFINE=1 reserved for future LLM refinement (no-op when unset).
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Chicago")
CAP_PER_CATEGORY = 15
LOOKBACK_HOURS = 24


def _now_chicago() -> datetime:
    return datetime.now(TZ)


def _window_bounds(now: datetime) -> tuple[datetime, datetime]:
    start = now - timedelta(hours=LOOKBACK_HOURS)
    return start, now


def _parse_email_date(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(TZ)
    except (TypeError, ValueError, OverflowError):
        return None


def _parse_summary_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    for chunk in text.split("---"):
        chunk = chunk.strip()
        if not chunk:
            continue
        fields: dict[str, str] = {}
        for line in chunk.splitlines():
            line = line.strip()
            if ": " in line:
                k, v = line.split(": ", 1)
                fields[k.strip()] = v.strip()
        if fields.get("ID"):
            blocks.append(fields)
    return blocks


def _categorize_gmail(fields: dict[str, str]) -> str | None:
    """Return primary triage category or None to omit. Precedence: urgent > needs_reply > needs_attention."""
    priority = fields.get("Priority", "").strip().lower()
    alert = fields.get("AlertNeeded", "").strip().lower()
    draft = fields.get("DraftNeeded", "").strip().lower()
    createtask = fields.get("CreateTask", "").strip().lower()
    labels = fields.get("Labels", "").strip().lower()

    urgent = (
        priority == "urgent"
        or alert == "yes"
        or "rental/urgent" in labels.replace(" ", "")
        or "/urgent" in labels
    )
    needs_reply = draft in ("yes", "maybe")
    needs_attention = createtask == "yes" or priority in ("medium", "high")

    if urgent:
        return "urgent"
    if needs_reply:
        return "needs_reply"
    if needs_attention:
        return "needs_attention"
    return None


def _hospitable_messages(root: dict[str, Any]) -> list[dict[str, Any]]:
    msgs = root.get("messages")
    if isinstance(msgs, dict) and isinstance(msgs.get("data"), list):
        return msgs["data"]
    if isinstance(msgs, list):
        return msgs
    return []


def _msg_ts(msg: dict[str, Any]) -> datetime | None:
    for key in (
        "created_at",
        "createdAt",
        "sent_at",
        "sentAt",
        "updated_at",
        "updatedAt",
        "timestamp",
    ):
        val = msg.get(key)
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val, tz=timezone.utc).astimezone(TZ)
        if isinstance(val, str):
            try:
                dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(TZ)
            except ValueError:
                continue
    return None


def _categorize_hospitable(msg: dict[str, Any]) -> str:
    text = json.dumps(msg, default=str).lower()
    if any(x in text for x in ("emergency", "urgent", "asap", "flooded", "broken pipe")):
        return "urgent"
    direction = str(msg.get("direction") or msg.get("from_type") or "").lower()
    unread = msg.get("read") is False or msg.get("isRead") is False or msg.get("unread") is True
    if "guest" in direction or unread:
        return "needs_reply"
    return "needs_attention"


def _summary_line_gmail(fields: dict[str, str], account: str) -> str:
    subj = fields.get("Subject", "(no subject)")[:120]
    sender = fields.get("SenderEmail") or fields.get("From", "")[:80]
    return f"[{account}] {subj} — {sender}".strip()


# Body excerpts shown under each Gmail bullet are capped to keep the Telegram
# card readable when several items land in the same digest.
BODY_SUMMARY_MAX = 280


def _body_summary_gmail(fields: dict[str, str]) -> str:
    raw = (fields.get("BodySummary") or "").strip()
    if not raw:
        return ""
    if len(raw) <= BODY_SUMMARY_MAX:
        return raw
    return raw[:BODY_SUMMARY_MAX].rstrip() + "…"


def _summary_line_hospitable(msg: dict[str, Any]) -> str:
    prev = str(msg.get("preview") or msg.get("body") or msg.get("text") or "")[:100]
    guest = str(msg.get("guestName") or msg.get("guest_name") or msg.get("sender") or "guest")
    rid = str(msg.get("reservationId") or msg.get("reservation_id") or "")
    base = f"[Hospitable] {guest}"
    if rid:
        base += f" (res {rid})"
    if prev:
        base += f": {prev}"
    return base[:200]


def _refs_gmail(fields: dict[str, str], account: str) -> dict[str, str]:
    refs: dict[str, str] = {
        "gmailMessageId": fields.get("ID", ""),
        "account": "rental" if account == "rental" else "personal",
    }
    if fields.get("Thread-ID"):
        refs["threadId"] = fields["Thread-ID"]
    if fields.get("Subject"):
        refs["subject"] = fields["Subject"][:200]
    if fields.get("SenderEmail") or fields.get("From"):
        refs["sender"] = (fields.get("SenderEmail") or fields.get("From", ""))[:120]
    if fields.get("Date"):
        refs["date"] = fields["Date"]
    body_excerpt = _body_summary_gmail(fields)
    if body_excerpt:
        refs["bodySummary"] = body_excerpt
    return refs


def _refs_hospitable(msg: dict[str, Any]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for k in ("id", "messageId", "message_id"):
        if msg.get(k):
            refs["hospitableMessageId"] = str(msg[k])
            break
    if msg.get("reservationId"):
        refs["reservationId"] = str(msg["reservationId"])
    elif msg.get("reservation_id"):
        refs["reservationId"] = str(msg["reservation_id"])
    return refs


def _maybe_llm_refine(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if os.environ.get("TRIAGE_LLM_REFINE", "").strip() not in ("1", "true", "yes"):
        return items
    # Hook for optional LLM refinement (D-03); disabled by default for CI/VPS determinism.
    return items


def build_items(
    base_dir: Path,
    now: datetime | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    now = now or _now_chicago()
    start, end = _window_bounds(now)
    window = {
        "tz": "America/Chicago",
        "start": start.isoformat(),
        "end": end.isoformat(),
    }

    items: list[dict[str, Any]] = []

    personal_path = base_dir / "output" / "gmail-review-summary-latest.txt"
    if personal_path.is_file():
        blocks = _parse_summary_blocks(personal_path.read_text(encoding="utf-8", errors="replace"))
        for fields in blocks:
            dt = _parse_email_date(fields.get("Date", ""))
            if dt is None or not (start <= dt <= end):
                continue
            cat = _categorize_gmail(fields)
            if not cat:
                continue
            refs = _refs_gmail(fields, "personal")
            item: dict[str, Any] = {
                "source": "personal_gmail",
                "category": cat,
                "summaryLine": _summary_line_gmail(fields, "personal"),
                "refs": refs,
            }
            if refs.get("bodySummary"):
                item["bodySummary"] = refs["bodySummary"]
            items.append(item)

    rental_path = base_dir / "output" / "gmail-review-rental-summary-latest.txt"
    if rental_path.is_file():
        blocks = _parse_summary_blocks(rental_path.read_text(encoding="utf-8", errors="replace"))
        for fields in blocks:
            dt = _parse_email_date(fields.get("Date", ""))
            if dt is None or not (start <= dt <= end):
                continue
            cat = _categorize_gmail(fields)
            if not cat:
                continue
            refs = _refs_gmail(fields, "rental")
            item = {
                "source": "rental_gmail",
                "category": cat,
                "summaryLine": _summary_line_gmail(fields, "rental"),
                "refs": refs,
            }
            if refs.get("bodySummary"):
                item["bodySummary"] = refs["bodySummary"]
            items.append(item)

    hosp_path = base_dir / "output" / "hospitable-events-latest.json"
    if hosp_path.is_file():
        try:
            root = json.loads(hosp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            root = {}
        for msg in _hospitable_messages(root):
            if not isinstance(msg, dict):
                continue
            dt = _msg_ts(msg)
            if dt is None or not (start <= dt <= end):
                continue
            cat = _categorize_hospitable(msg)
            items.append(
                {
                    "source": "hospitable",
                    "category": cat,
                    "summaryLine": _summary_line_hospitable(msg),
                    "refs": _refs_hospitable(msg),
                }
            )

    items = _maybe_llm_refine(items)

    meta = {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "window": window,
        "items": items,
    }
    return meta, items


def render_markdown(meta: dict[str, Any], items: list[dict[str, Any]]) -> str:
    if not items:
        return (
            f"Triage digest — all clear for past {LOOKBACK_HOURS}h "
            f"(through {meta['window']['end'][:16]} CT). Nothing actionable."
        )

    order_cat = ("urgent", "needs_reply", "needs_attention")
    titles = {
        "urgent": "Urgent",
        "needs_reply": "Needs reply",
        "needs_attention": "Needs attention",
    }
    suborder = ("personal_gmail", "rental_gmail", "hospitable")
    sublabels = {
        "personal_gmail": "Personal Gmail",
        "rental_gmail": "Rental Gmail",
        "hospitable": "Hospitable",
    }

    by_cat: dict[str, list[dict[str, Any]]] = {c: [] for c in order_cat}
    for it in items:
        by_cat.setdefault(it["category"], []).append(it)

    out: list[str] = [
        f"**Triage digest** — window `{meta['window']['start']}` → `{meta['window']['end']}` (America/Chicago)"
    ]
    for cat in order_cat:
        bucket = by_cat.get(cat, [])
        if not bucket:
            continue
        out.append(f"## {titles[cat]}")
        total = len(bucket)
        shown = bucket[:CAP_PER_CATEGORY]
        hidden = total - len(shown)
        # Group shown items under subheadings
        by_src: dict[str, list[dict[str, Any]]] = {s: [] for s in suborder}
        for it in shown:
            by_src.setdefault(it["source"], []).append(it)
        for src in suborder:
            sub = by_src.get(src, [])
            if not sub:
                continue
            out.append(f"### {sublabels[src]}")
            for it in sub:
                out.append(f"- {it['summaryLine']}")
                body = it.get("bodySummary")
                if body:
                    # Indented continuation so the bullet stays readable and the
                    # operator has enough context to decide without opening Gmail.
                    out.append(f"  {body}")
        if hidden > 0:
            out.append(
                f"+{hidden} more items omitted (cap {CAP_PER_CATEGORY}); run on-demand `/triage` or `openclaw triage` for full detail."
            )
    return "\n".join(out)


def _draft_state_path(base_dir: Path) -> Path:
    return base_dir / "state" / "triage-draft-tokens.json"


def build_draft_state(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Build token state for Gmail needs_reply items used by `tdr` finalization."""
    by_token: dict[str, Any] = {}
    for it in items:
        if it.get("category") != "needs_reply":
            continue
        if it.get("source") not in ("personal_gmail", "rental_gmail"):
            continue
        refs = it.get("refs") if isinstance(it.get("refs"), dict) else {}
        mid = refs.get("gmailMessageId")
        if not mid:
            continue
        token = secrets.token_hex(6)
        account = refs.get("account") if refs.get("account") in ("personal", "rental") else "personal"
        by_token[token] = {
            "account": account,
            "gmailMessageId": mid,
            "threadId": refs.get("threadId"),
            "subject": refs.get("subject", ""),
            "sender": refs.get("sender", ""),
            "date": refs.get("date", ""),
            "summaryLine": it.get("summaryLine", ""),
            "draftTextVersion": 0,
            "draftId": None,
        }
    return by_token


def _write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def run_build(
    base_dir: Path,
    now: datetime | None = None,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    meta, items = build_items(base_dir, now=now)
    by_token = build_draft_state(items)
    meta["draftTokens"] = list(by_token.keys())
    md = render_markdown(meta, items)
    return meta, md, by_token


def _parse_now_iso(raw: str) -> datetime:
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build triage digest artifacts.")
    parser.add_argument(
        "--base-dir",
        default=os.environ.get("OPENCLAW_GWS_DIR", "/data/openclaw-gws"),
        help="Root openclaw-gws data directory",
    )
    parser.add_argument(
        "--stdout-md-only",
        action="store_true",
        help="Print Markdown to stdout only (no file writes); for tests",
    )
    parser.add_argument(
        "--now-iso",
        default=None,
        help="Override 'now' for tests (ISO datetime, America/Chicago or offset)",
    )
    args = parser.parse_args()
    base = Path(args.base_dir)
    fixed_now = _parse_now_iso(args.now_iso) if args.now_iso else None
    meta, md, by_token = run_build(base, now=fixed_now)

    if args.stdout_md_only:
        sys.stdout.write(md)
        if not md.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    out_dir = base / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "triage-digest-latest.json"
    md_path = out_dir / "triage-digest-latest.md"
    json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")

    state_payload = {
        "version": 1,
        "generatedAt": meta.get("generatedAt"),
        "byToken": by_token,
    }
    _write_json_atomic(_draft_state_path(base), state_payload)
    sys.stdout.write(md)
    if not md.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
