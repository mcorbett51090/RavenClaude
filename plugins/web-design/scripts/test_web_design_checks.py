#!/usr/bin/env python3
"""test_web_design_checks.py - regression suite for the web-design checkers.

Stdlib-only (unittest, no pytest). Run:  python3 test_web_design_checks.py
Exits 0 iff every case passes.

  - flesch_kincaid.py `check` must not PASS text it cannot score (review A-24):
    empty, markup-only and non-Latin-script input exit 2 [UNASSESSABLE].
  - check-web-anti-patterns.sh is PostToolUse: no doc may claim that
    WEB_DESIGN_STRICT=1 blocks the edit (review A-23).
  - its hardcoded-colour check exempts token files by basename only and
    sees 3/4/6/8-digit hex (review A-25).
"""

from __future__ import annotations

import os
import re
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
        self.assertEqual(
            g.stdout.strip(), "FK grade: 4.51  (words=100, sentences=8, syllables=129)"
        )
        self.assertEqual(self.check(PARAGRAPH, "8").returncode, 0)
        self.assertEqual(self.check(PARAGRAPH, "4").returncode, 1)


PLUGIN = os.path.dirname(HERE)
HOOK = os.path.join(PLUGIN, "hooks", "check-web-anti-patterns.sh")
BLOCK_CLAIM = re.compile(
    r"exit 2\s*=\s*block|BLOCK on violation|make it blocking|treats? as blocking", re.IGNORECASE
)


def run_hook(path: str, strict: bool) -> subprocess.CompletedProcess:
    env = dict(os.environ, WEB_DESIGN_STRICT="1" if strict else "0")
    return subprocess.run(
        ["bash", HOOK, path], capture_output=True, text=True, env=env, check=False
    )


class StrictModeIsNotABlock(unittest.TestCase):
    """Review A-23: the hook is PostToolUse, so strict mode cannot undo an edit."""

    def test_docs_do_not_claim_strict_mode_blocks_the_edit(self):
        for rel in ("hooks/check-web-anti-patterns.sh", "README.md", "CLAUDE.md"):
            with open(os.path.join(PLUGIN, rel), encoding="utf-8") as fh:
                text = fh.read()
            self.assertIsNone(BLOCK_CLAIM.search(text), f"{rel} still claims strict mode blocks")
            self.assertRegex(text, r"(?i)not(\*\*)? undo", f"{rel} must say strict does not undo")

    def test_strict_mode_still_exits_2_on_a_finding(self):
        with tempfile.TemporaryDirectory() as d:
            css = os.path.join(d, "src", "a.css")
            os.makedirs(os.path.dirname(css))
            with open(css, "w", encoding="utf-8") as fh:
                fh.write(".a { color: #123456; }\n")
            self.assertEqual(run_hook(css, strict=False).returncode, 0)
            self.assertEqual(run_hook(css, strict=True).returncode, 2)


class HardcodedColorCheck(unittest.TestCase):
    """Review A-25: exempt token files by basename only; see 4- and 8-digit hex."""

    def findings(self, rel_path: str, css: str) -> int:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, rel_path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(css)
            return run_hook(path, strict=False).stderr.count("[hardcoded-color]")

    def test_a_tokens_named_directory_does_not_exempt_its_files(self):
        self.assertEqual(self.findings("design-tokens-site/src/a.css", ".a{color:#abc}\n"), 1)

    def test_a_token_file_is_still_exempt(self):
        self.assertEqual(self.findings("site/src/tokens.css", ".a{color:#abc}\n"), 0)
        self.assertEqual(self.findings("site/src/palette.css", ".a{color:#abc}\n"), 0)

    def test_8_and_4_digit_hex_are_flagged(self):
        self.assertEqual(self.findings("site/src/c.css", ".a{color:#11223344}\n"), 1)
        self.assertEqual(self.findings("site/src/d.css", ".a{color:#abcd}\n"), 1)

    def test_3_and_6_digit_hex_still_flagged_and_5_digit_is_not(self):
        self.assertEqual(self.findings("site/src/e.css", ".a{color:#123456}\n"), 1)
        self.assertEqual(self.findings("site/src/f.css", ".a{color:#fff}\n"), 1)
        self.assertEqual(self.findings("site/src/g.css", ".a{content:'#12345'}\n"), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
