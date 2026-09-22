#!/usr/bin/env python3
"""caveman-route.py — the caveman auto-routing classifier (FORGE phase P1, pure).

Reads a trailing window of a Claude Code transcript's DEDUPED assistant responses and
decides whether the installed third-party `caveman` plugin should be `on`, `off`, or
left alone (`hold`) for this session. This file is a **pure classifier**: stdlib only,
no writes, no wiring into any hook. Nothing calls it yet — that is P3 (the hook body)
and P5 (offline replay), neither of which is this file's job.

Full design: `.ravenclaude/runs/forge/caveman-routing-decision-tree/plan.md`, section
"P1 — Classifier + knob schema" and "Classifier contract (`caveman-route.py`)".

Input contract (stdin JSON):
    {transcript_path, session_id, cursor_byte, prior_verdict, streak}
    `cursor_byte` is nullable — a `null`/absent value means "no prior state", i.e. this
    is the FIRST classifier call for this session (bootstrap). `prior_verdict`/`streak`
    are accepted for round-trip completeness with the output contract; this classifier
    is self-contained (it reconstructs the trailing window itself every call, per the
    cursor mechanics below) and does not need them to produce a correct verdict.

Output contract (stdout JSON):
    {verdict: "on"|"off"|"hold", mode, why, metrics, cursor_byte, streak}
    `mode` is the resolved `caveman_routing:` posture knob (off/shadow/live) — an
    independent settings echo, not derived from the transcript. `verdict` is this
    turn's transcript-driven decision. `why` is a fixed-vocabulary enum string, never
    free text (C8). `metrics` carries derived integers/floats only — counts, never raw
    prompt/tool-input/tool-result content (C8; the Gate 110 no-egress shape, applied
    here by construction — see the `no-egress-sentinel` self-test fixture).

C6 — dedupe on (requestId, message.id). Claude Code writes ONE JSONL LINE PER CONTENT
BLOCK: a single assistant response with a `thinking` + a `text` + two `tool_use` blocks
is FOUR separate lines, each carrying the full `message.usage` (repeated) and exactly
one block in `message.content[]` (verified against a live transcript this session — see
plan.md "Transcript block shape"). Summing every line inflates tool-call density
1.5-2.1x. Every line sharing (requestId, message.id) is one logical "response"; blocks
are unioned into that response's counts. C6 also specifies the fallback: an entry with
no `message.id` keeps PER-LINE counting (each such line is its own response) — matching
caveman's own fallback.

C7 — posture reads use an anchored-regex scalar idiom, NEVER PyYAML (`read_knobs`
below is the Python-side equivalent of `worktree-guard.sh`'s `sed`/`grep` idiom).

C8 — nothing here ever holds/echoes raw prompt, tool-input, or tool-result text. The
aggregator reads exactly two things out of a content block: its `type` (tool_use/text)
and, for a `text` block only, `len(block["text"])` — a character COUNT, never the text
itself. Every output field is a fixed enum, a validated integer, or a derived float.

Cursor / sliding-window mechanics (why `cursor_byte` isn't "bytes fully consumed"):
each call reads `[cursor_byte, EOF)` capped at 4 MiB (the bound `context-usage-meter.py`
already uses for its own bounded transcript tail read). The returned `cursor_byte` is
NOT simply "how far we read" — when the read contains MORE than `W` deduped responses,
the returned cursor is pulled back to the byte offset of the OLDEST response still
inside the trailing window, so the next call's `[cursor, EOF)` naturally re-covers the
same sliding window plus whatever is new, without ever re-scanning the whole transcript.
Bootstrap (cursor is null) seeks to `max(0, size - 512 KiB)` and — per the plan — the
bootstrap verdict is forced `off` regardless of what the window shows (a full first read
buys nothing: we don't yet trust a window built from a mid-file seek).

Usage:
    echo '{"transcript_path": "...", "cursor_byte": null}' | caveman-route.py
    caveman-route.py --replay /path/to/transcript.jsonl   # P5's offline-replay mode
    caveman-route.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

# ── Knob schema (settled here per the plan's P1 spec) ───────────────────────────────
DEFAULT_MODE = "off"
DEFAULT_WINDOW = 6  # [unverified — n=1; plan-A's proposal, no measurement behind the 6]
DEFAULT_ENABLE_STREAK = 4  # [unverified — n=1; claim 2 measured isolated prose prompts, not a streak]

# → off trigger thresholds. [unverified — n=1; derived from claim 1's single 14-turn session]
OFF_LAST_TWO_TOOL_THRESHOLD = 2
OFF_RATIO_THRESHOLD = 1.0

TAIL_CAP_BYTES = 4 * 1024 * 1024  # the context-usage-meter.py bound, reused here
BOOTSTRAP_TAIL_BYTES = 512 * 1024
REPLAY_CAP_BYTES = 64 * 1024 * 1024  # --replay reads a whole archived transcript, bounded
POSTURE_SCAN_CAP = 256 * 1024

_MODE_RE = re.compile(r"(?m)^[ \t]*caveman_routing:[ \t]*(off|shadow|live)[ \t]*$")
_WINDOW_KNOB_RE = re.compile(r"(?m)^[ \t]*caveman_routing_window:[ \t]*([0-9]+)[ \t]*$")
_STREAK_KNOB_RE = re.compile(r"(?m)^[ \t]*caveman_routing_enable_streak:[ \t]*([0-9]+)[ \t]*$")

_EMPTY_METRICS = {
    "responses_in_window": 0,
    "tool_use_total": 0,
    "text_total": 0,
    "avg_tool_use_per_response": 0.0,
    "last_two_max_tool_use": 0,
    "clean_streak": 0,
}


# ── C7: posture knob read — anchored regex, never PyYAML ────────────────────────────
def read_knobs(project_root: Path) -> dict:
    """Read `caveman_routing[_window|_enable_streak]` from
    `<project_root>/.ravenclaude/comfort-posture.yaml`, C7-style. Absent file, absent
    keys, or a malformed value all fall back to the documented defaults — never raise.
    """
    out = {"mode": DEFAULT_MODE, "window": DEFAULT_WINDOW, "enable_streak": DEFAULT_ENABLE_STREAK}
    path = project_root / ".ravenclaude" / "comfort-posture.yaml"
    try:
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
    except OSError:
        return out
    if len(text) > POSTURE_SCAN_CAP:
        text = text[:POSTURE_SCAN_CAP]

    m = _MODE_RE.search(text)
    if m:
        out["mode"] = m.group(1)

    w = _WINDOW_KNOB_RE.search(text)
    if w:
        try:
            val = int(w.group(1))
        except ValueError:
            val = 0
        if val > 0:
            out["window"] = val

    s = _STREAK_KNOB_RE.search(text)
    if s:
        try:
            val = int(s.group(1))
        except ValueError:
            val = 0
        if val > 0:
            out["enable_streak"] = val

    return out


# ── Bounded, incremental transcript tail read ────────────────────────────────────────
def read_tail(path: Path, cursor_byte: int | None) -> tuple[list[tuple[int, str]], int, bool, int]:
    """Read `[start, min(start+CAP, size))` of `path`, return
    `(lines, new_cursor_byte, bootstrap, size)` where `lines` is `[(byte_offset, text)]`
    for each complete JSONL line found. Never raises. A torn/partial final line (no
    trailing newline — an in-progress write) is dropped silently and the cursor never
    advances past it, so the next call re-reads it once it's complete.
    """
    try:
        size = path.stat().st_size
    except OSError:
        fallback_cursor = cursor_byte if isinstance(cursor_byte, int) else 0
        return [], fallback_cursor, cursor_byte is None, 0

    bootstrap = cursor_byte is None
    if bootstrap:
        start = max(0, size - BOOTSTRAP_TAIL_BYTES)
    else:
        start = max(0, min(int(cursor_byte), size))

    end = min(start + TAIL_CAP_BYTES, size)
    try:
        with path.open("rb") as fh:
            fh.seek(start)
            raw = fh.read(end - start)
    except OSError:
        return [], start, bootstrap, size

    # An arbitrary bootstrap seek can land mid-line; only a bootstrap seek past byte 0
    # risks a torn HEAD (a non-bootstrap cursor is always a line-start boundary we chose
    # ourselves on a prior call, so it is never dropped here).
    drop_first = bootstrap and start > 0

    lines: list[tuple[int, str]] = []
    i = 0
    consumed = 0
    first = True
    while True:
        nl = raw.find(b"\n", i)
        if nl == -1:
            break  # torn tail — dropped silently, cursor does not advance past it
        segment = raw[i:nl]
        line_offset = start + i
        if not (first and drop_first):
            if segment.strip():
                try:
                    lines.append((line_offset, segment.decode("utf-8", errors="replace")))
                except Exception:
                    pass
        first = False
        i = nl + 1
        consumed = i

    return lines, start + consumed, bootstrap, size


# ── C6: dedupe on (requestId, message.id); C8: derived values only ─────────────────
def _aggregate_responses(lines: list[tuple[int, str]]) -> list[dict]:
    """Group per-content-block JSONL lines into deduped assistant "responses". Only
    `type == "assistant"` lines are considered (never `type == "user"`, which is where
    tool_result / prompt content lives — excluded by construction, C8). A malformed or
    non-JSON line is skipped silently, never raised.
    """
    order: list[str] = []
    groups: dict[str, dict] = {}
    fallback_idx = 0

    for offset, line in lines:
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if not isinstance(obj, dict) or obj.get("type") != "assistant":
            continue
        message = obj.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            content = []

        req_id = obj.get("requestId")
        msg_id = message.get("id")
        if isinstance(msg_id, str) and msg_id:
            key = "k:%s|%s" % (req_id if isinstance(req_id, str) else "", msg_id)
        else:
            # C6 fallback: no message.id -> this line counts as its own response.
            fallback_idx += 1
            key = "f:%d" % fallback_idx

        if key not in groups:
            groups[key] = {
                "tool_use_blocks": 0,
                "text_blocks": 0,
                "text_chars": 0,
                "output_tokens": None,
                "_start_offset": offset,
            }
            order.append(key)
        rec = groups[key]

        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "tool_use":
                rec["tool_use_blocks"] += 1
            elif btype == "text":
                rec["text_blocks"] += 1
                text_val = block.get("text")
                if isinstance(text_val, str):
                    rec["text_chars"] += len(text_val)  # a COUNT only — never the text (C8)

        usage = message.get("usage")
        if isinstance(usage, dict):
            out_tok = usage.get("output_tokens")
            if isinstance(out_tok, int):
                rec["output_tokens"] = out_tok

    return [groups[k] for k in order]


def classify_window(window: list[dict], enable_streak: int) -> tuple[str, str, dict]:
    """The asymmetric-hysteresis decision over an already-windowed response list.
    Disabling is the safe direction and fires on ANY signal in the last two responses
    or the window's density ratio; enabling requires `enable_streak` CONSECUTIVE clean
    (no tool use, some prose) responses trailing the window. Everything returned is a
    derived integer/float/fixed-string — never content (C8).
    """
    streak = 0
    for r in reversed(window):
        if r["tool_use_blocks"] == 0 and r["text_chars"] > 0:
            streak += 1
        else:
            break

    if not window:
        return "hold", "hold:no-data", dict(_EMPTY_METRICS)

    n = len(window)
    tool_use_total = sum(r["tool_use_blocks"] for r in window)
    text_total = sum(r["text_blocks"] for r in window)
    avg_tool = tool_use_total / n
    last_two_max_tool = max((r["tool_use_blocks"] for r in window[-2:]), default=0)

    metrics = {
        "responses_in_window": n,
        "tool_use_total": tool_use_total,
        "text_total": text_total,
        "avg_tool_use_per_response": round(avg_tool, 4),
        "last_two_max_tool_use": last_two_max_tool,
        "clean_streak": streak,
    }

    if last_two_max_tool >= OFF_LAST_TWO_TOOL_THRESHOLD or avg_tool >= OFF_RATIO_THRESHOLD:
        return "off", "off:tool-heavy", metrics
    if streak >= enable_streak:
        return "on", "on:clean-streak", metrics
    return "hold", "hold:insufficient-signal", metrics


def classify(input_obj: dict, project_root: Path | None = None) -> dict:
    """The pure entry point: input contract dict in, output contract dict out. No
    writes, no side effects beyond reading the transcript file and the posture file.
    """
    project_root = project_root or Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    knobs = read_knobs(project_root)

    transcript_path_raw = input_obj.get("transcript_path")
    if not isinstance(transcript_path_raw, str) or not transcript_path_raw:
        return {
            "verdict": "hold",
            "mode": knobs["mode"],
            "why": "hold:no-transcript",
            "metrics": dict(_EMPTY_METRICS),
            "cursor_byte": 0,
            "streak": 0,
        }

    cursor_in = input_obj.get("cursor_byte")
    cursor_in = cursor_in if isinstance(cursor_in, int) else None

    lines, new_cursor, bootstrap, _size = read_tail(Path(transcript_path_raw), cursor_in)
    responses = _aggregate_responses(lines)

    window_n = knobs["window"]
    window = responses[-window_n:] if window_n > 0 else list(responses)

    verdict, why, metrics = classify_window(window, knobs["enable_streak"])

    if bootstrap and window:
        # Bootstrap seeked into an arbitrary mid-file position; we don't yet trust a
        # verdict built from partial history. Force off (the safe direction) regardless
        # of what the window shows — a full first read buys nothing (plan.md P1).
        verdict, why = "off", "off:bootstrap"

    cursor_out = new_cursor
    if window_n > 0 and len(responses) > window_n:
        # More responses were read than the window needs: pull the cursor BACK to the
        # start of the oldest response still IN the window, so the next call's
        # [cursor, EOF) naturally re-covers the same sliding window plus new data.
        cursor_out = window[0]["_start_offset"]

    return {
        "verdict": verdict,
        "mode": knobs["mode"],
        "why": why,
        "metrics": metrics,
        "cursor_byte": cursor_out,
        "streak": metrics["clean_streak"],
    }


# ── P5's mode: streaming replay of an archived transcript, turn by turn ─────────────
def replay(path: Path, window_n: int, enable_streak: int) -> list[dict]:
    """Stream an existing (already-complete) transcript through the classifier
    response-by-response and emit the verdict trace it WOULD have produced —
    P5's offline calibration input. Nothing calls this yet (P5 is a later phase); the
    flag ships now per the plan's file table. No bootstrap suppression here: replay has
    the full archived history from turn one, so there is no partial-read distrust to
    apply (that is a live-session-only concern).
    """
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if len(raw) > REPLAY_CAP_BYTES:
        raw = raw[-REPLAY_CAP_BYTES:]

    offset = 0
    lines: list[tuple[int, str]] = []
    for raw_line in raw.split("\n"):
        lines.append((offset, raw_line))
        offset += len(raw_line) + 1
    if lines and lines[-1][1] == "":
        lines.pop()  # the trailing artifact of a file that ends with a newline

    responses = _aggregate_responses(lines)
    trace = []
    for i in range(len(responses)):
        w = responses[max(0, i - window_n + 1) : i + 1] if window_n > 0 else responses[: i + 1]
        verdict, why, metrics = classify_window(w, enable_streak)
        trace.append({"index": i, "verdict": verdict, "why": why, "metrics": metrics})
    return trace


# ── --self-test fixtures ─────────────────────────────────────────────────────────────
def _mk_line(req_id: str, msg_id: str, block_type: str, text: str | None = None) -> str:
    block: dict = {"type": block_type}
    if block_type == "text":
        block["text"] = text or ""
    return json.dumps(
        {
            "type": "assistant",
            "requestId": req_id,
            "message": {
                "id": msg_id,
                "role": "assistant",
                "content": [block],
                "usage": {"output_tokens": 50},
            },
        }
    )


def _mk_response(idx: int, kinds: list[tuple[str, str | None]]) -> list[str]:
    req_id = "req_%04d" % idx
    msg_id = "msg_%04d" % idx
    return [_mk_line(req_id, msg_id, kind, text) for kind, text in kinds]


def _write_transcript(tmp_dir: Path, lines: list[str]) -> Path:
    p = tmp_dir / "transcript.jsonl"
    with p.open("w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line)
            fh.write("\n")
    return p


def _fixture_tool_heavy_off() -> tuple[bool, str]:
    """The 14-turn tool-heavy shape from claim 1 -> off."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        lines: list[str] = []
        for i in range(14):
            lines += _mk_response(i, [("thinking", None), ("tool_use", None), ("tool_use", None)])
        transcript = _write_transcript(tmp, lines)
        result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        if result["verdict"] != "off":
            return False, "expected off, got %r (why=%s)" % (result["verdict"], result.get("why"))
        return True, ""


