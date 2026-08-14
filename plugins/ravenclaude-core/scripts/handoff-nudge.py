#!/usr/bin/env python3
"""handoff-nudge.py — Stop-hook detector. Derived values only.

Emits hookSpecificOutput.additionalContext when:
  * stdin reason == end_turn
  * stopHookActive is not true
  * context_handoff.mode is nag or block (default off = silent)
  * live meter status=ok and percent >= threshold
  * once-per-session throttle file allows it
  * no newer non-empty handoff.md than this session start

Never echoes lastAssistantMessage, transcript, or plan text.
Never writes handoff.md.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTINEL_FORBIDDEN = "ZZINJECTIONSENTINELZZ"


def _load_meter():
    spec = importlib.util.spec_from_file_location(
        "context_usage_meter", HERE / "context-usage-meter.py"
    )
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _payload() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def _reason(p: dict) -> str:
    val = p.get("reason") or ""
    return val if isinstance(val, str) else ""


def _stop_hook_active(p: dict) -> bool:
    return bool(p.get("stopHookActive") or p.get("stop_hook_active"))


def _session_id(p: dict) -> str:
    sid = (
        os.environ.get("GROK_SESSION_ID")
        or p.get("sessionId")
        or p.get("session_id")
        or ""
    )
    return sid if isinstance(sid, str) else ""


def _project_root(p: dict) -> Path:
    cwd = (
        p.get("workspaceRoot")
        or p.get("cwd")
        or os.environ.get("GROK_WORKSPACE_ROOT")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or os.getcwd()
    )
    meter = _load_meter()
    if meter is None:
        return Path(str(cwd)).resolve()
    return meter.find_project_root(Path(str(cwd)))


def _state_path(root: Path) -> Path:
    return root / ".ravenclaude" / "handoff-nudge-state.json"


def _throttled(root: Path, session_id: str) -> bool:
    path = _state_path(root)
    if not session_id or not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    return data.get("session_id") == session_id


def _stamp_throttle(root: Path, session_id: str) -> None:
    path = _state_path(root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "fired_at": datetime.now(timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                }
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _recent_handoff(root: Path, session_started: str | None) -> bool:
    """Skip if the newest non-empty handoff.md is newer than 15 minutes.

    Proxy for "already handed off this session" when session start is unknown.
    """
    runs = root / ".ravenclaude" / "runs"
    if not runs.is_dir():
        return False
    newest = None
    try:
        for child in runs.iterdir():
            hf = child / "handoff.md"
            if hf.is_file() and hf.stat().st_size > 0:
                mtime = hf.stat().st_mtime
                if newest is None or mtime > newest:
                    newest = mtime
    except OSError:
        return False
    if newest is None:
        return False
    import time
    return (time.time() - newest) < 15 * 60


def _emit_nudge(percent: float, threshold: int, task_hint: str, mode: str) -> None:
    pct = int(round(percent))
    ctx = (
        f"Context is hot (~{pct}% used; soft threshold {threshold}%, "
        f"before auto-compact). Quality reset: run the session-handoff skill now "
        f"(/handoff). Write the brief to the existing run dir"
        f"{' (' + task_hint + ')' if task_hint else ''} "
        f"and continue in a fresh Grok window. Do not /fork. Do not grok -p. "
        f"Do not compact away the work."
    )
    if SENTINEL_FORBIDDEN in ctx:
        return
    hook_event = "Stop"
    body = {
        "hookSpecificOutput": {
            "hookEventName": hook_event,
            "additionalContext": ctx,
        }
    }
    if mode == "block":
        body["decision"] = "block"
        body["reason"] = ctx
    sys.stdout.write(json.dumps(body, separators=(",", ":")) + "\n")


def _latest_task(root: Path) -> str:
    runs = root / ".ravenclaude" / "runs"
    if not runs.is_dir():
        return ""
    best = None
    best_m = -1.0
    try:
        for child in runs.iterdir():
            if not child.is_dir():
                continue
            m = child.stat().st_mtime
            if m > best_m:
                best, best_m = child.name, m
    except OSError:
        return ""
    return best or ""


def main() -> int:
    payload = _payload()
    if _reason(payload) != "end_turn":
        return 0
    if _stop_hook_active(payload):
        return 0

    meter = _load_meter()
    if meter is None:
        return 0

    root = _project_root(payload)
    posture = meter.read_posture(root)
    mode = posture.get("mode") or "off"
    if mode not in ("nag", "block"):
        return 0

    sid = _session_id(payload)
    if _throttled(root, sid):
        return 0
    if _recent_handoff(root, None):
        return 0

    session = None
    if hasattr(meter, "session_dir_from_env"):
        session = meter.session_dir_from_env(payload)
    result = meter.measure(
        session,
        posture.get("window"),
        posture.get("threshold"),
        None,
    )
    if result.get("status") != "ok" or not result.get("over"):
        return 0

    percent = result.get("percent")
    threshold = result.get("threshold")
    if not isinstance(percent, (int, float)) or not isinstance(threshold, int):
        return 0

    last_msg = payload.get("lastAssistantMessage") or ""
    if isinstance(last_msg, str) and SENTINEL_FORBIDDEN in last_msg:
        # Must not leak. Ignore the message entirely.
        last_msg = ""

    task = _latest_task(root)
    _emit_nudge(float(percent), int(threshold), task, mode)
    if sid:
        _stamp_throttle(root, sid)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
