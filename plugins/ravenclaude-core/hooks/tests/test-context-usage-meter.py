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


def _claude_transcript_with_model(tmp: Path, entries) -> Path:
    """Like _claude_transcript but each entry is (usage_dict, model_id_or_None)."""
    path = tmp / "transcript.jsonl"
    lines = []
    for usage, model in entries:
        message = {"usage": usage}
        if model is not None:
            message["model"] = model
        lines.append(json.dumps({"type": "assistant", "message": message}) + "\n")
    path.write_text("".join(lines))
    return path


class ModelAwareWindowTests(unittest.TestCase):
    """Added 2026-09-08 — the meter's window used to be hardcoded to 200000 for
    every Claude Code session regardless of the actual running model, which is
    wrong by 5x for every current model except haiku. See CLAUDE.md milestone
    "Context-usage meter becomes model-aware"."""

    def test_governed_sonnet_id_resolves_from_catalog(self):
        r = meter.resolve_context_window_for_model("claude-sonnet-5")
        self.assertEqual(r, (1000000, "catalog"))

    def test_governed_haiku_id_resolves_from_catalog(self):
        r = meter.resolve_context_window_for_model("claude-haiku-4-5-20251001")
        self.assertEqual(r, (200000, "catalog"))

    def test_unresolved_haiku_shaped_id_uses_heuristic(self):
        r = meter.resolve_context_window_for_model("claude-haiku-9000-hypothetical")
        self.assertEqual(r, (200000, "heuristic"))

    def test_unresolved_non_haiku_id_uses_generic_heuristic(self):
        r = meter.resolve_context_window_for_model("claude-opus-99-hypothetical")
        self.assertEqual(r, (1000000, "heuristic"))

    def test_none_model_id_resolves_to_none_none(self):
        self.assertEqual(meter.resolve_context_window_for_model(None), (None, "none"))
        self.assertEqual(meter.resolve_context_window_for_model(""), (None, "none"))

    def test_measure_uses_catalog_window_for_sonnet_session(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript_with_model(
                Path(raw), [({"input_tokens": 100}, "claude-sonnet-5")]
            )
            payload = {"transcript_path": str(transcript)}
            r = meter.measure(None, None, 70, None, claude_payload=payload)
            self.assertEqual(r["status"], "ok")
            self.assertEqual(r["window"], 1000000)
            self.assertEqual(r["window_source"], "catalog")
            self.assertEqual(r["model_id"], "claude-sonnet-5")
            # this is the whole point: 100 used / 1,000,000 window is nowhere
            # near the old (wrong) 200000-window percent of 0.05.
            self.assertEqual(r["percent"], round(100 / 1000000 * 100, 1))

    def test_measure_uses_heuristic_window_for_unresolved_haiku_shaped_id(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript_with_model(
                Path(raw), [({"input_tokens": 50}, "claude-haiku-9000-hypothetical")]
            )
            payload = {"transcript_path": str(transcript)}
            r = meter.measure(None, None, 70, None, claude_payload=payload)
            self.assertEqual(r["window"], 200000)
            self.assertEqual(r["window_source"], "heuristic")

    def test_owner_window_still_wins_over_model_resolution(self):
        """Explicit owner_window (rank 2) must beat model-aware resolution (rank 4)."""
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript_with_model(
                Path(raw), [({"input_tokens": 100}, "claude-sonnet-5")]
            )
            payload = {"transcript_path": str(transcript)}
            r = meter.measure(None, 42, 70, None, claude_payload=payload)
            self.assertEqual(r["window"], 42)

    def test_no_model_in_transcript_still_falls_back_to_default(self):
        """Byte-identical to the pre-existing test_claude_default_window_only_applies_to_claude_source
        behavior — a transcript with no model field must still resolve DEFAULT_CLAUDE_WINDOW,
        never crash, never silently pick a heuristic window."""
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript_with_model(Path(raw), [({"input_tokens": 100}, None)])
            payload = {"transcript_path": str(transcript)}
            r = meter.measure(None, None, 70, None, claude_payload=payload)
            self.assertEqual(r["window"], meter.DEFAULT_CLAUDE_WINDOW)
            self.assertEqual(r["window_source"], "default")
            self.assertIsNone(r["model_id"])

    def test_last_assistant_turn_model_wins(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = _claude_transcript_with_model(
                Path(raw),
                [
                    ({"input_tokens": 10}, "claude-haiku-4-5-20251001"),
                    ({"input_tokens": 20}, "claude-sonnet-5"),
                ],
            )
            payload = {"transcript_path": str(transcript)}
            r = meter.measure(None, None, 70, None, claude_payload=payload)
            self.assertEqual(r["model_id"], "claude-sonnet-5")
            self.assertEqual(r["window"], 1000000)

    def test_grok_path_gets_no_model_id_or_effective_budget_regression(self):
        """The Grok path must stay byte-identical — model_id is always None there,
        and effective_budget is still computed from whatever window it resolved
        (this field is new and additive on both paths, not Claude-Code-only)."""
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(Path(raw), [100])
            r = meter.measure(sess, 1000, 70, 85)
            self.assertIsNone(r["model_id"])
            self.assertEqual(r["effective_budget"], meter.effective_budget(1000))


class EffectiveBudgetTests(unittest.TestCase):
    def test_default_reservation_and_margin(self):
        # 1,000,000 window: 16000 reserved + 5% (50000) overhead = 934000.
        self.assertEqual(meter.effective_budget(1000000), 934000)

    def test_haiku_window_default_reservation_and_margin(self):
        # 200,000 window: 16000 reserved + 5% (10000) overhead = 174000.
        self.assertEqual(meter.effective_budget(200000), 174000)

    def test_overrides_are_honored(self):
        self.assertEqual(
            meter.effective_budget(1000000, reserved_output=0, overhead_margin_pct=0), 1000000
        )

    def test_never_goes_negative(self):
        self.assertEqual(meter.effective_budget(100, reserved_output=1000), 0)

    def test_measure_emits_effective_budget_on_ok(self):
        with tempfile.TemporaryDirectory() as raw:
            sess = _session(Path(raw), [100])
            r = meter.measure(sess, 1000, 70, 85, reserved_output=0, overhead_margin_pct=0)
            self.assertEqual(r["effective_budget"], 1000)

    def test_measure_emits_none_effective_budget_on_unknown(self):
        with tempfile.TemporaryDirectory() as raw:
            sess = Path(raw) / "empty"
            sess.mkdir()
            r = meter.measure(sess, 1000, 70, 85)
            self.assertEqual(r["status"], "unknown")
            self.assertIsNone(r["effective_budget"])


if __name__ == "__main__":
    unittest.main()