def _fixture_prose_on() -> tuple[bool, str]:
    """A 6-response prose-only shape -> on."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        lines: list[str] = []
        for i in range(6):
            lines += _mk_response(i, [("thinking", None), ("text", "a clean prose turn. " * 5)])
        transcript = _write_transcript(tmp, lines)
        result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        if result["verdict"] != "on":
            return False, "expected on, got %r (metrics=%s)" % (result["verdict"], result["metrics"])
        return True, ""


def _fixture_pivot_off() -> tuple[bool, str]:
    """A mid-window pivot (prose then tools) -> off within 1 response of the pivot."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        before_lines: list[str] = []
        for i in range(5):
            before_lines += _mk_response(i, [("text", "clean prose. " * 5)])
        before_path = _write_transcript(tmp, before_lines)
        before = classify({"transcript_path": str(before_path), "cursor_byte": 0}, project_root=tmp)
        if before["verdict"] == "off":
            return False, "pre-pivot window was already off — fixture premise broken"

        pivot_lines = before_lines + _mk_response(
            5, [("thinking", None), ("tool_use", None), ("tool_use", None)]
        )
        after_path = _write_transcript(tmp, pivot_lines)
        after = classify({"transcript_path": str(after_path), "cursor_byte": 0}, project_root=tmp)
        if after["verdict"] != "off":
            return False, "expected off within 1 response of the pivot, got %r" % after["verdict"]
        return True, ""


