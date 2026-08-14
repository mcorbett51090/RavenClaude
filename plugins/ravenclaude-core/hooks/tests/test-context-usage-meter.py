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


if __name__ == "__main__":
    unittest.main()
