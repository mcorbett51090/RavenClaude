#!/usr/bin/env python3
"""Unit tests for context-usage-meter.py (P1).

Live used = last updates.jsonl params._meta.totalTokens.
A mutant that reads signals.json.contextTokensUsed as used MUST fail.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "context_usage_meter", HERE / "scripts" / "context-usage-meter.py"
)
meter = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(meter)


def _session(tmp: Path, updates, signals=None) -> Path:
    d = tmp / "sess"
    d.mkdir()
    if updates is not None:
        lines = []
        for used in updates:
            lines.append(
                json.dumps({"params": {"_meta": {"totalTokens": used}}}) + "\n"
            )
        (d / "updates.jsonl").write_text("".join(lines))
    if signals is not None:
        (d / "signals.json").write_text(json.dumps(signals))
    return d


class MeterTests(unittest.TestCase):
    def test_last_line_wins(self):
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(Path(raw), [100, 200, 350])
            r = meter.measure(sess, 1000, 70, 85)
            self.assertEqual(r["status"], "ok")
            self.assertEqual(r["used"], 350)
            self.assertEqual(r["window"], 1000)
            self.assertEqual(r["percent"], 35.0)
            self.assertFalse(r["over"])

    def test_signals_window_not_used(self):
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(
                Path(raw),
                [400],
                {"contextWindowTokens": 2000, "contextTokensUsed": 99999},
            )
            r = meter.measure(sess, None, 70, 85)
            self.assertEqual(r["used"], 400)
            self.assertEqual(r["window"], 2000)
            self.assertNotEqual(r["used"], 99999)

    def test_absent_signals_no_owner_window_is_unknown(self):
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(Path(raw), [400])
            r = meter.measure(sess, None, 70, 85)
            # no signals window, no owner window, grok config may or may not exist
            if r["window"] is None:
                self.assertEqual(r["status"], "unknown")
                self.assertIsNone(r["percent"])

    def test_owner_window_when_no_signals(self):
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(Path(raw), [800])
            r = meter.measure(sess, 1000, 70, 85)
            self.assertEqual(r["status"], "ok")
            self.assertEqual(r["window"], 1000)
            self.assertTrue(r["over"])  # 80% >= 70

    def test_clamp_threshold_below_auto_compact(self):
        self.assertEqual(meter.clamp_threshold(90, 85), 84)
        self.assertEqual(meter.clamp_threshold(None, 85), 70)
        self.assertEqual(meter.clamp_threshold(0, 85), 1)

    def test_missing_updates_unknown(self):
        with tempfile.TemporaryDirectory() as raw:
            sess = Path(raw) / "empty"
            sess.mkdir()
            r = meter.measure(sess, 1000, 70, 85)
            self.assertEqual(r["status"], "unknown")
            self.assertFalse(r["over"])

    def test_used_never_comes_from_signals_context_tokens_used(self):
        """Mutant guard: used must not equal signals.contextTokensUsed when they differ."""
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(
                Path(raw),
                [10],
                {"contextWindowTokens": 100, "contextTokensUsed": 99},
            )
            r = meter.measure(sess, None, 70, 85)
            self.assertEqual(r["used"], 10)
            src = (HERE / "scripts" / "context-usage-meter.py").read_text()
            # The live-used function must not mention contextTokensUsed as a read key.
            live_fn = src.split("def last_total_tokens", 1)[1].split("def window_from_signals", 1)[0]
            self.assertNotIn("contextTokensUsed", live_fn)


def _claude_transcript(tmp: Path, usages) -> Path:
    """Build a minimal Claude Code transcript: one assistant line per usage dict."""
    path = tmp / "transcript.jsonl"
    lines = []
    for usage in usages:
        lines.append(
            json.dumps({"type": "assistant", "message": {"usage": usage}}) + "\n"
        )
    path.write_text("".join(lines))
    return path


class ClaudeCodePathTests(unittest.TestCase):
    """The Claude Code fallback added 2026-08-26 — see the module docstring's
    ⛔ CORRECTED note. Every existing Grok-path test above must remain
    untouched and green; these are purely additive."""

    def test_grok_path_untouched_by_new_default_param(self):
        """A caller that never passes claude_payload gets byte-identical behavior."""
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(Path(raw), [100])
            r = meter.measure(sess, 1000, 70, 85)
            self.assertEqual(r["status"], "ok")
            self.assertEqual(r["used"], 100)

    def test_claude_transcript_resolves_usage_and_status_ok(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript(
                Path(raw),
                [
                    {
                        "input_tokens": 5,
                        "cache_read_input_tokens": 1000,
                        "cache_creation_input_tokens": 2000,
                        "output_tokens": 40,
                    }
                ],
            )
            payload = {"transcript_path": str(transcript), "session_id": "sid-1", "cwd": raw}
            r = meter.measure(None, 10000, 70, None, claude_payload=payload)
            self.assertEqual(r["status"], "ok")
            self.assertEqual(r["used"], 5 + 1000 + 2000)
            self.assertEqual(r["source"], "claude-code")
            # output_tokens must NOT be counted as context usage.
            self.assertNotEqual(r["used"], 5 + 1000 + 2000 + 40)

    def test_claude_last_assistant_turn_wins(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript(
                Path(raw),
                [
                    {"input_tokens": 10, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    {"input_tokens": 999, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                ],
            )
            payload = {"transcript_path": str(transcript)}
            r = meter.measure(None, 10000, 70, None, claude_payload=payload)
            self.assertEqual(r["used"], 999)

    def test_grok_reading_never_overridden_by_claude_fallback(self):
        """When the Grok session HAS a reading, the Claude payload must be ignored."""
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(Path(raw), [50])
            transcript = _claude_transcript(Path(raw), [{"input_tokens": 999999}])
            payload = {"transcript_path": str(transcript)}
            r = meter.measure(sess, 1000, 70, 85, claude_payload=payload)
            self.assertEqual(r["used"], 50)
            self.assertEqual(r["source"], "grok")

    def test_claude_default_window_only_applies_to_claude_source(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript(Path(raw), [{"input_tokens": 100}])
            payload = {"transcript_path": str(transcript)}
            # no owner_window, no signals.json (there is none for Claude Code) —
            # the Claude default (200000) must apply.
            r = meter.measure(None, None, 70, None, claude_payload=payload)
            self.assertEqual(r["window"], meter.DEFAULT_CLAUDE_WINDOW)

    def test_claude_transcript_path_prefers_payload_field(self):
        payload = {"transcript_path": "/tmp/does-not-matter.jsonl", "session_id": "x", "cwd": "/tmp"}
        p = meter.claude_transcript_path(payload)
        self.assertEqual(str(p), "/tmp/does-not-matter.jsonl")

    def test_claude_transcript_path_falls_back_to_reconstruction(self):
        payload = {"session_id": "abc123", "cwd": "/Users/x/proj"}
        p = meter.claude_transcript_path(payload)
        self.assertIsNotNone(p)
        self.assertTrue(str(p).endswith("-Users-x-proj/abc123.jsonl"))

    def test_no_usable_source_still_unknown(self):
        """No Grok session, no Claude transcript -> unknown, never a crash."""
        r = meter.measure(None, None, 70, None, claude_payload={})
        self.assertEqual(r["status"], "unknown")
        self.assertIsNone(r["percent"])

    def test_missing_transcript_file_is_none_not_error(self):
        payload = {"transcript_path": "/nonexistent/path/does-not-exist.jsonl"}
        used = meter.last_total_tokens_claude(meter.claude_transcript_path(payload))
        self.assertIsNone(used)


if __name__ == "__main__":
    unittest.main()