def _fixture_torn_line() -> tuple[bool, str]:
    """A torn final line (mid-write, no trailing newline) -> no crash."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete = _mk_response(0, [("text", "hello")])
        transcript = tmp / "transcript.jsonl"
        with transcript.open("w", encoding="utf-8") as fh:
            for line in complete:
                fh.write(line)
                fh.write("\n")
            fh.write('{"type":"assistant","message":{"id":"msg_torn","content":[{"type":"tex')
            # deliberately no trailing newline: an in-progress write
        try:
            result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        except Exception as exc:  # the whole point of this fixture
            return False, "raised %r" % exc
        if "verdict" not in result:
            return False, "malformed result: %r" % result
        return True, ""


def _fixture_empty_hold() -> tuple[bool, str]:
    """An empty (or absent) transcript -> hold."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        transcript = tmp / "transcript.jsonl"
        transcript.write_text("", encoding="utf-8")
        result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        if result["verdict"] != "hold":
            return False, "expected hold for an empty transcript, got %r" % result["verdict"]

        missing = tmp / "does-not-exist.jsonl"
        result2 = classify({"transcript_path": str(missing), "cursor_byte": 0}, project_root=tmp)
        if result2["verdict"] != "hold":
            return False, "expected hold for a missing transcript, got %r" % result2["verdict"]
        return True, ""


