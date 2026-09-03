#!/usr/bin/env python3
"""handoff-nudge.py — Stop-hook detector. Derived values only.

⛔ REVISED (P1, precompact-handoff-convergence) — rev-1 required stdin
`reason == "end_turn"` verbatim, which NEITHER Claude Code's real Stop payload
NOR Copilot's carries in that shape, so this hook had never actually fired on
either host. The trigger is now a host-vocabulary union with an INVERTED
default: fire unless a present `reason`/`stopReason`/`stop_reason` explicitly
says the stop was NOT a turn end (Grok's `channel_closed`/`shutdown`). An
absent reason field (Claude Code, Codex) is treated as the turn-end signal
itself, not as "stay silent". Also revised: the once-per-session throttle now
stamps on emission but only SUPPRESSES on a CONFIRMED outcome (a written
handoff.md, or a recorded "nothing to do" verdict), with a 900s cooldown floor
and a 3-attempt ceiling — so one silently-eaten attempt no longer burns the
whole session's nudge budget forever. The task-id is a defined, resolvable
derivation (`session-<sanitized-session-id>`, or a continued prior task-id
when this session wrote it), suppression state is scoped per-session with a
7-day bound, and a low-headroom degradation emits a `/compact`-only line when
there isn't enough runway left to write a brief first.

Emits hookSpecificOutput.additionalContext when:
  * stdin reason is absent, OR equals "end_turn" (host-vocabulary union)
  * stopHookActive is not true
  * context_handoff.mode is nag or block (default off = silent)
  * live meter status=ok and percent >= threshold
  * the per-session throttle (confirmed-outcome gated) allows it
  * no recent (<15 min) non-empty handoff.md for this session's task-id

Never echoes lastAssistantMessage / last_assistant_message, transcript, or
plan text. Never writes handoff.md.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTINEL_FORBIDDEN = "ZZINJECTIONSENTINELZZ"

# F2 — the throttle's confirmed-outcome gate.
RETRY_COOLDOWN_SECONDS = 900
MAX_ATTEMPTS = 3

# F7 — bound the per-session state directory so it never grows unbounded.
STATE_DIR_MAX_AGE_SECONDS = 7 * 24 * 60 * 60

# F6a — below this many points of headroom to the host's auto-compact
# threshold, don't spend the turn writing a brief; emit the /compact line only.
MIN_PROCEDURE_HEADROOM = 5

# F1a — the host-vocabulary union for the stop-reason signal.
_STOP_REASON_KEYS = ("reason", "stopReason", "stop_reason")

_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]")


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


def _stop_reason(p: dict) -> str:
    """F1a — host-vocabulary union. First present, non-empty string wins."""
    for key in _STOP_REASON_KEYS:
        val = p.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


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


def _sanitize(value: str) -> str:
    """Byte-identical to precompact-digest.sh:130 —
    tr -dc 'A-Za-z0-9._-' | cut -c1-128, with '.'/'..'/empty -> 'unknown'."""
    cleaned = _SANITIZE_RE.sub("", value or "")[:128]
    if cleaned in ("", ".", ".."):
        return "unknown"
    return cleaned


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


def _task_id(root: Path, session_id: str) -> str:
    """F8 — a defined, resolvable task-id derivation.

    Continue the newest run dir when IT was written by THIS session (per
    meta.json's `last_handoff_session_id`, a key context-handoff.py's
    stamp_meta already writes — no new contract). Otherwise derive a fresh,
    `session-`-prefixed id from this session's own id, so the brief can never
    land in a foreign run dir and is stable for the lifetime of the session.
    """
    latest = _latest_task(root)
    if latest:
        dest = root / ".ravenclaude" / "runs" / latest
        hf = dest / "handoff.md"
        if hf.is_file():
            meta = dest / "meta.json"
            try:
                data = json.loads(meta.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                data = None
            if (
                isinstance(data, dict)
                and session_id
                and data.get("last_handoff_session_id") == session_id
            ):
                return latest
    return "session-" + _sanitize(session_id)


def _state_path(root: Path, session_id: str) -> Path:
    return root / ".ravenclaude" / "handoff-nudge-state" / (_sanitize(session_id) + ".json")


def _prune_state_dir(state_dir: Path) -> None:
    """F7 — bound the per-session state directory: unlink anything >7 days old."""
    try:
        now = time.time()
        for child in state_dir.iterdir():
            try:
                if child.is_file() and (now - child.stat().st_mtime) > STATE_DIR_MAX_AGE_SECONDS:
                    child.unlink()
            except OSError:
                continue
    except OSError:
        pass


def _parse_iso(value) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return (
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )
    except ValueError:
        return None


def _throttled(root: Path, session_id: str, task_id: str) -> bool:
    """F2 — the throttle's confirmed-outcome predicate.

    True iff a per-session state file exists AND at least one of:
      (a) a handoff.md for THIS session's task-id post-dates the emission
          (confirmed success — a written brief closes the session)
      (b) the agent recorded a deliberate "nothing to do" verdict
      (c) we are still inside the retry cooldown since the last attempt
      (d) the attempt ceiling has been reached (permanent silence)
    """
    path = _state_path(root, session_id)
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(data, dict):
        return False

    if data.get("verdict") == "nothing-to-do":
        return True

    attempts = data.get("attempts")
    if isinstance(attempts, int) and attempts >= MAX_ATTEMPTS:
        return True

    fired_at = _parse_iso(data.get("fired_at"))
    if fired_at is None:
        return False

    if task_id:
        hf = root / ".ravenclaude" / "runs" / task_id / "handoff.md"
        try:
            if hf.is_file() and hf.stat().st_mtime >= fired_at:
                return True
        except OSError:
            pass

    if (time.time() - fired_at) < RETRY_COOLDOWN_SECONDS:
        return True

    return False


def _stamp_throttle(root: Path, session_id: str) -> None:
    path = _state_path(root, session_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _prune_state_dir(path.parent)
        attempts = 1
        try:
            prior = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(prior, dict):
                prior_attempts = prior.get("attempts")
                if isinstance(prior_attempts, int):
                    attempts = prior_attempts + 1
        except (OSError, ValueError):
            pass
        path.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "fired_at": datetime.now(timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "attempts": attempts,
                    "verdict": None,
                }
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _recent_handoff(root: Path, task_id: str, session_id: str) -> bool:
    """F7 — scoped to THIS session's task-id (not a global runs/ scan).

    Skip if that task-id's handoff.md is non-empty and newer than 15 minutes.
    If the dir exists but was written by a DIFFERENT session (per
    meta.json's last_handoff_session_id), it does not count as "this
    session already handed off" regardless of recency.
    """
    if not task_id:
        return False
    dest = root / ".ravenclaude" / "runs" / task_id
    hf = dest / "handoff.md"
    try:
        if not hf.is_file() or hf.stat().st_size == 0:
            return False
        mtime = hf.stat().st_mtime
    except OSError:
        return False
    meta = dest / "meta.json"
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = None
    if isinstance(data, dict):
        last_sid = data.get("last_handoff_session_id")
        if last_sid and session_id and last_sid != session_id:
            return False
    return (time.time() - mtime) < 15 * 60


def _emit_nudge(
    percent: float,
    threshold: int,
    auto_compact,
    task_id: str,
    mode: str,
) -> None:
    pct = int(round(percent))
    auto_disp = auto_compact if isinstance(auto_compact, (int, float)) else None
    headroom = None
    if auto_disp is not None:
        headroom = auto_disp - percent

    if headroom is not None and headroom < MIN_PROCEDURE_HEADROOM:
        # F6a — not enough headroom left to spend the turn writing a brief;
        # a half-written handoff.md at the auto-compact boundary is worse
        # than none. Emit the ready-to-run /compact line only.
        ctx = (
            f"Context is hot (~{pct}% used; auto-compact ~{int(round(auto_disp))}% — "
            f"only ~{int(round(headroom))} points of headroom left). Not enough "
            f"headroom to write a brief first — run `/compact <steering text you "
            f"compose now, in this turn>` immediately. Compaction appends, it does "
            f"not delete the transcript. Once past the boundary, revisit the "
            f"session-handoff brief for task {task_id} if it still needs one. "
            f"Do not /fork."
        )
    else:
        auto_txt = f"{int(round(auto_disp))}%" if auto_disp is not None else "the host's threshold"
        # ⛔ This message used to say "continue in a fresh Grok window" and "do not
        # compact away the work". BOTH were wrong, and the hook fires on every host:
        #   - It named GROK unconditionally, while session-handoff/SKILL.md's own rule
        #     is that a non-Grok successor must NEVER be handed a grok launch command.
        #   - "Do not compact away the work" asserts compaction DESTROYS. This repo
        #     retracted that after measuring: compaction APPENDS (CLAUDE.md v0.244.1 —
        #     pre-boundary turns and thinking blocks are retained; compact-anchor.sh
        #     restores ADDRESSABILITY, not data).
        # The nudge states the cost honestly, names /compact as the default, and
        # walks a four-step procedure (write -> fill -> finalize -> compose) so the
        # brief is a real artifact rather than advice nobody acted on.
        ctx = (
            f"Context is hot (~{pct}% used; soft threshold {threshold}%, "
            f"auto-compact ~{auto_txt}). DEFAULT: /compact and keep going — "
            f"compaction appends, it does not delete the transcript (pre-boundary "
            f"turns and thinking blocks are retained). Before compacting, run this "
            f"4-step procedure once: "
            f"(1) `python3 plugins/ravenclaude-core/scripts/context-handoff.py write "
            f"--task-id {task_id} --host <this-host-pair>` to produce handoff.md + "
            f"handoff-seed.txt — no egress, no cheap-lane call, no "
            f"precompact-digest.py involvement of any kind. "
            f"(2) Fill the eight MODEL FILL sections of handoff.md from your own "
            f"in-turn understanding — this is what makes the brief better than any "
            f"auto-derived draft. "
            f"(3) `python3 plugins/ravenclaude-core/scripts/context-handoff.py "
            f"finalize --task-id {task_id}` to re-scrub and re-chmod the file now "
            f"that the sensitive content actually exists. "
            f"(4) Compose the /compact steering text yourself, in this same turn, "
            f"at your own trust level, and surface it as a ready-to-run line — "
            f"never read it back off handoff.md and slice it. "
            f"Reach for /handoff (a NEW window on THIS host) only if a plugin/hook "
            f"change must go live (hooks load at SessionStart, so /compact cannot "
            f"pick it up), the next reader is not this session (another CLI, a "
            f"later day, a teammate), or the task is genuinely done — then run the "
            f"session-handoff skill. Do not /fork. "
            f"Host note: on GitHub Copilot CLI/Chat, mode 'nag' delivers nothing "
            f"(Stop has no context-injection field there) — only mode 'block' "
            f"actually reaches you on that host; seeing this text means either "
            f"block fired, or you're on a host (like Claude Code) where nag "
            f"delivers."
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


def main() -> int:
    payload = _payload()

    # F1a — inverted default: fire unless a PRESENT reason explicitly says
    # this stop was not a turn end (Grok's channel_closed/shutdown). An
    # absent reason (Claude Code, Codex) is the turn-end signal itself.
    r = _stop_reason(payload)
    if r and r != "end_turn":
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
    task_id = _task_id(root, sid)

    if _throttled(root, sid, task_id):
        return 0
    if _recent_handoff(root, task_id, sid):
        return 0

    session = None
    if hasattr(meter, "session_dir_from_env"):
        session = meter.session_dir_from_env(payload)
    result = meter.measure(
        session,
        posture.get("window"),
        posture.get("threshold"),
        None,
        claude_payload=payload,
    )
    if result.get("status") != "ok" or not result.get("over"):
        return 0

    percent = result.get("percent")
    threshold = result.get("threshold")
    auto_compact = result.get("auto_compact")
    if not isinstance(percent, (int, float)) or not isinstance(threshold, int):
        return 0

    # F1a (:241) — read BOTH the camelCase and snake_case forms so the
    # derived-values-only guard can see its input on every host. Neither
    # value is ever placed in the emitted text; this is defense-in-depth.
    last_msg = payload.get("lastAssistantMessage") or payload.get("last_assistant_message") or ""
    if isinstance(last_msg, str) and SENTINEL_FORBIDDEN in last_msg:
        last_msg = ""

    _emit_nudge(float(percent), int(threshold), auto_compact, task_id, mode)
    if sid:
        _stamp_throttle(root, sid)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
