"""Tests for triage-reply CLI body normalization (literal \\n from argv/shell)."""

from __future__ import annotations

import importlib.util
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


def _load_triage_reply():
    script = Path(__file__).resolve().parents[1] / "openclaw-gws-triage-reply"
    loader = SourceFileLoader("_triage_reply_under_test", str(script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestNormalizeCliBodyText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mod = _load_triage_reply()

    def test_literal_newlines_become_breaks(self):
        n = self._mod.normalize_cli_body_text
        self.assertEqual(n("Hi.\\n\\nThanks!"), "Hi.\n\nThanks!")

    def test_crlf_literal(self):
        n = self._mod.normalize_cli_body_text
        self.assertEqual(n("a\\r\\nb"), "a\nb")

    def test_real_newlines_unchanged(self):
        n = self._mod.normalize_cli_body_text
        self.assertEqual(n("a\nb"), "a\nb")

    def test_no_backslash_passthrough(self):
        n = self._mod.normalize_cli_body_text
        self.assertEqual(n("plain"), "plain")


if __name__ == "__main__":
    unittest.main()
