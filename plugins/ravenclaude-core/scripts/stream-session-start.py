#!/usr/bin/env python3
"""stream-session-start.py — SessionStart classifier wiring for Agentic Work-Streams (P2).

Implements the locked tiebreak: **session-boundary classification, sticky active stream.**
At session start, this helper decides whether to SUGGEST (or, on explicit opt-in, SET) an
active stream — but ONLY when no stream is already active. When a stream IS active it returns
a sticky no-op, so the classifier never re-runs while a stream is active (the false-new-stream
mitigation). It is consumed by capability-orientation.py to render a banner suggestion.

CONFIG (`.ravenclaude/comfort-posture.yaml`, top-level scalars, parsed minimally — no PyYAML):
  stream_classify: off | label_only | auto      (default: label_only)
    off        — do nothing; never classify or suggest.
    label_only — classify when no stream is active, SUGGEST in the banner; never auto-switch.
    auto       — same, but ALSO set the active stream when the match is confident (opt-in).
  stream_threshold: <float in [0.05, 0.95]>       (default: 0.18; out-of-range clamped)
    The cosine floor for a "confident" match.

WHAT IT CLASSIFIES (derived, low-cost, no prompt text):
  The current git branch + the subjects of the last few commits — a cheap, prompt-free signal
  for "what is this session likely about." Classified against the per-stream centroids in the
  registry. NO prompt text is read; the result carries only derived labels/slugs/scores.

DETERMINISM / FAIL-SAFE:
  All git calls are read-only, bounded, and best-effort; any failure → an inert result.
  Returns a plain dict; the caller decides how to render. The optional `auto` set-active is the
  only write, and only when explicitly configured + confident + no stream already active.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CLASSIFY = _HERE / "stream-classify.py"
_OPS = _HERE / "stream-ops.py"

_VALID_MODES = ("off", "label_only", "auto")
_DEFAULT_MODE = "label_only"
_DEFAULT_THRESHOLD = 0.18
_THRESH_MIN, _THRESH_MAX = 0.05, 0.95
_MAX_COMMITS = 8

# Cap the config text we scan so a pathologically large file can't cost us time
# (defense-in-depth alongside the de-ambiguated numeric pattern below).
_CONFIG_SCAN_CAP = 65536

# NB (security): the numeric capture is written as `\d+(?:\.\d+)?|\.\d+` — a single
# unambiguous alternation — NOT `[0-9]*\.?[0-9]+`. The ambiguous form backtracks
# catastrophically (ReDoS) on a long digit run that the anchored tail can't satisfy
# (a hostile `.ravenclaude/comfort-posture.yaml` reachable from the SessionStart
# banner). This form has no overlapping quantifiers, so it is linear-time.
_MODE_RE = re.compile(r"^[ \t]*stream_classify[ \t]*:[ \t]*([A-Za-z_]{1,16})[ \t]*(?:#.*)?$", re.MULTILINE)
_THRESH_RE = re.compile(
    r"^[ \t]*stream_threshold[ \t]*:[ \t]*(\d+(?:\.\d+)?|\.\d+)[ \t]*(?:#.*)?$", re.MULTILINE
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_config(root: Path) -> dict:
    """Read stream_classify + stream_threshold from comfort-posture.yaml (minimal parse).

    Fail-safe: absent file / unparseable → defaults. An out-of-range or non-numeric threshold
    is clamped/defaulted. An unknown mode → the default mode.
    """
    mode = _DEFAULT_MODE
    threshold = _DEFAULT_THRESHOLD
    try:
        cfg = root / ".ravenclaude" / "comfort-posture.yaml"
        text = cfg.read_text(encoding="utf-8") if cfg.is_file() else ""
    except OSError:
        text = ""
    # Bound the text we scan (ReDoS defense-in-depth — see the _THRESH_RE note).
    if len(text) > _CONFIG_SCAN_CAP:
        text = text[:_CONFIG_SCAN_CAP]
    m = _MODE_RE.search(text)
    if m and m.group(1) in _VALID_MODES:
        mode = m.group(1)
    t = _THRESH_RE.search(text)
    if t:
        try:
            val = float(t.group(1))
            threshold = min(_THRESH_MAX, max(_THRESH_MIN, val))
        except ValueError:
            threshold = _DEFAULT_THRESHOLD
    return {"mode": mode, "threshold": threshold}


def _git_signal(root: Path) -> str:
    """Cheap, prompt-free 'what is this session about' signal: branch + recent commit subjects.

    Read-only, bounded, best-effort. Returns "" on any failure.
    """
    parts: list[str] = []
    try:
        b = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if b.returncode == 0:
            parts.append(b.stdout.strip().replace("/", " ").replace("-", " "))
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        log = subprocess.run(
            ["git", "-C", str(root), "log", f"-{_MAX_COMMITS}", "--pretty=%s"],
            capture_output=True, text=True, timeout=5,
        )
        if log.returncode == 0:
            parts.append(log.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return "\n".join(p for p in parts if p)


def classify_session(root: Path) -> dict:
    """The SessionStart decision. Returns a derived-only result dict:

      {
        "mode":        "off"|"label_only"|"auto",
        "sticky":      bool,            # True when a stream is already active (no classify)
        "active":      str | None,      # the already-active stream (if sticky)
        "suggestion":  str | None,      # suggested stream id (when not sticky + confident)
        "score":       float,           # the suggestion's cosine (0.0 if none)
        "switched":    bool,            # True iff auto-mode set the active stream this call
      }

    Never raises; any failure degrades to an inert result.
    """
    result = {
        "mode": _DEFAULT_MODE, "sticky": False, "active": None,
        "suggestion": None, "score": 0.0, "switched": False,
    }
    try:
        cfg = read_config(root)
        result["mode"] = cfg["mode"]
        if cfg["mode"] == "off":
            return result

        ops = _load(_OPS, "stream_ops")
        clf = _load(_CLASSIFY, "stream_classify")

        # STICKY: a stream is already active → do NOT re-classify (the load-bearing rule).
        active = ops.read_active(root)
        if active:
            result["sticky"] = True
            result["active"] = active
            return result

        centroids = ops.get_centroids(root)
        if not centroids:
            return result  # no streams to match against

        signal = _git_signal(root)
        if not signal:
            return result

        res = clf.classify(signal, centroids, threshold=cfg["threshold"])
        if res["confident"] and res["best_stream"]:
            result["suggestion"] = res["best_stream"]
            result["score"] = round(float(res["best_score"]), 4)
            # AUTO: opt-in only — set the active stream when confident + nothing active.
            if cfg["mode"] == "auto":
                try:
                    ops.set_active(root, res["best_stream"])
                    result["switched"] = True
                except ValueError:
                    result["switched"] = False
    except Exception:
        # Total fail-safe — an inert result, never a session-start break.
        return result
    return result


# ── CLI shim (for the gate + manual inspection) ───────────────────────────────

if __name__ == "__main__":
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(description="SessionStart stream classifier (sticky, P2).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--config-only", action="store_true", help="emit only the parsed config")
    args = ap.parse_args()
    root = Path(args.root)
    if args.config_only:
        print(json.dumps(read_config(root), sort_keys=True))
        sys.exit(0)
    print(json.dumps(classify_session(root), sort_keys=True))
