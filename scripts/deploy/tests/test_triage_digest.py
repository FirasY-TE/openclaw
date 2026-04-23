"""Tests for triage digest builder (Phase 2 / plan 02-01).

Run: python3 -m unittest discover -s scripts/deploy/tests -p 'test_triage_digest.py' -v
(or: python3 -m pytest scripts/deploy/tests/test_triage_digest.py -q if pytest is installed)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import triage_digest_build as tdb  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "triage"


class TestTriageDigest(unittest.TestCase):
    def test_personal_review_script_escalates_response_required_subjects(self) -> None:
        script = Path(__file__).resolve().parents[1] / "openclaw-gws-review-test"
        text = script.read_text(encoding="utf-8").lower()
        for phrase in ("response required", "please reply", "let me know", "please advise"):
            self.assertIn(phrase, text)
        self.assertIn("if not is_promo and any(sig in subj for sig in response_required_signals):", text)
        self.assertIn('draft = "maybe"', text)

    def test_rental_review_script_escalates_response_required_subjects(self) -> None:
        script = Path(__file__).resolve().parents[1] / "openclaw-gws-review-rental-test"
        text = script.read_text(encoding="utf-8").lower()
        for phrase in ("response required", "please reply", "let me know", "please advise"):
            self.assertIn(phrase, text)
        self.assertIn("if not is_promo and any(sig in subj for sig in response_required_signals):", text)
        self.assertIn('draft = "maybe"', text)

    def test_urgent_wins_over_needs_reply(self) -> None:
        fields = {
            "Priority": "urgent",
            "DraftNeeded": "yes",
            "CreateTask": "yes",
            "AlertNeeded": "no",
        }
        self.assertEqual(tdb._categorize_gmail(fields), "urgent")

    def test_overflow_line_after_15_items(self) -> None:
        meta = {
            "window": {
                "start": "2026-04-13T00:00:00-05:00",
                "end": "2026-04-13T20:00:00-05:00",
            }
        }
        items = [
            {
                "source": "rental_gmail",
                "category": "needs_attention",
                "summaryLine": f"line {i}",
                "refs": {"gmailMessageId": str(i)},
            }
            for i in range(17)
        ]
        md = tdb.render_markdown(meta, items)
        self.assertIn("+", md)
        self.assertTrue(any(ch.isdigit() for ch in md))
        self.assertTrue("on-demand" in md.lower() or "/triage" in md)

    def test_all_clear_message(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "output"
            out.mkdir()
            meta, items = tdb.build_items(tmp, now=tdb._parse_now_iso("2026-04-13T20:00:00-05:00"))
            self.assertEqual(items, [])
            md = tdb.render_markdown(meta, items)
            self.assertIn("all clear", md.lower())

    def test_fixture_pipeline_in_window(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "output"
            out.mkdir()
            shutil.copy(FIXTURES / "personal-summary-fragment.txt", out / "gmail-review-summary-latest.txt")
            shutil.copy(FIXTURES / "rental-summary-fragment.txt", out / "gmail-review-rental-summary-latest.txt")
            shutil.copy(FIXTURES / "hospitable-events-slice.json", out / "hospitable-events-latest.json")

            now = tdb._parse_now_iso("2026-04-13T20:00:00-05:00")
            meta, items = tdb.build_items(tmp, now=now)
            self.assertGreaterEqual(len(items), 3)
            sources = {it["source"] for it in items}
            self.assertIn("personal_gmail", sources)
            self.assertIn("rental_gmail", sources)
            self.assertIn("hospitable", sources)
            md = tdb.render_markdown(meta, items)
            self.assertIn("Triage digest", md)

    def test_body_summary_renders_under_gmail_bullet(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "output"
            out.mkdir()
            shutil.copy(FIXTURES / "personal-summary-fragment.txt", out / "gmail-review-summary-latest.txt")

            now = tdb._parse_now_iso("2026-04-13T20:00:00-05:00")
            meta, items = tdb.build_items(tmp, now=now)
            self.assertTrue(items, "fixture should produce at least one item")
            item = items[0]
            self.assertIn("bodySummary", item)
            self.assertIn("invoice", item["bodySummary"].lower())
            # Body summary is also surfaced in refs so the draft agent can reuse it.
            self.assertIn("bodySummary", item["refs"])

            md = tdb.render_markdown(meta, items)
            # Renders under the bullet so the operator has context without opening Gmail.
            self.assertIn("invoice", md.lower())
            self.assertRegex(md, r"-\s+\[personal\].+\n\s{2}Hi — following up")

    def test_body_summary_truncated_when_long(self) -> None:
        fields = {"BodySummary": "x" * 600}
        summary = tdb._body_summary_gmail(fields)
        self.assertLessEqual(len(summary), tdb.BODY_SUMMARY_MAX + 1)
        self.assertTrue(summary.endswith("…"))

    def test_bash_script_syntax(self) -> None:
        script = Path(__file__).resolve().parents[1] / "openclaw-gws-triage-digest"
        r = subprocess.run(["bash", "-n", str(script)], check=False, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_rg_markers_on_digest_script(self) -> None:
        script = Path(__file__).resolve().parents[1] / "openclaw-gws-triage-digest"
        text = script.read_text(encoding="utf-8")
        self.assertIn("send_with_topic_fallback triage_digest", text)
        self.assertIn("America/Chicago", text)
        self.assertIn("triage-digest-latest", text)

    def test_run_build_keeps_token_state_without_button_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "output"
            out.mkdir()
            shutil.copy(FIXTURES / "personal-summary-fragment.txt", out / "gmail-review-summary-latest.txt")
            shutil.copy(FIXTURES / "rental-summary-fragment.txt", out / "gmail-review-rental-summary-latest.txt")

            now = tdb._parse_now_iso("2026-04-13T20:00:00-05:00")
            meta, md, by_token = tdb.run_build(tmp, now=now)

            self.assertIn("draftTokens", meta)
            self.assertTrue(meta["draftTokens"], "needs_reply rows should mint tokens for tdr")
            first_token = meta["draftTokens"][0]
            token_state = by_token[first_token]
            self.assertIn("draftTokenByMessageId", meta)
            self.assertIn("gmailMessageId", token_state)
            self.assertTrue(token_state["gmailMessageId"])
            self.assertIn("account", token_state)
            self.assertNotIn("lastActive", token_state)
            self.assertNotIn("lastDraftText", token_state)
            self.assertNotIn("tgd" + ":", md)
            self.assertNotIn("callback_data", md)
            self.assertIn(f"(token: `{first_token}`)", md)
            self.assertIn("/bash tdr send-now <token>", md)
            self.assertIn("/bash tdr save <token>", md)
            for key in (
                "account",
                "gmailMessageId",
                "threadId",
                "subject",
                "sender",
                "date",
                "summaryLine",
                "draftTextVersion",
                "draftId",
            ):
                self.assertIn(key, token_state)

    def test_hospitable_dict_sender_renders_full_name_without_repr_leak(self) -> None:
        # Regression: `sender` in the real Hospitable payload is a dict; the
        # digest line must resolve it to full_name/first_name and never leak
        # raw Python dict repr (e.g. "{'first_name': ...}").
        msg = {
            "id": "hmsg-x",
            "sender": {
                "first_name": "Jaclyn",
                "full_name": "Jaclyn Yacoub",
                "locale": "",
                "picture_url": "https://example.invalid/jaclyn.jpg",
            },
            "reservation_id": "res-100",
            "body": "Can we get an early check-in around 1pm?",
            "direction": "guest",
            "unread": True,
            "created_at": "2026-04-13T17:15:00-05:00",
        }
        line = tdb._summary_line_hospitable(msg)
        self.assertIn("Jaclyn Yacoub", line)
        self.assertIn("early check-in", line)
        self.assertNotIn("{'", line)
        self.assertNotIn("first_name", line)

    def test_hospitable_dict_sender_first_name_fallback(self) -> None:
        # When full_name is missing, fall back to first_name — still no dict repr.
        msg = {
            "id": "hmsg-y",
            "sender": {"first_name": "Jaclyn", "locale": ""},
            "reservation_id": "res-101",
            "body": "Quick question about parking.",
            "direction": "guest",
            "unread": True,
            "created_at": "2026-04-13T17:30:00-05:00",
        }
        line = tdb._summary_line_hospitable(msg)
        self.assertIn("Jaclyn", line)
        self.assertNotIn("{'", line)
        self.assertNotIn("first_name", line)

    def test_hospitable_slice_digest_has_no_dict_repr_leak(self) -> None:
        # End-to-end: run the digest builder against the hospitable fixture and
        # assert the rendered markdown's Hospitable section contains the real
        # guest name and no dict-repr leak.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "output"
            out.mkdir()
            shutil.copy(FIXTURES / "hospitable-events-slice.json", out / "hospitable-events-latest.json")

            now = tdb._parse_now_iso("2026-04-13T20:00:00-05:00")
            meta, items = tdb.build_items(tmp, now=now)
            hosp_items = [it for it in items if it["source"] == "hospitable"]
            self.assertGreaterEqual(len(hosp_items), 2, "fixture should yield both hospitable messages in window")

            md = tdb.render_markdown(meta, items)
            self.assertIn("### Hospitable", md)
            self.assertIn("Jaclyn Yacoub", md)
            self.assertNotIn("{'", md)
            self.assertNotIn("first_name", md)
            self.assertNotIn("picture_url", md)

    def test_needs_reply_bucket_still_renders_after_callback_removal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "output"
            out.mkdir()
            shutil.copy(FIXTURES / "personal-summary-fragment.txt", out / "gmail-review-summary-latest.txt")
            shutil.copy(FIXTURES / "rental-summary-fragment.txt", out / "gmail-review-rental-summary-latest.txt")

            now = tdb._parse_now_iso("2026-04-13T20:00:00-05:00")
            meta, items = tdb.build_items(tmp, now=now)
            needs_reply = [
                it
                for it in items
                if it.get("category") == "needs_reply"
                and it.get("source") in ("personal_gmail", "rental_gmail")
            ]
            self.assertTrue(needs_reply, "fixture should still surface draft-needed Gmail rows")

            md = tdb.render_markdown(meta, items)
            self.assertIn("## Needs reply", md)


if __name__ == "__main__":
    unittest.main()