def _fixture_dedupe_load_bearing() -> tuple[bool, str]:
    """C6's dedupe is load-bearing, not decorative.

    ONE response split across 3 raw JSONL lines (thinking + 2x tool_use, all sharing one
    requestId+message.id — the real observed shape). Deduped correctly this collapses to
    ONE response with tool_use_blocks=2, which trips the off trigger. If the dedupe key
    is removed (each line counted as its own response), the SAME 2 tool_use blocks land
    on two separate 1-block "responses" — neither reaches the >=2-per-response trigger,
    and the 2/3 density ratio stays under the >=1.0 trigger — so the (broken) undeduped
    path resolves to "hold" instead of "off". Verified manually during this build: with
    the `msg_id`/`key` grouping in `_aggregate_responses` temporarily disabled (every
    line forced into its own group), THIS fixture's `responses_in_window` assertion goes
    from 1 to 3 and the verdict assertion goes from "off" to "hold" — i.e. it fails
    exactly as documented here. That change was reverted before finishing; the shipped
    code carries the real dedupe.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        lines = _mk_response(0, [("thinking", None), ("tool_use", None), ("tool_use", None)])
        transcript = _write_transcript(tmp, lines)
        result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        metrics = result["metrics"]
        if metrics["responses_in_window"] != 1:
            return False, "dedupe failed to collapse 3 lines into 1 response: %r" % metrics
        if result["verdict"] != "off":
            return False, (
                "expected off (a deduped 2-tool_use response trips the off trigger); "
                "got %r — this is exactly the failure shape when dedupe is broken"
                % result["verdict"]
            )
        return True, ""


def _fixture_missing_message_id_fallback() -> tuple[bool, str]:
    """C6's fallback: no `message.id` -> per-line counting."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        line_a = json.dumps(
            {
                "type": "assistant",
                "requestId": "req_a",
                "message": {"content": [{"type": "tool_use"}], "usage": {"output_tokens": 10}},
            }
        )
        line_b = json.dumps(
            {
                "type": "assistant",
                "requestId": "req_b",
                "message": {
                    "content": [{"type": "text", "text": "hi"}],
                    "usage": {"output_tokens": 10},
                },
            }
        )
        transcript = _write_transcript(tmp, [line_a, line_b])
        result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        if result["metrics"]["responses_in_window"] != 2:
            return False, (
                "C6 fallback broken: 2 lines with no message.id should count as 2 "
                "responses, got %r" % result["metrics"]
            )
        return True, ""


