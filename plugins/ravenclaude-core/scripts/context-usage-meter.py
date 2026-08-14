#!/usr/bin/env python3
"""context-usage-meter.py — live context percent for the session-handoff detector.

Live USED tokens come from the last `params._meta.totalTokens` on the session's
`updates.jsonl` (G3b claim 26, settled). Do NOT read `signals.json.contextTokensUsed`
as the live meter (claim 24, falsified).

Window size, ranked:
  1. same-session `signals.json.contextWindowTokens` if present
  2. owner knob (`--window` or posture `context_handoff.context_window_tokens`)
  3. Grok config `context_window = N` if found
Never hardcode 500000.

A hook process locates the session via GROK_SESSION_ID (claim 28). The agent
process does not have that env var (claim 30, falsified) — this script is for
hooks and explicit `--session-dir` tests.

Stdout: one JSON object. status=unknown (and no percent) when used or window is
missing. Exit 0 always on expected failure so a Stop hook can stay fail-open.

Python 3.9, stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

DEFAULT_THRESHOLD = 70
DEFAULT_AUTO_COMPACT = 85
MAX_UPDATES_BYTES = 64 * 1024 * 1024
_CONFIG_SCAN_CAP = 256 * 1024

_WINDOW_RE = re.compile(
    r"(?m)^[ \t]*context_window[ \t]*=[ \t]*(\d+)\b"
)
_AUTO_RE = re.compile(
    r"(?m)^[ \t]*auto_compact_threshold_percent[ \t]*=[ \t]*(\d+)\b"
)
_POSTURE_WINDOW_RE = re.compile(
    r"(?m)^[ \t]*context_window_tokens[ \t]*:[ \t]*(\d+)\b"
)
_POSTURE_THRESH_RE = re.compile(
    r"(?m)^[ \t]*threshold_percent[ \t]*:[ \t]*(\d+)\b"
)


def _int(value, lo=0, hi=10**12):
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < lo or value > hi:
        return None
    return value


def _as_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return _int(value)
    if isinstance(value, float) and value.is_integer():
        return _int(int(value))
    return None


def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / ".ravenclaude").is_dir() or (candidate / ".git").exists():
            return candidate
    return start


def encode_cwd(cwd: str) -> str:
    return quote(str(Path(cwd).resolve()), safe="")


def session_dir_from_env(payload: dict) -> Path | None:
    sid = (
        os.environ.get("GROK_SESSION_ID")
        or payload.get("sessionId")
        or payload.get("session_id")
    )
    if not isinstance(sid, str) or not sid.strip():
        return None
    cwd = (
        payload.get("workspaceRoot")
        or payload.get("cwd")
        or os.environ.get("GROK_WORKSPACE_ROOT")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or os.getcwd()
    )
    if not isinstance(cwd, str) or not cwd:
        return None
    home = os.environ.get("GROK_HOME") or str(Path.home() / ".grok")
    return Path(home) / "sessions" / encode_cwd(cwd) / sid.strip()


def last_total_tokens(updates_path: Path) -> int | None:
    """Last params._meta.totalTokens in updates.jsonl. Never signals.json used."""
    try:
        if not updates_path.is_file():
            return None
        if updates_path.stat().st_size > MAX_UPDATES_BYTES:
            return None
    except OSError:
        return None
    last = None
    try:
        with updates_path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if "totalTokens" not in line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                meta = None
                if isinstance(obj, dict):
                    params = obj.get("params")
                    if isinstance(params, dict):
                        meta = params.get("_meta")
                    if not isinstance(meta, dict):
                        meta = obj.get("_meta")
                if isinstance(meta, dict):
                    tok = _as_int(meta.get("totalTokens"))
                    if tok is not None:
                        last = tok
    except OSError:
        return None
    return last


def window_from_signals(session: Path) -> int | None:
    sig = session / "signals.json"
    try:
        if not sig.is_file():
            return None
        data = json.loads(sig.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return _as_int(data.get("contextWindowTokens"))


def _scan_int(path: Path, regex: re.Pattern) -> int | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if len(text) > _CONFIG_SCAN_CAP:
        text = text[:_CONFIG_SCAN_CAP]
    match = regex.search(text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def window_from_grok_config() -> int | None:
    home = Path(os.environ.get("GROK_HOME") or (Path.home() / ".grok"))
    return _scan_int(home / "config.toml", _WINDOW_RE)


def auto_compact_from_grok_config() -> int:
    home = Path(os.environ.get("GROK_HOME") or (Path.home() / ".grok"))
    val = _scan_int(home / "config.toml", _AUTO_RE)
    if val is None or val < 2:
        return DEFAULT_AUTO_COMPACT
    return min(99, val)


def clamp_threshold(raw: int | None, auto_compact: int) -> int:
    ceiling = max(1, auto_compact - 1)
    if raw is None:
        return min(DEFAULT_THRESHOLD, ceiling)
    return max(1, min(int(raw), ceiling))


def read_posture(root: Path) -> dict:
    path = root / ".ravenclaude" / "comfort-posture.yaml"
    out = {"mode": "off", "threshold": None, "spawn": "copy-paste-only", "window": None}
    try:
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
    except OSError:
        return out
    if len(text) > _CONFIG_SCAN_CAP:
        text = text[:_CONFIG_SCAN_CAP]
    # Restrict to a context_handoff: block when present. The next block starts
    # at a column-0 key (indented children like `mode:` must stay inside).
    block = text
    start = re.search(r"(?m)^[ \t]*#?[ \t]*context_handoff[ \t]*:", text)
    if start:
        rest = text[start.end() :]
        nxt = re.search(r"(?m)^[A-Za-z_]", rest)
        block = text[start.start() : start.end() + (nxt.start() if nxt else len(rest))]
    mode_m = re.search(r"(?m)^[ \t]*#?[ \t]*mode[ \t]*:[ \t]*(off|nag|block)\b", block)
    if mode_m:
        out["mode"] = mode_m.group(1)
    spawn_m = re.search(
        r"(?m)^[ \t]*#?[ \t]*spawn[ \t]*:[ \t]*(copy-paste-only|os-terminal)\b", block
    )
    if spawn_m:
        out["spawn"] = spawn_m.group(1)
    tw = _POSTURE_WINDOW_RE.search(block)
    if tw:
        try:
            out["window"] = int(tw.group(1))
        except ValueError:
            pass
    tt = _POSTURE_THRESH_RE.search(block)
    if tt:
        try:
            out["threshold"] = int(tt.group(1))
        except ValueError:
            pass
    return out


def measure(
    session: Path | None,
    owner_window: int | None,
    owner_threshold: int | None,
    auto_compact: int | None,
) -> dict:
    used = last_total_tokens(session / "updates.jsonl") if session is not None else None
    window = None
    if session is not None:
        window = window_from_signals(session)
    if window is None:
        window = owner_window
    if window is None:
        window = window_from_grok_config()
    auto = auto_compact if auto_compact is not None else auto_compact_from_grok_config()
    threshold = clamp_threshold(owner_threshold, auto)
    if used is None or window is None or window <= 0:
        return {
            "status": "unknown",
            "used": used,
            "window": window,
            "percent": None,
            "threshold": threshold,
            "auto_compact": auto,
            "over": False,
        }
    percent = (used / window) * 100.0
    return {
        "status": "ok",
        "used": used,
        "window": window,
        "percent": round(percent, 1),
        "threshold": threshold,
        "auto_compact": auto,
        "over": percent >= threshold,
    }


def _load_payload() -> dict:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Live Grok context-usage meter")
    ap.add_argument("--session-dir", help="Explicit session directory (tests)")
    ap.add_argument("--window", type=int, help="Owner-supplied window tokens")
    ap.add_argument("--threshold", type=int, help="Soft threshold percent")
    ap.add_argument("--auto-compact", type=int, help="Auto-compact percent ceiling")
    ap.add_argument("--project-root", help="Project root for posture (tests)")
    args = ap.parse_args(argv)

    payload = _load_payload()
    if args.session_dir:
        session = Path(args.session_dir)
    else:
        session = session_dir_from_env(payload)

    root = find_project_root(Path(args.project_root) if args.project_root else Path.cwd())
    posture = read_posture(root)
    owner_window = args.window if args.window is not None else posture.get("window")
    owner_thresh = (
        args.threshold if args.threshold is not None else posture.get("threshold")
    )
    result = measure(session, owner_window, owner_thresh, args.auto_compact)
    result["mode"] = posture.get("mode") or "off"
    result["spawn"] = posture.get("spawn") or "copy-paste-only"
    json.dump(result, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
