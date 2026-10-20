#!/usr/bin/env python3
"""test_web_design_checks.py - regression suite for the web-design checkers.

Stdlib-only (unittest, no pytest). Run:  python3 test_web_design_checks.py
Exits 0 iff every case passes.

  - flesch_kincaid.py `check` must not PASS text it cannot score (review A-24):
    empty, markup-only and non-Latin-script input exit 2 [UNASSESSABLE].
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FK = os.path.join(HERE, "flesch_kincaid.py")

# 100 words of plain prose, 8 sentences. Its grade must not move.
PARAGRAPH = (
    "The shop opens at nine and closes at six on weekdays. "
    "On Saturday it opens later, at ten, and closes early, at four. "
    "We are closed on Sunday so the staff can rest. "
    "If you need help outside these hours, send us an email and we will reply the next morning. "
    "Most orders ship within two days of payment. "
    "Large orders can take a little longer because we pack each item by hand. "
    "You can track your parcel from the link in your receipt. "
    "Thank you for buying from a small local business, and we hope to see you again."
)


def run(*args: str, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args], input=stdin, capture_output=True, text=True, check=False
    )


class FleschKincaidCheck(unittest.TestCase):
    def check(self, text: str, ceiling: str = "8") -> subprocess.CompletedProcess:
        return run(FK, "check", "-", "--max", ceiling, stdin=text)

    def test_empty_input_is_unassessable(self):
        r = self.check("")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("[UNASSESSABLE]", r.stdout)

    def test_markup_only_input_is_unassessable(self):
        r = self.check("<div><p></p></div>\n<!-- hero copy goes here -->")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("[UNASSESSABLE]", r.stdout)

    def test_non_latin_input_is_unassessable(self):
        r = self.check("こんにちは。今日はいい天気ですね。")
        self.assertEqual(r.returncode, 2, r.stdout)

    def test_unassessable_file_input(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            path = fh.name
        try:
            r = run(FK, "check", path, "--max", "8")
        finally:
            os.unlink(path)
        self.assertEqual(r.returncode, 2, r.stdout)

    def test_plain_paragraph_is_scored_unchanged(self):
        self.assertEqual(len(PARAGRAPH.split()), 100)
        g = run(FK, "grade", "-", stdin=PARAGRAPH)
        self.assertEqual(g.stdout.strip(), "FK grade: 4.51  (words=100, sentences=8, syllables=129)")
        self.assertEqual(self.check(PARAGRAPH, "8").returncode, 0)
        self.assertEqual(self.check(PARAGRAPH, "4").returncode, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