def _fixture_malformed_json_skipped() -> tuple[bool, str]:
    """A non-JSON line is skipped silently, never raised."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        good = _mk_response(0, [("text", "fine")])
        lines = ["not json at all {{{"] + good + ["also not json"]
        transcript = _write_transcript(tmp, lines)
        try:
            result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        except Exception as exc:
            return False, "raised %r" % exc
        if result["metrics"]["responses_in_window"] != 1:
            return False, "expected the 1 valid response to survive, got %r" % result["metrics"]
        return True, ""


def _fixture_bootstrap_forces_off() -> tuple[bool, str]:
    """Bootstrap (cursor_byte omitted) forces off even over a window that would
    otherwise be "on"."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        lines: list[str] = []
        for i in range(6):
            lines += _mk_response(i, [("text", "clean prose. " * 5)])
        transcript = _write_transcript(tmp, lines)
        result = classify({"transcript_path": str(transcript)}, project_root=tmp)  # no cursor_byte
        if result["verdict"] != "off" or result["why"] != "off:bootstrap":
            return False, "expected off:bootstrap, got %r/%r" % (result["verdict"], result["why"])
        return True, ""


def _fixture_knob_parsing() -> tuple[bool, str]:
    """C7 knob read: defaults, overrides, and a malformed-value fallback."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        defaults = read_knobs(tmp)
        if defaults != {"mode": "off", "window": 6, "enable_streak": 4}:
            return False, "unexpected defaults: %r" % defaults

        posture_dir = tmp / ".ravenclaude"
        posture_dir.mkdir()
        (posture_dir / "comfort-posture.yaml").write_text(
            "caveman_routing: shadow\ncaveman_routing_window: 3\ncaveman_routing_enable_streak: 2\n",
            encoding="utf-8",
        )
        knobs = read_knobs(tmp)
        if knobs != {"mode": "shadow", "window": 3, "enable_streak": 2}:
            return False, "override parsing failed: %r" % knobs

        (posture_dir / "comfort-posture.yaml").write_text(
            "caveman_routing: live\ncaveman_routing_window: not-a-number\n", encoding="utf-8"
        )
        knobs2 = read_knobs(tmp)
        if knobs2["mode"] != "live" or knobs2["window"] != 6:
            return False, "malformed window value did not fall back to default: %r" % knobs2
        return True, ""


def _fixture_no_egress_sentinel() -> tuple[bool, str]:
    """C8: raw content never reaches the output, even when it appears in a text block."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        sentinel = "SENTINEL-DO-NOT-EGRESS-4f9c2"
        lines = _mk_response(0, [("text", "some prose containing %s in the body" % sentinel)])
        transcript = _write_transcript(tmp, lines)
        result = classify({"transcript_path": str(transcript), "cursor_byte": 0}, project_root=tmp)
        if sentinel in json.dumps(result):
            return False, "C8 violated: raw transcript content leaked into classifier output"
        return True, ""


