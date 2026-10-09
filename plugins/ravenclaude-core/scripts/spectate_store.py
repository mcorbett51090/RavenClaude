#!/usr/bin/env python3
"""spectate_store.py — pure library for Spectate JSONL + reducer (v0.1).

No HTTP. Server wrappers call these helpers and emit status/headers/body.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TAIL_BYTES = 5 * 1024 * 1024  # 5 MiB
SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
HARNESSES = (
    "claude-code",
    "codex-cli",
    "copilot-cli",
    "copilot-vscode",
    "cursor",
    "gemini-cli",
    "grok-build",
    "grok-bot",
    "unknown",
)
SENSITIVE_KEYS = frozenset(
    {
        "args",
        "input",
        "output",
        "result",
        "prompt",
        "content",
        "messages",
        "secret",
        "token",
        "password",
        "authorization",
        "raw",
    }
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
STEPS = (
    "assemble",
    "call-model",
    "classify",
    "execute-tools",
    "package",
    "update-context",
)
STEP_CAP = {
    "assemble": "session",
    "call-model": "prompt",
    "classify": "prompt",
    "execute-tools": "tool_pre",
    "package": "tool_post",
    "update-context": "compact",
}
DENY_RANK = {
    "denied-org": 4,
    "denied-plugin": 3,
    "denied-user": 2,
    "denied-harness": 1,
}
TERMINAL = frozenset(
    {
        "succeeded",
        "failed",
        "denied-org",
        "denied-plugin",
        "denied-user",
        "denied-harness",
        "unavailable-harness",
    }
)
KIND_ORDER = {
    "session.start": 0,
    "prompt.submit": 1,
    "tool.pre": 2,
    "subagent.start": 2,
    "compact.pre": 2,
    "permission.request": 3,
    "tool.post": 4,
    "tool.fail": 4,
    "permission.resolve": 4,
    "turn.end": 4,
    "subagent.stop": 4,
    "steer.applied": 4,
    "session.end": 5,
    "stream.truncated": 6,
    "emitter.truncated": 7,
    "step.seed": 8,
}


def now_rfc3339() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def runs_root(project_root: Path | str) -> Path:
    return Path(project_root).resolve() / ".ravenclaude" / "runs"


def validate_session_id(session_id: str) -> bool:
    if not session_id or session_id in (".", "..") or session_id.startswith("."):
        return False
    if "/" in session_id or "\\" in session_id or "%" in session_id:
        return False
    return bool(SESSION_RE.fullmatch(session_id))


def _open_nofollow(path: Path) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(str(path), flags)


def resolve_run_dir(project_root: Path | str, session_id: str) -> Path | None:
    if not validate_session_id(session_id):
        return None
    root = runs_root(project_root)
    candidate = (root / session_id).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_dir() or candidate.is_symlink():
        return None
    return candidate


def resolve_fixed_file(run_dir: Path, name: str) -> Path | None:
    root = run_dir.parent.resolve()
    path = (run_dir / name).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    if not path.is_file() or path.is_symlink():
        return None
    return path


def _scrub_string(s: str) -> str:
    s = CONTROL_RE.sub("", s)
    low = s.lower()
    for needle in ("sk-", "ghp_", "ghu_", "xoxb-", "password=", "authorization:"):
        if needle in low:
            return "[scrubbed]"
    return s[:512]


def scrub_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if str(k).lower() in SENSITIVE_KEYS:
                continue
            out[k] = scrub_obj(v)
        return out
    if isinstance(obj, list):
        return [scrub_obj(x) for x in obj]
    if isinstance(obj, str):
        return _scrub_string(obj)
    return obj


def read_jsonl_tail(path: Path, *, max_bytes: int = TAIL_BYTES) -> tuple[list[dict], dict]:
    """Return (events, meta) where meta has skipped_malformed, truncated, size, mtime_ns."""
    meta = {
        "skipped_malformed": 0,
        "truncated": False,
        "size": 0,
        "mtime_ns": 0,
    }
    try:
        st = path.stat()
    except OSError:
        return [], meta
    meta["size"] = st.st_size
    meta["mtime_ns"] = getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9))
    if st.st_size == 0:
        return [], meta
    start = 0
    if st.st_size > max_bytes:
        start = st.st_size - max_bytes
        meta["truncated"] = True
    fd = _open_nofollow(path)
    try:
        if start:
            os.lseek(fd, start, os.SEEK_SET)
        raw = os.read(fd, st.st_size - start if start else st.st_size)
    finally:
        os.close(fd)
    if start and raw:
        # drop partial first line
        nl = raw.find(b"\n")
        if nl >= 0:
            raw = raw[nl + 1 :]
        else:
            raw = b""
    text = raw.decode("utf-8", errors="replace")
    events: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            meta["skipped_malformed"] += 1
            continue
        if not isinstance(obj, dict):
            meta["skipped_malformed"] += 1
            continue
        events.append(scrub_obj(obj))
    return events, meta


def load_capabilities(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cap_state(capabilities: dict, harness: str, key: str) -> str:
    h = capabilities.get("harnesses", {}).get(harness, {})
    cell = h.get(key) or {}
    return cell.get("state", "unknown")


def seed_status(
    capabilities: dict, harness: str, step: str, event_count: int
) -> tuple[str, str | None]:
    key = STEP_CAP[step]
    state = cap_state(capabilities, harness, key)
    if state == "unsupported":
        return "unavailable-harness", None
    if state == "unknown":
        return "idle", "unknown"
    if event_count == 0:
        return "idle", None
    return "available", None


def _deny_status(by: str | None) -> str:
    return {
        "org": "denied-org",
        "plugin": "denied-plugin",
        "user": "denied-user",
        "harness": "denied-harness",
    }.get(by or "plugin", "denied-plugin")


def _join_denies(hook_events: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for ev in hook_events:
        corr = ev.get("corr_id")
        if not corr or not isinstance(corr, str):
            continue
        verdict = (ev.get("verdict") or "").lower()
        if verdict not in ("deny", "denied", "block", "blocked"):
            continue
        by = ev.get("by") or "plugin"
        out[corr] = {
            "by": by,
            "source": str(ev.get("hook") or "hook")[:64],
            "rule": str(ev.get("rule") or "deny")[:64],
        }
    return out


def reduce(
    events: list[dict],
    hook_denies: list[dict],
    capabilities: dict,
    *,
    harness: str,
) -> list[dict]:
    """Server-side reducer → node list."""
    real = [e for e in events if e.get("kind") != "stream.truncated"]
    real.sort(key=lambda e: (e.get("ts") or "", KIND_ORDER.get(e.get("kind") or "", 99)))
    deny_by_corr = _join_denies(hook_denies)
    session_ended = any(e.get("kind") == "session.end" for e in real)
    event_count = len(real)

    # turn indexing
    turn = 0
    turn_of: dict[str, int] = {}
    for e in real:
        kind = e.get("kind")
        if kind == "prompt.submit":
            turn += 1
        nid = e.get("node_id")
        if nid:
            turn_of[nid] = max(0, turn - (0 if kind == "prompt.submit" else 0))
            if kind == "prompt.submit":
                turn_of[nid] = turn - 1 if turn else 0

    nodes: dict[str, dict] = {}
    agents = sorted({str(e.get("agent_id") or "main") for e in real} or {"main"})

    # seed spine for turn 0 (and current turn if events)
    turns = {0}
    for e in real:
        if e.get("kind") == "prompt.submit":
            turns.add(turn_of.get(e.get("node_id") or "", 0))
    if not turns:
        turns = {0}

    for agent_id in agents:
        for t in sorted(turns):
            for step in STEPS:
                nid = f"step:{agent_id}:{t}:{step}"
                status, cap = seed_status(capabilities, harness, step, event_count)
                node = {
                    "node_id": nid,
                    "parent_id": None,
                    "agent_id": agent_id,
                    "turn": t,
                    "step": step,
                    "kind": "step.seed",
                    "status": status,
                    "unterminated": False,
                    "deny": None,
                    "metrics": None,
                    "ts": None,
                }
                if cap:
                    node["capability_state"] = cap
                nodes[nid] = node

    def set_status(node: dict, status: str) -> None:
        cur = node.get("status")
        if cur in TERMINAL and status not in DENY_RANK:
            # deny can still beat success
            if status not in DENY_RANK:
                return
        if cur in DENY_RANK and status in DENY_RANK:
            if DENY_RANK[status] < DENY_RANK[cur]:
                return
        elif cur in DENY_RANK and status not in DENY_RANK:
            return
        node["status"] = status

    for e in real:
        kind = e.get("kind") or ""
        agent_id = str(e.get("agent_id") or "main")
        t = turn_of.get(e.get("node_id") or "", 0)
        if kind == "prompt.submit":
            t = turn_of.get(e["node_id"], 0)
            for step in ("assemble", "call-model"):
                nid = f"step:{agent_id}:{t}:{step}"
                if nid in nodes:
                    set_status(nodes[nid], "running" if step == "assemble" else "available")
                    nodes[nid]["ts"] = e.get("ts")
            if f"step:{agent_id}:{t}:assemble" in nodes:
                set_status(nodes[f"step:{agent_id}:{t}:assemble"], "succeeded")
        elif kind == "tool.pre":
            spine = f"step:{agent_id}:{t}:execute-tools"
            if spine in nodes:
                set_status(nodes[spine], "running")
                nodes[spine]["ts"] = e.get("ts")
            nid = str(e.get("node_id") or "")
            if nid and ID_RE.fullmatch(nid):
                node = {
                    "node_id": nid,
                    "parent_id": spine,
                    "agent_id": agent_id,
                    "turn": t,
                    "step": "execute-tools",
                    "kind": kind,
                    "status": "running",
                    "unterminated": False,
                    "deny": None,
                    "metrics": e.get("metrics"),
                    "ts": e.get("ts"),
                    "tool": e.get("tool"),
                }
                nodes[nid] = node
                corr = e.get("corr_id")
                if corr and corr in deny_by_corr:
                    d = deny_by_corr[corr]
                    node["deny"] = d
                    set_status(node, _deny_status(d.get("by")))
        elif kind in ("tool.post", "tool.fail"):
            nid = str(e.get("node_id") or "")
            node = nodes.get(nid)
            if node:
                set_status(node, "failed" if kind == "tool.fail" else "succeeded")
                node["ts"] = e.get("ts")
                if e.get("metrics"):
                    node["metrics"] = e.get("metrics")
                corr = e.get("corr_id")
                if corr and corr in deny_by_corr:
                    d = deny_by_corr[corr]
                    node["deny"] = d
                    set_status(node, _deny_status(d.get("by")))
        elif kind == "permission.request":
            nid = str(e.get("node_id") or "")
            if nid in nodes:
                set_status(nodes[nid], "waiting-approval")
        elif kind == "permission.resolve":
            nid = str(e.get("node_id") or "")
            node = nodes.get(nid)
            if node:
                deny = e.get("deny")
                if deny and isinstance(deny, dict):
                    node["deny"] = {
                        "by": deny.get("by") or "user",
                        "source": str(deny.get("source") or "permission")[:64],
                        "rule": str(deny.get("rule") or "deny")[:64],
                    }
                    set_status(node, _deny_status(node["deny"]["by"]))
                else:
                    set_status(node, "running")
        elif kind == "turn.end":
            for step in ("package", "update-context"):
                nid = f"step:{agent_id}:{t}:{step}"
                if nid in nodes and nodes[nid]["status"] not in TERMINAL:
                    set_status(nodes[nid], "succeeded")
        elif kind == "session.end":
            pass
        # asserted_status only if non-terminal
        asserted = e.get("asserted_status")
        nid = str(e.get("node_id") or "")
        if asserted and nid in nodes and nodes[nid]["status"] not in TERMINAL:
            if asserted not in ("failed",) and nodes[nid].get("deny"):
                pass
            elif asserted in TERMINAL or asserted in (
                "running",
                "available",
                "idle",
                "waiting-approval",
            ):
                if nodes[nid]["status"] not in TERMINAL:
                    nodes[nid]["status"] = asserted

    if session_ended:
        for node in nodes.values():
            if node["status"] not in TERMINAL and node["status"] not in ("unavailable-harness",):
                node["unterminated"] = True

    # newest-first cap
    ordered = sorted(
        nodes.values(),
        key=lambda n: (
            n.get("turn") or 0,
            STEPS.index(n["step"]) if n.get("step") in STEPS else 99,
            n.get("ts") or "",
        ),
        reverse=True,
    )
    return ordered[:2000]


def session_summary_status(nodes: list[dict], events: list[dict]) -> str:
    statuses = [n.get("status") for n in nodes]
    if "failed" in statuses:
        return "failed"
    for d in ("denied-org", "denied-plugin", "denied-user", "denied-harness"):
        if d in statuses:
            return d
    if "waiting-approval" in statuses:
        return "waiting-approval"
    if "running" in statuses or any(n.get("unterminated") for n in nodes):
        return "running"
    if "succeeded" in statuses and any(e.get("kind") == "session.end" for e in events):
        return "succeeded"
    return "idle"


def list_sessions(
    project_root: Path | str,
    *,
    cursor: str | None = None,
    limit: int = 50,
    harness: str | None = None,
    capabilities: dict | None = None,
) -> dict:
    limit = max(1, min(int(limit), 200))
    root = runs_root(project_root)
    items: list[dict] = []
    if root.is_dir():
        for d in root.iterdir():
            if not d.is_dir() or d.is_symlink():
                continue
            if not validate_session_id(d.name):
                continue
            spectate = d / "spectate-events.jsonl"
            hook = d / "hook-events.jsonl"
            has_stream = spectate.is_file() and not spectate.is_symlink()
            has_hook = hook.is_file() and not hook.is_symlink()
            if not has_stream and not has_hook:
                continue
            synthetic = False
            harness_val = "unknown"
            latest = "idle"
            mtime = d.stat().st_mtime
            if has_stream:
                events, _meta = read_jsonl_tail(spectate)
                if events:
                    harness_val = str(events[0].get("harness") or "unknown")
                    synthetic = bool(events[0].get("synthetic"))
                    caps = capabilities or {"harnesses": {}}
                    nodes = reduce(events, [], caps, harness=harness_val)
                    latest = session_summary_status(nodes, events)
                meta_path = d / "meta.json"
                if meta_path.is_file():
                    try:
                        mj = json.loads(meta_path.read_text(encoding="utf-8"))
                        synthetic = synthetic or bool(mj.get("synthetic"))
                    except json.JSONDecodeError:
                        pass
            if harness and harness_val != harness:
                continue
            items.append(
                {
                    "session_id": d.name,
                    "harness": harness_val,
                    "synthetic": synthetic,
                    "mtime": mtime,
                    "latest_status": latest,
                    "has_stream": has_stream,
                }
            )

    # ranking: non-synthetic with stream > non-synthetic without > synthetic
    def rank(it: dict) -> tuple:
        return (
            0 if (not it["synthetic"] and it["has_stream"]) else 1 if not it["synthetic"] else 2,
            -it["mtime"],
        )

    items.sort(key=rank)
    start = 0
    if cursor:
        try:
            start = int(cursor)
        except ValueError:
            start = 0
    page = items[start : start + limit]
    next_c = str(start + limit) if start + limit < len(items) else None
    return {"sessions": page, "next_cursor": next_c}


def nodes_response(
    project_root: Path | str,
    session_id: str,
    capabilities: dict,
) -> tuple[int, dict]:
    if not validate_session_id(session_id):
        return 400, {"error": "invalid_session_id"}
    run = resolve_run_dir(project_root, session_id)
    if run is None:
        # distinguish missing dir vs present without stream
        root = runs_root(project_root)
        raw = root / session_id
        if raw.is_dir():
            hook = raw / "hook-events.jsonl"
            return 404, {
                "error": "no_spectate_stream",
                "has_hook_events": hook.is_file(),
            }
        return 404, {"error": "session_not_found"}
    spectate = resolve_fixed_file(run, "spectate-events.jsonl")
    if spectate is None:
        hook = run / "hook-events.jsonl"
        return 404, {
            "error": "no_spectate_stream",
            "has_hook_events": hook.is_file() and not hook.is_symlink(),
        }
    events, meta = read_jsonl_tail(spectate)
    hook_path = resolve_fixed_file(run, "hook-events.jsonl")
    hook_events: list[dict] = []
    hook_meta = {"mtime_ns": 0, "size": 0}
    if hook_path:
        hook_events, hook_meta = read_jsonl_tail(hook_path)
        # only keep allow-listed fields
        hook_events = [
            {k: ev.get(k) for k in ("ts", "corr_id", "verdict", "hook", "rule", "by") if k in ev}
            for ev in hook_events
        ]
    harness = "unknown"
    synthetic = False
    if events:
        harness = str(events[0].get("harness") or "unknown")
        synthetic = bool(events[0].get("synthetic"))
    if meta["truncated"] and events:
        events = [
            {
                "schema": "rc.spectate.v1",
                "ts": events[0].get("ts"),
                "session_id": session_id,
                "harness": harness,
                "source": "recorded",
                "kind": "stream.truncated",
                "node_id": "stream:truncated",
                "agent_id": "main",
                "synthetic": True,
            },
            *events,
        ]
    nodes = reduce(events, hook_events, capabilities, harness=harness)
    last_ts = None
    for e in reversed(events):
        if e.get("kind") not in ("stream.truncated", "step.seed") and e.get("ts"):
            last_ts = e["ts"]
            break
    session_ended = any(e.get("kind") == "session.end" for e in events)
    server_now = now_rfc3339()
    source_hint = (
        "demo" if synthetic else ("live" if (last_ts and not session_ended) else "recorded")
    )
    etag = f'W/"{meta["mtime_ns"]}-{meta["size"]}-{hook_meta.get("mtime_ns", 0)}-{hook_meta.get("size", 0)}"'
    body = {
        "session_id": session_id,
        "harness": harness,
        "synthetic": synthetic,
        "server_now": server_now,
        "last_event_ts": last_ts,
        "session_ended": session_ended,
        "source_hint": source_hint,
        "etag": etag,
        "nodes_truncated": len(nodes) >= 2000,
        "skipped_malformed": meta["skipped_malformed"],
        "nodes": nodes,
    }
    return 200, body


def events_response(
    project_root: Path | str,
    session_id: str,
    *,
    cursor: str | None = None,
    limit: int = 100,
) -> tuple[int, dict]:
    if not validate_session_id(session_id):
        return 400, {"error": "invalid_session_id"}
    run = resolve_run_dir(project_root, session_id)
    if run is None:
        root = runs_root(project_root)
        if (root / session_id).is_dir():
            hook = root / session_id / "hook-events.jsonl"
            return 404, {
                "error": "no_spectate_stream",
                "has_hook_events": hook.is_file(),
            }
        return 404, {"error": "session_not_found"}
    spectate = resolve_fixed_file(run, "spectate-events.jsonl")
    if spectate is None:
        return 404, {
            "error": "no_spectate_stream",
            "has_hook_events": (run / "hook-events.jsonl").is_file(),
        }
    limit = max(1, min(int(limit), 500))
    st = spectate.stat()
    size = st.st_size
    cursor_reset = False
    start = 0
    if cursor is None or cursor == "":
        start = max(0, size - TAIL_BYTES)
    else:
        try:
            start = int(cursor)
        except ValueError:
            return 400, {"error": "invalid_query"}
        if start > size:
            cursor_reset = True
            start = max(0, size - TAIL_BYTES)
        if start == 0 and size > TAIL_BYTES:
            # cursor 0 only valid when size ≤ 5 MiB
            start = size - TAIL_BYTES
            cursor_reset = True
    truncated = start > 0
    fd = _open_nofollow(spectate)
    try:
        os.lseek(fd, start, os.SEEK_SET)
        raw = os.read(fd, min(TAIL_BYTES, size - start))
    finally:
        os.close(fd)
    offset = start
    if start and raw:
        nl = raw.find(b"\n")
        if nl >= 0:
            offset = start + nl + 1
            raw = raw[nl + 1 :]
        else:
            raw = b""
            offset = start
    events: list[dict] = []
    skipped = 0
    pos = offset
    for line in raw.splitlines(keepends=True):
        pos += len(line)
        s = line.decode("utf-8", errors="replace").strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if isinstance(obj, dict):
            events.append(scrub_obj(obj))
            if len(events) >= limit:
                break
    return 200, {
        "session_id": session_id,
        "events": events,
        "next_cursor": str(pos),
        "cursor_reset": cursor_reset,
        "truncated": truncated,
        "skipped_malformed": skipped,
    }


def parse_query_int(value: str | None, default: int) -> int | None:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return None