_FIXTURES = [
    ("14-turn-tool-heavy-off", _fixture_tool_heavy_off),
    ("6-response-prose-on", _fixture_prose_on),
    ("mid-window-pivot-off", _fixture_pivot_off),
    ("torn-final-line-no-crash", _fixture_torn_line),
    ("empty-transcript-hold", _fixture_empty_hold),
    ("dedupe-load-bearing", _fixture_dedupe_load_bearing),
    ("missing-message-id-fallback", _fixture_missing_message_id_fallback),
    ("malformed-json-line-skipped", _fixture_malformed_json_skipped),
    ("bootstrap-forces-off", _fixture_bootstrap_forces_off),
    ("knob-parsing-defaults-and-override", _fixture_knob_parsing),
    ("no-egress-sentinel", _fixture_no_egress_sentinel),
]


def self_test() -> int:
    fails = []
    for name, fn in _FIXTURES:
        try:
            ok, detail = fn()
        except Exception as exc:  # a crashing fixture is itself a failure
            ok, detail = False, "raised %r" % exc
        if not ok:
            fails.append((name, detail))

    if fails:
        for name, detail in fails:
            print("FAIL: %s: %s" % (name, detail), file=sys.stderr)
        print(
            "caveman-route self-test: %d/%d passed" % (len(_FIXTURES) - len(fails), len(_FIXTURES)),
            file=sys.stderr,
        )
        return 1

    print("caveman-route self-test: %d/%d passed" % (len(_FIXTURES), len(_FIXTURES)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Caveman auto-routing classifier — pure, stdlib-only, no side effects."
    )
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument(
        "--replay", metavar="TRANSCRIPT", help="stream an archived transcript, emit the verdict trace"
    )
    ap.add_argument("--window", type=int, help="override caveman_routing_window (--replay only)")
    ap.add_argument(
        "--enable-streak", type=int, help="override caveman_routing_enable_streak (--replay only)"
    )
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.replay:
        project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        knobs = read_knobs(project_root)
        window_n = args.window if args.window and args.window > 0 else knobs["window"]
        streak_n = (
            args.enable_streak if args.enable_streak and args.enable_streak > 0 else knobs["enable_streak"]
        )
        trace = replay(Path(args.replay), window_n, streak_n)
        print(
            json.dumps(
                {"transcript": args.replay, "window": window_n, "enable_streak": streak_n, "trace": trace},
                indent=2,
            )
        )
        return 0

    try:
        raw_in = sys.stdin.read()
    except Exception:
        raw_in = ""
    try:
        input_obj = json.loads(raw_in) if raw_in.strip() else {}
    except ValueError:
        input_obj = {}
    if not isinstance(input_obj, dict):
        input_obj = {}

    print(json.dumps(classify(input_obj)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
