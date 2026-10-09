#!/usr/bin/env python3
"""spectate_store.py — pure library behind the Spectate poll API (v0.1).

No sockets and no HTTP framework. The server wrappers call the ``http_*`` helpers,
each of which returns ``(status, headers, body)``; ``body`` is a JSON-serialisable
dict (``None`` on a 304). Everything below those helpers is deterministic given the
files on disk, the capability matrix and the schema, so it is unit-testable without a
server.

What this module enforces (contract: docs/plans/2026-10-09-harness-spectate/BUILD-PLAN.md):

* Path & identity (G1-5, G2-18, G9-8, G9-9): session ids are regex-gated, run dirs and
  the three fixed filenames are opened with ``O_NOFOLLOW`` relative to a directory fd, and
  only regular files are read. A symlinked run dir or file reads as absent, never as a
  different session.
* Read path (G1-2, G1-6, G9-8): 5 MiB (5 * 1024 * 1024) tail window, absolute byte-offset
  cursors, partial trailing lines never consumed, malformed lines counted and skipped.
  Every line is parsed against the allow-list schema (the same JSON file the gate checks),
  rejected on any sensitive key at any depth, then value-scrubbed.
* Reducer (G1-3, G2-7, G2-8, G3-2, G5-7, G7-3): ``reduce`` / ``reduce_session`` turn
  events + hook denies + the capability matrix into nodes. Silence is never read as
  unavailable; an ``unknown`` capability never becomes ``unavailable-harness``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat as stat_mod
import tempfile
import urllib.parse
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent / "knowledge" / "spectate-event-schema-v1.json"
CAPABILITIES_PATH = HERE.parent / "knowledge" / "spectate-capabilities.json"

TAIL_BYTES = 5 * 1024 * 1024
MAX_LINE_BYTES = 64 * 1024
MAX_META_BYTES = 64 * 1024
MAX_NODES = 2000
LIVE_WINDOW_SECONDS = 60

SPECTATE_FILE = "spectate-events.jsonl"
HOOK_FILE = "hook-events.jsonl"
META_FILE = "meta.json"

SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,64}$")
UINT_RE = re.compile(r"^[0-9]{1,15}$")

HARNESSES = (
    "claude-code",
    "codex-cli",
    "copilot-cli",
    "copilot-vscode",
    "cursor",
    "gemini-cli",
    "grok-build",
    "grok-bot",
)
HARNESS_ENUM = (*HARNESSES, "unknown")

STEPS = ("assemble", "call-model", "classify", "execute-tools", "package", "update-context")
STEP_CAP = {
    "assemble": "session",
    "call-model": "prompt",
    "classify": "prompt",
    "execute-tools": "tool_pre",
    "package": "tool_post",
    "update-context": "compact",
}
CAPABILITY_STATES = ("supported", "partial", "unsupported", "unknown")

DENY_STATUS = {
    "org": "denied-org",
    "plugin": "denied-plugin",
    "user": "denied-user",
    "harness": "denied-harness",
}
DENY_RANK = {"org": 4, "plugin": 3, "user": 2, "harness": 1}
STATUS_RANK = {
    "denied-org": 100,
    "denied-plugin": 90,
    "denied-user": 80,
    "denied-harness": 70,
    "failed": 60,
    "succeeded": 50,
    "waiting-approval": 40,
    "running": 30,
    "available": 20,
    "idle": 10,
    "unavailable-harness": 0,
}
# Rank used to roll a step's tool children up into the step node: in-flight work outranks
# `succeeded` so a step with a tool still waiting on approval never reads as done.
AGG_RANK = {**STATUS_RANK, "waiting-approval": 55, "running": 54}
OPEN_STATUSES = frozenset({"running", "waiting-approval"})

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
    "step.seed": 4,
    "session.end": 5,
    "stream.truncated": 6,
    "emitter.truncated": 7,
}
ANNOTATION_KINDS = frozenset({"stream.truncated", "emitter.truncated", "step.seed"})
NODE_KINDS = frozenset(
    {
        "tool.pre",
        "tool.post",
        "tool.fail",
        "permission.request",
        "permission.resolve",
        "subagent.start",
        "subagent.stop",
    }
)

HOOK_DENY_VERDICTS = frozenset({"deny", "denied", "block", "blocked"})

# Mirror of plugins/ravenclaude-core/hooks/_scrub.sh `_secret_patterns` (ERE → Python re).
# Keep the three copies in sync (hook, thing-seat.sh, this).
SECRET_PATTERNS = tuple(
    re.compile(p)
    for p in (
        r"AKIA[0-9A-Z]{12,}",
        r"sk-(ant-)?[A-Za-z0-9-]{20,}",
        r"sk_live_[A-Za-z0-9]{24,}",
        r"rk_live_[A-Za-z0-9]{24,}",
        r"ghp_[A-Za-z0-9]{30,}",
        r"github_pat_[A-Za-z0-9_]{20,}",
        r"glpat-[A-Za-z0-9_-]{15,}",
        r"xox[baprs]-[A-Za-z0-9-]{10,}",
        r"AIza[0-9A-Za-z_-]{30,}",
        r"npm_[A-Za-z0-9]{30,}",
        r"hf_[A-Za-z0-9]{30,}",
        r"AccountKey=[A-Za-z0-9+/=]{20,}",
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"--password[=\s]\S+",
        r"--token[=\s]\S+",
        r"(^|\s)-p[^\s0-9]\S{15,}",
        r"(https?|postgres(ql)?|mysql|mongodb|redis|amqp|smtp)s?://"
        r"[A-Za-z0-9._-]{2,}:[A-Za-z0-9._%+-]{4,}@",
    )
)

# Fields whose value may be dropped (rather than the whole event rejected) when it looks
# like a secret: they are optional and carry no identity.
_DROPPABLE_PATHS = (("tool", "target"), ("deny", "source"), ("deny", "rule"))

_SCHEMA_CACHE: dict[str, Any] = {}
_REDUCE_CACHE: dict[tuple, dict] = {}
_REDUCE_CACHE_MAX = 256


# --------------------------------------------------------------------------------------
# Schema interpreter — the subset of JSON Schema the Spectate schema uses.
# --------------------------------------------------------------------------------------


def load_schema(path: Path | None = None) -> dict:
    p = Path(path) if path else SCHEMA_PATH
    key = str(p)
    if key not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[key] = json.loads(p.read_text(encoding="utf-8"))
    return _SCHEMA_CACHE[key]


def sensitive_keys(schema: dict | None = None) -> frozenset[str]:
    return frozenset((schema or load_schema()).get("x-sensitive-keys", ()))


def _ecma_pattern(pat: str) -> re.Pattern:
    # ECMA `$` matches only at the very end; Python's also matches before a final "\n",
    # which would let "abc\n" pass an id charset. \Z is the exact translation.
    if pat.endswith("$") and not pat.endswith("\\$"):
        pat = pat[:-1] + r"\Z"
    return re.compile(pat)


_PATTERN_CACHE: dict[str, re.Pattern] = {}


def _pattern(pat: str) -> re.Pattern:
    c = _PATTERN_CACHE.get(pat)
    if c is None:
        c = _PATTERN_CACHE[pat] = _ecma_pattern(pat)
    return c


def _type_ok(inst: Any, t: str) -> bool:
    if t == "object":
        return isinstance(inst, dict)
    if t == "array":
        return isinstance(inst, list)
    if t == "string":
        return isinstance(inst, str)
    if t == "boolean":
        return isinstance(inst, bool)
    if t == "null":
        return inst is None
    if t == "number":
        return isinstance(inst, (int, float)) and not isinstance(inst, bool)
    if t == "integer":
        return isinstance(inst, int) and not isinstance(inst, bool)
    return False


def _resolve_ref(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported $ref {ref!r}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _walk_schema(node: dict, inst: Any, path: str, errs: list[str], root: dict) -> None:
    if "$ref" in node:
        _walk_schema(_resolve_ref(root, node["$ref"]), inst, path, errs, root)
    where = path or "/"
    if "const" in node and (inst != node["const"] or type(inst) is not type(node["const"])):
        errs.append(f"{where}: must equal {node['const']!r}")
    if "enum" in node and not any(inst == v and type(inst) is type(v) for v in node["enum"]):
        errs.append(f"{where}: not one of the allowed values")
    if "type" in node:
        types = node["type"] if isinstance(node["type"], list) else [node["type"]]
        if not any(_type_ok(inst, t) for t in types):
            errs.append(f"{where}: wrong type (want {'|'.join(types)})")
            return
    if isinstance(inst, str):
        if "maxLength" in node and len(inst) > node["maxLength"]:
            errs.append(f"{where}: longer than {node['maxLength']}")
        if "minLength" in node and len(inst) < node["minLength"]:
            errs.append(f"{where}: shorter than {node['minLength']}")
        if "pattern" in node and not _pattern(node["pattern"]).search(inst):
            errs.append(f"{where}: does not match pattern {node['pattern']}")
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if isinstance(inst, float) and not math.isfinite(inst):
            errs.append(f"{where}: not a finite number")
        else:
            if "minimum" in node and inst < node["minimum"]:
                errs.append(f"{where}: below minimum {node['minimum']}")
            if "maximum" in node and inst > node["maximum"]:
                errs.append(f"{where}: above maximum {node['maximum']}")
    if isinstance(inst, dict):
        for req in node.get("required", ()):
            if req not in inst:
                errs.append(f"{where}: missing required property {req}")
        props = node.get("properties", {})
        for key, val in inst.items():
            sub = f"{path}/{key}"
            if key in props:
                _walk_schema(props[key], val, sub, errs, root)
            elif node.get("additionalProperties") is False:
                errs.append(f"{sub}: additional property not allowed ({key})")
    for sub_schema in node.get("allOf", ()):
        _walk_schema(sub_schema, inst, path, errs, root)
    if "if" in node:
        probe: list[str] = []
        _walk_schema(node["if"], inst, path, probe, root)
        if not probe:
            if "then" in node:
                _walk_schema(node["then"], inst, path, errs, root)
        elif "else" in node:
            _walk_schema(node["else"], inst, path, errs, root)
    if "not" in node:
        probe = []
        _walk_schema(node["not"], inst, path, probe, root)
        if not probe:
            errs.append(f"{where}: matches a forbidden shape")


def validate_schema(obj: Any, schema: dict | None = None) -> list[str]:
    sch = schema or load_schema()
    errs: list[str] = []
    _walk_schema(sch, obj, "", errs, sch)
    return errs


# --------------------------------------------------------------------------------------
# Scrubbing
# --------------------------------------------------------------------------------------


def secret_hit(value: str) -> bool:
    return any(p.search(value) for p in SECRET_PATTERNS)


def iter_strings(obj: Any):
    """Yield ``(path_tuple, value)`` for every string in a JSON value (iterative)."""
    stack: list[tuple[tuple, Any]] = [((), obj)]
    while stack:
        path, cur = stack.pop()
        if isinstance(cur, str):
            yield path, cur
        elif isinstance(cur, dict):
            for k, v in cur.items():
                stack.append(((*path, k), v))
        elif isinstance(cur, list):
            for i, v in enumerate(cur):
                stack.append(((*path, i), v))


def find_sensitive_keys(obj: Any, keys: frozenset[str] | None = None) -> list[str]:
    """Dotted paths of every dict key (at any depth) that is a forbidden payload key."""
    bad = keys if keys is not None else sensitive_keys()
    hits: list[str] = []
    stack: list[tuple[tuple, Any]] = [((), obj)]
    while stack:
        path, cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                p = (*path, k)
                if isinstance(k, str) and k.lower() in bad:
                    hits.append(".".join(str(x) for x in p))
                stack.append((p, v))
        elif isinstance(cur, list):
            for i, v in enumerate(cur):
                stack.append(((*path, i), v))
    return sorted(hits)


def check_event(obj: Any) -> list[str]:
    """Every reason ``obj`` is not an acceptable Spectate event (empty list = acceptable).

    Reasons are tagged ``schema:``, ``sensitive-key:``, ``secret:`` or ``encoding:`` so a
    gate can assert *why* a bad fixture was rejected, not merely that it was.
    """
    errs: list[str] = []
    if not isinstance(obj, dict):
        return ["schema: / : event must be an object"]
    errs.extend(f"sensitive-key: {p}" for p in find_sensitive_keys(obj))
    errs.extend(f"schema: {e}" for e in validate_schema(obj))
    for path, s in iter_strings(obj):
        where = ".".join(str(x) for x in path)
        try:
            s.encode("utf-8")
        except UnicodeEncodeError:
            errs.append(f"encoding: {where}: lone surrogate")
            continue
        if secret_hit(s):
            errs.append(f"secret: {where}")
    return errs


def scrub_event(obj: dict) -> dict | None:
    """Value-scrub a schema-valid event. Secret-shaped optional values are dropped; a
    secret-shaped value anywhere else rejects the event (returns None)."""
    out = json.loads(json.dumps(obj))
    for path, s in iter_strings(out):
        if not secret_hit(s):
            continue
        if tuple(path) in _DROPPABLE_PATHS:
            del out[path[0]][path[1]]
        else:
            return None
    return out


def _reject_constant(name: str) -> Any:
    raise ValueError(f"non-finite JSON constant {name}")


def parse_event_line(line: bytes, session_id: str) -> tuple[dict | None, str | None]:
    """Allow-list parse of one JSONL line → ``(event, None)`` or ``(None, reason)``."""
    if len(line) > MAX_LINE_BYTES:
        return None, "line-too-long"
    try:
        text = line.decode("utf-8")
    except UnicodeDecodeError:
        return None, "encoding"
    try:
        obj = json.loads(text, parse_constant=_reject_constant)
    except (ValueError, RecursionError):
        return None, "json"
    if not isinstance(obj, dict):
        return None, "shape"
    if find_sensitive_keys(obj):
        return None, "sensitive-key"
    if validate_schema(obj):
        return None, "schema"
    for _path, s in iter_strings(obj):
        try:
            s.encode("utf-8")
        except UnicodeEncodeError:
            return None, "encoding"
    clean = scrub_event(obj)
    if clean is None:
        return None, "secret"
    if clean.get("session_id") != session_id:
        return None, "session-mismatch"
    return clean, None


def sanitize_token(value: Any, default: str | None = None) -> str | None:
    """Reduce a free string to the short-token charset (G5-9), or ``default``."""
    if not isinstance(value, str) or secret_hit(value):
        return default
    cleaned = re.sub(r"[^A-Za-z0-9._:/-]", "", value)[:64]
    return cleaned or default


def parse_hook_line(line: bytes) -> tuple[dict | None, str | None]:
    """Hook-event line → ``{ts, corr_id, verdict, hook, rule}`` (never ``path``).

    Valid JSON without a usable ``corr_id`` yields ``(None, None)``: nothing to join on,
    and not malformed (every pre-v0.2 hook line looks like that)."""
    if len(line) > MAX_LINE_BYTES:
        return None, "line-too-long"
    try:
        obj = json.loads(line.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, ValueError, RecursionError):
        return None, "json"
    if not isinstance(obj, dict):
        return None, "shape"
    corr = obj.get("corr_id")
    if not isinstance(corr, str) or not ID_RE.fullmatch(corr):
        return None, None
    verdict = sanitize_token(obj.get("verdict"))
    if verdict is None:
        return None, None
    ts = obj.get("ts")
    return {
        "ts": ts if isinstance(ts, str) and len(ts) <= 40 else None,
        "corr_id": corr,
        "verdict": verdict.lower(),
        "hook": sanitize_token(obj.get("hook"), "hook"),
        "rule": sanitize_token(obj.get("rule")),
    }, None


def deny_by_for_hook(hook: str | None) -> str:
    """Map a hook name to ``deny.by`` (G5-9). Marketplace hook denies default to plugin."""
    h = (hook or "").lower()
    if h.startswith(("org", "managed", "policy")):
        return "org"
    if h.startswith(("permission", "user")):
        return "user"
    if h.startswith(("harness", "native")):
        return "harness"
    return "plugin"


# --------------------------------------------------------------------------------------
# Identity & path resolution
# --------------------------------------------------------------------------------------


def validate_session_id(session_id: Any) -> bool:
    """Regex gate (G1-5). Rejects '', '.', '..', separators, encoded separators, NUL."""
    if not isinstance(session_id, str) or not SESSION_RE.fullmatch(session_id):
        return False
    return session_id not in (".", "..")


def runs_root(project_root: Path | str) -> Path:
    return Path(project_root).resolve() / ".ravenclaude" / "runs"


_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_DIR_FD = os.open in os.supports_dir_fd


class _Run:
    """A run directory held open by fd so the three fixed names resolve inside it."""

    def __init__(self, dfd: int, path: Path):
        self.dfd = dfd
        self.path = path

    def open_file(self, name: str) -> int | None:
        """Open one of the fixed filenames: no symlink follow, regular files only."""
        assert name in (SPECTATE_FILE, HOOK_FILE, META_FILE), name
        flags = os.O_RDONLY | _O_CLOEXEC | _O_NOFOLLOW | _O_NONBLOCK
        try:
            if _DIR_FD:
                fd = os.open(name, flags, dir_fd=self.dfd)
            else:
                full = self.path / name
                if stat_mod.S_ISLNK(os.lstat(full).st_mode):
                    return None
                fd = os.open(str(full), flags)
        except OSError:
            return None
        try:
            if not stat_mod.S_ISREG(os.fstat(fd).st_mode):
                os.close(fd)
                return None
        except OSError:
            os.close(fd)
            return None
        return fd

    def close(self) -> None:
        try:
            os.close(self.dfd)
        except OSError:
            pass


def open_run(project_root: Path | str, session_id: str) -> tuple[str, _Run | None]:
    """→ ``("invalid"|"missing"|"ok", run)``. A symlinked run dir is ``missing``."""
    if not validate_session_id(session_id):
        return "invalid", None
    root = runs_root(project_root).resolve()
    flags = os.O_RDONLY | _O_CLOEXEC | _O_DIRECTORY
    try:
        rfd = os.open(str(root), flags)
    except OSError:
        return "missing", None
    try:
        sub_flags = flags | _O_NOFOLLOW
        try:
            if _DIR_FD:
                dfd = os.open(session_id, sub_flags, dir_fd=rfd)
            else:
                cand = root / session_id
                if stat_mod.S_ISLNK(os.lstat(cand).st_mode):
                    return "missing", None
                dfd = os.open(str(cand), sub_flags)
        except OSError:
            return "missing", None
    finally:
        os.close(rfd)
    return "ok", _Run(dfd, root / session_id)


# --------------------------------------------------------------------------------------
# Capability matrix
# --------------------------------------------------------------------------------------


def load_capabilities(path: Path | str | None = None) -> dict:
    return json.loads(Path(path or CAPABILITIES_PATH).read_text(encoding="utf-8"))


def capabilities_mtime_ns(path: Path | str | None = None) -> int:
    try:
        return Path(path or CAPABILITIES_PATH).stat().st_mtime_ns
    except OSError:
        return 0


def cap_state(capabilities: dict, harness: str, key: str) -> str:
    cell = (capabilities.get("harnesses", {}).get(harness) or {}).get(key) or {}
    state = cell.get("state", "unknown")
    return state if state in CAPABILITY_STATES else "unknown"


def capability_states(
    capabilities: dict, harness: str, overrides: Mapping[str, str] | None = None
) -> dict[str, str]:
    """Flat ``key → state`` for one harness. ``overrides`` (synthetic demo sessions only)
    replace individual cells; unknown keys / states are ignored."""
    keys = capabilities.get("keys") or list(STEP_CAP.values())
    out = {k: cap_state(capabilities, harness, k) for k in keys}
    for k, v in (overrides or {}).items():
        if k in out and v in CAPABILITY_STATES:
            out[k] = v
    return out


# --------------------------------------------------------------------------------------
# Reducer
# --------------------------------------------------------------------------------------


def seed_status(caps: Mapping[str, str], step: str, event_count: int) -> tuple[str, str | None]:
    """Seed precedence (G3-2). → ``(status, capability_state|None)``."""
    state = caps.get(STEP_CAP[step], "unknown")
    if state == "unsupported":
        return "unavailable-harness", None
    if state == "unknown":
        return "idle", "unknown"
    if event_count == 0:
        return "idle", None
    return "available", None


def _deny_obj(raw: Any) -> dict | None:
    if not isinstance(raw, dict):
        return None
    by = raw.get("by") if raw.get("by") in DENY_STATUS else "user"
    out: dict[str, str] = {"by": by}
    for k in ("source", "rule"):
        if isinstance(raw.get(k), str) and raw[k]:
            out[k] = raw[k]
    return out


def _better_deny(a: dict | None, b: dict | None) -> dict | None:
    if a is None:
        return b
    if b is None:
        return a
    return b if DENY_RANK[b["by"]] > DENY_RANK[a["by"]] else a


class _Node:
    __slots__ = (
        "agent",
        "node_id",
        "turn",
        "kind",
        "step",
        "parent_raw",
        "soft",
        "terminal",
        "deny",
        "corr",
        "metrics",
        "tool",
        "ts",
        "seq",
    )

    def __init__(self, agent: str, node_id: str, turn: int, kind: str, step: str, seq: int):
        self.agent = agent
        self.node_id = node_id
        self.turn = turn
        self.kind = kind
        self.step = step
        self.parent_raw: str | None = None
        self.soft: str | None = None
        self.terminal: str | None = None
        self.deny: dict | None = None
        self.corr: set[str] = set()
        self.metrics: dict[str, float] = {}
        self.tool: dict | None = None
        self.ts: str | None = None
        self.seq = seq

    def status(self) -> str:
        if self.deny:
            return DENY_STATUS[self.deny["by"]]
        return self.terminal or self.soft or "idle"


def _step_id(agent: str, turn: int, step: str) -> str:
    return f"step:{agent}:{turn}:{step}"


def _apply_terminal(node: _Node, status: str) -> None:
    if node.terminal is None or STATUS_RANK[status] > STATUS_RANK[node.terminal]:
        node.terminal = status


def _join_hook_denies(hook_denies: list[dict]) -> dict[str, dict]:
    joined: dict[str, dict] = {}
    for h in hook_denies:
        corr = h.get("corr_id")
        if not isinstance(corr, str) or str(h.get("verdict") or "").lower() not in (
            HOOK_DENY_VERDICTS
        ):
            continue
        deny: dict[str, str] = {"by": deny_by_for_hook(h.get("hook")), "source": "hook"}
        hook = sanitize_token(h.get("hook"))
        if hook:
            deny["source"] = hook
        rule = sanitize_token(h.get("rule"))
        if rule:
            deny["rule"] = rule
        joined[corr] = _better_deny(joined.get(corr), deny)  # type: ignore[assignment]
    return joined


def session_summary_status(nodes: list[dict], session_ended: bool) -> str:
    """Session-summary reducer (G4-3) → ``latest_status``."""
    statuses = {n["status"] for n in nodes}
    if "failed" in statuses:
        return "failed"
    for deny_status in ("denied-org", "denied-plugin", "denied-user", "denied-harness"):
        if deny_status in statuses:
            return deny_status
    if "waiting-approval" in statuses:
        return "waiting-approval"
    if "running" in statuses or any(n["unterminated"] for n in nodes):
        return "running"
    if "succeeded" in statuses and session_ended:
        return "succeeded"
    return "idle"


def reduce_session(
    events: list[dict],
    hook_denies: list[dict],
    capabilities: dict,
    *,
    harness: str,
    overrides: Mapping[str, str] | None = None,
) -> dict:
    """Server-side reducer. → ``{nodes, nodes_truncated, session_ended, event_count,
    last_event_ts, latest_status}``. ``nodes`` follow the G5-8 shape plus ``tool`` and an
    optional ``parent_truncated``."""
    caps = capability_states(capabilities, harness, overrides)
    session_ended = any(e.get("kind") == "session.end" for e in events)
    evs = [e for e in events if e.get("kind") not in ANNOTATION_KINDS]
    count = len(evs)
    order = sorted(
        range(count),
        key=lambda i: (evs[i].get("ts") or "", KIND_ORDER.get(evs[i].get("kind") or "", 99), i),
    )

    agents: dict[str, dict] = {"main": {"turn": 0, "prompted": False}}
    closed: set[tuple[str, int]] = set()
    nodes: dict[tuple[str, str], _Node] = {}
    step_obs: dict[tuple[str, int, str], dict] = {}
    compact_open: set[tuple[str, int]] = set()
    last_ts: str | None = None

    def observe(agent: str, turn: int, step: str, status: str, ts: str | None, **extra) -> None:
        cur = step_obs.get((agent, turn, step))
        if cur is None or STATUS_RANK[status] >= STATUS_RANK[cur["status"]]:
            step_obs[(agent, turn, step)] = {"status": status, "ts": ts, **extra}

    for seq, i in enumerate(order):
        e = evs[i]
        kind = e["kind"]
        ts = e.get("ts")
        if kind != "session.end" and ts:
            last_ts = ts
        agent = e.get("agent_id") or "main"
        st = agents.setdefault(agent, {"turn": 0, "prompted": False})
        turn = st["turn"]

        if kind == "prompt.submit":
            if st["prompted"]:
                closed.add((agent, turn))
                st["turn"] = turn = turn + 1
            st["prompted"] = True
            extra = {}
            chars = (e.get("metrics") or {}).get("prompt_chars")
            if chars is not None:
                extra["metrics"] = {"prompt_chars": chars}
            observe(agent, turn, "assemble", "succeeded", ts, **extra)
            continue
        if kind == "turn.end":
            closed.add((agent, turn))
            observe(agent, turn, "package", "succeeded", ts)
            if (agent, turn) in compact_open:
                compact_open.discard((agent, turn))
                observe(agent, turn, "update-context", "succeeded", ts)
            continue
        if kind == "compact.pre":
            compact_open.add((agent, turn))
            observe(agent, turn, "update-context", "running", ts)
            continue
        if kind not in NODE_KINDS:
            continue

        nid = e["node_id"]
        node = nodes.get((agent, nid))
        if node is None:
            node = nodes[(agent, nid)] = _Node(agent, nid, turn, kind, "execute-tools", seq)
        node.seq = seq
        node.ts = ts
        if e.get("parent_id") and node.parent_raw is None:
            node.parent_raw = e["parent_id"]
        if e.get("corr_id"):
            node.corr.add(e["corr_id"])
        if e.get("tool") and node.tool is None:
            node.tool = {k: v for k, v in e["tool"].items() if k in ("name", "family", "target")}
        for mk, mv in (e.get("metrics") or {}).items():
            node.metrics[mk] = mv

        if kind in ("tool.pre", "subagent.start"):
            node.soft = "running"
        elif kind == "permission.request":
            node.soft = "waiting-approval"
        elif kind == "permission.resolve":
            if node.soft in (None, "waiting-approval"):
                node.soft = "running"
        elif kind in ("tool.post", "subagent.stop"):
            _apply_terminal(node, "succeeded")
        elif kind == "tool.fail":
            _apply_terminal(node, "failed")

        node.deny = _better_deny(node.deny, _deny_obj(e.get("deny")))
        asserted = e.get("asserted_status")
        if asserted and node.terminal is None and node.deny is None:
            node.soft = asserted

    joined = _join_hook_denies(hook_denies)
    for node in nodes.values():
        for corr in node.corr:
            if corr in joined:
                node.deny = _better_deny(node.deny, joined[corr])

    if session_ended:
        for agent, st in agents.items():
            closed.update((agent, t) for t in range(st["turn"] + 1))

    known_step_ids = {
        _step_id(a, t, s) for a, st in agents.items() for t in range(st["turn"] + 1) for s in STEPS
    }
    agent_order = ["main", *sorted(a for a in agents if a != "main")]

    out: list[dict] = []
    recency: dict[str, tuple[int, int]] = {}

    def finish(rec: dict, agent: str, turn: int, recent: int) -> None:
        if rec["status"] in OPEN_STATUSES and (agent, turn) in closed:
            rec["unterminated"] = True
        recency[rec["node_id"]] = (turn, recent)
        out.append(rec)

    for agent in agent_order:
        for turn in range(agents[agent]["turn"] + 1):
            children = [n for n in nodes.values() if n.agent == agent and n.turn == turn]
            for step in STEPS:
                rec: dict[str, Any] = {
                    "node_id": _step_id(agent, turn, step),
                    "parent_id": None,
                    "agent_id": agent,
                    "turn": turn,
                    "step": step,
                    "kind": "step.seed",
                    "status": "idle",
                    "unterminated": False,
                    "deny": None,
                    "metrics": {},
                    "ts": None,
                    "tool": None,
                }
                recent = -1
                if step == "execute-tools" and children:
                    best = max(children, key=lambda n: AGG_RANK[n.status()])
                    rec["status"] = best.status()
                    rec["deny"] = best.deny if best.deny else None
                    rec["ts"] = max((n.ts or "" for n in children), default=None) or None
                    recent = max(n.seq for n in children)
                elif (agent, turn, step) in step_obs:
                    ob = step_obs[(agent, turn, step)]
                    rec["status"] = ob["status"]
                    rec["ts"] = ob["ts"]
                    rec["metrics"] = dict(ob.get("metrics") or {})
                else:
                    rec["status"], cap = seed_status(caps, step, count)
                    if cap:
                        rec["capability_state"] = cap
                finish(rec, agent, turn, recent)
            for n in sorted(children, key=lambda x: x.seq):
                step_node = _step_id(agent, turn, n.step)
                rec = {
                    "node_id": n.node_id,
                    "parent_id": n.parent_raw or step_node,
                    "agent_id": agent,
                    "turn": turn,
                    "step": n.step,
                    "kind": n.kind,
                    "status": n.status(),
                    "unterminated": False,
                    "deny": n.deny,
                    "metrics": dict(n.metrics),
                    "ts": n.ts,
                    "tool": n.tool,
                }
                if n.parent_raw and (
                    n.parent_raw not in known_step_ids and (agent, n.parent_raw) not in nodes
                ):
                    rec["parent_truncated"] = True
                finish(rec, agent, turn, n.seq)

    truncated = len(out) > MAX_NODES
    if truncated:
        keep = {
            r["node_id"]
            for r in sorted(out, key=lambda r: recency[r["node_id"]], reverse=True)[:MAX_NODES]
        }
        out = [r for r in out if r["node_id"] in keep]
        present = {r["node_id"] for r in out}
        for r in out:
            if r.get("parent_id") and r["parent_id"] not in present:
                r["parent_truncated"] = True

    return {
        "nodes": out,
        "nodes_truncated": truncated,
        "session_ended": session_ended,
        "event_count": count,
        "last_event_ts": last_ts,
        "latest_status": session_summary_status(out, session_ended) if count else "idle",
    }


def reduce(
    events: list[dict],
    hook_denies: list[dict],
    capabilities: dict,
    *,
    harness: str,
    overrides: Mapping[str, str] | None = None,
) -> list[dict]:
    """``reduce(events, hook_denies, capabilities) → nodes`` (BUILD-PLAN § Reducer)."""
    return reduce_session(events, hook_denies, capabilities, harness=harness, overrides=overrides)[
        "nodes"
    ]


# --------------------------------------------------------------------------------------
# File windows
# --------------------------------------------------------------------------------------


def _pread_all(fd: int, offset: int, length: int) -> bytes:
    chunks: list[bytes] = []
    while length > 0:
        buf = os.pread(fd, min(length, 1 << 20), offset)
        if not buf:
            break
        chunks.append(buf)
        offset += len(buf)
        length -= len(buf)
    return b"".join(chunks)


def _window(size: int, cursor: int | None) -> tuple[int, bool, bool]:
    """→ ``(start, cursor_reset, truncated)`` for a file snapshot of ``size`` bytes.

    First view starts at the tail start. A cursor beyond the snapshot, or older than the
    tail window, resets to the tail start (never byte 0 of an oversize file)."""
    tail = max(0, size - TAIL_BYTES)
    truncated = tail > 0
    if cursor is None:
        return tail, False, truncated
    if cursor > size or cursor < tail:
        return tail, True, truncated
    return cursor, False, truncated


def _complete_lines(fd: int, start: int, size: int) -> tuple[list[tuple[bytes, int]], int]:
    """Complete ``\\n``-terminated lines in ``[start, size)`` → ``([(line, end_offset)],
    first_offset)``. A window that begins mid-line skips to the first line boundary."""
    if start >= size:
        return [], start
    lead = 1 if start > 0 else 0
    raw = _pread_all(fd, start - lead, size - start + lead)
    pos = start
    if lead:
        if raw[:1] != b"\n":
            nl = raw.find(b"\n", 1)
            if nl < 0:
                return [], start
            pos = start - 1 + nl + 1
            raw = raw[nl + 1 :]
        else:
            raw = raw[1:]
    lines: list[tuple[bytes, int]] = []
    first = pos
    at = 0
    while True:
        nl = raw.find(b"\n", at)
        if nl < 0:
            break
        lines.append((raw[at:nl], pos + (nl + 1 - at)))
        pos += nl + 1 - at
        at = nl + 1
    return lines, first


def _fstat(fd: int | None) -> tuple[int, int]:
    if fd is None:
        return 0, 0
    st = os.fstat(fd)
    return st.st_mtime_ns, st.st_size


def _read_json_file(fd: int | None) -> dict | None:
    if fd is None:
        return None
    _m, size = _fstat(fd)
    if size > MAX_META_BYTES:
        return None
    try:
        data = json.loads(_pread_all(fd, 0, size).decode("utf-8"))
    except (UnicodeDecodeError, ValueError, RecursionError):
        return None
    return data if isinstance(data, dict) else None


class _Snapshot:
    """The three fixed files of one run, opened once and stat'd once so the etag, the
    window and the reduce all describe the same bytes."""

    def __init__(self, run: _Run):
        self.run = run
        self.sfd = run.open_file(SPECTATE_FILE)
        self.hfd = run.open_file(HOOK_FILE)
        self.mfd = run.open_file(META_FILE)
        self.s_stat = _fstat(self.sfd)
        self.h_stat = _fstat(self.hfd)
        self.m_stat = _fstat(self.mfd)

    @property
    def has_stream(self) -> bool:
        return self.sfd is not None

    def fingerprint(self, caps_mtime_ns: int) -> tuple:
        return (*self.s_stat, *self.h_stat, *self.m_stat, caps_mtime_ns)

    def close(self) -> None:
        for fd in (self.sfd, self.hfd, self.mfd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        self.run.close()


def _etag(fp: tuple) -> str:
    return 'W/"' + hashlib.sha256(repr(fp).encode()).hexdigest()[:20] + '"'


def _etag_tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    return {t.strip() for t in value.split(",") if t.strip()}


def _overrides_from_meta(meta: dict | None) -> dict[str, str]:
    """Capability overrides are honoured only for sessions stamped ``synthetic: true`` — a
    real session can never have its matrix rewritten from a file it controls."""
    if not meta or meta.get("synthetic") is not True:
        return {}
    raw = meta.get("capability_overrides")
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if isinstance(k, str) and v in CAPABILITY_STATES}


def _read_stream(
    snap: _Snapshot, session_id: str, *, cursor: int | None, limit: int | None
) -> dict:
    """Read the spectate window. ``limit`` caps *valid events returned* (None = all)."""
    assert snap.sfd is not None
    size = snap.s_stat[1]
    start, reset, truncated = _window(size, cursor)
    lines, first = _complete_lines(snap.sfd, start, size)
    lock = _stream_harness(snap, session_id, size)
    events: list[dict] = []
    skipped = 0
    next_cursor = first
    for raw, end in lines:
        next_cursor = end
        line = raw.strip(b" \t\r")
        if not line:
            continue
        ev, why = parse_event_line(line, session_id)
        if ev is None or (lock is not None and ev["harness"] != lock):
            skipped += 1
            continue
        events.append(ev)
        if limit is not None and len(events) >= limit:
            break
    return {
        "events": events,
        "skipped_malformed": skipped,
        "next_cursor": next_cursor,
        "cursor_reset": reset,
        "truncated": truncated,
        "window_start": start,
        "harness": lock,
    }


def _stream_harness(snap: _Snapshot, session_id: str, size: int) -> str | None:
    """The one harness of this stream: that of the first valid event in the tail window."""
    assert snap.sfd is not None
    start = max(0, size - TAIL_BYTES)
    probe_end = min(size, start + 256 * 1024)
    lines, _first = _complete_lines(snap.sfd, start, probe_end)
    for raw, _end in lines:
        ev, _why = parse_event_line(raw.strip(b" \t\r"), session_id)
        if ev is not None:
            return ev["harness"]
    return None


def _read_hook_denies(snap: _Snapshot) -> tuple[list[dict], int]:
    if snap.hfd is None:
        return [], 0
    size = snap.h_stat[1]
    start, _reset, _trunc = _window(size, None)
    lines, _first = _complete_lines(snap.hfd, start, size)
    out: list[dict] = []
    skipped = 0
    for raw, _end in lines:
        line = raw.strip(b" \t\r")
        if not line:
            continue
        rec, why = parse_hook_line(line)
        if rec is not None:
            out.append(rec)
        elif why is not None:
            skipped += 1
    return out, skipped


def _truncation_marker(session_id: str, harness: str, first_ts: str | None, skipped: int) -> dict:
    return {
        "schema": "rc.spectate.v1",
        "ts": first_ts or now_rfc3339(),
        "session_id": session_id,
        "harness": harness,
        "source": "recorded",
        "kind": "stream.truncated",
        "metrics": {"out_bytes": skipped},
        "synthetic": True,
    }


# --------------------------------------------------------------------------------------
# Session loading (cached by stat fingerprint)
# --------------------------------------------------------------------------------------


def now_rfc3339(now: datetime | None = None) -> str:
    n = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%S.") + f"{n.microsecond // 1000:03d}Z"


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _load_reduced(snap: _Snapshot, session_id: str, capabilities: dict, caps_mtime: int) -> dict:
    key = (str(snap.run.path), snap.fingerprint(caps_mtime))
    hit = _REDUCE_CACHE.get(key)
    if hit is not None:
        return hit
    stream = _read_stream(snap, session_id, cursor=None, limit=None)
    denies, hook_skipped = _read_hook_denies(snap)
    meta = _read_json_file(snap.mfd)
    harness = stream["harness"] or "unknown"
    events = stream["events"]
    synthetic = bool(meta and meta.get("synthetic") is True) or bool(
        events and events[0].get("synthetic") is True
    )
    result = reduce_session(
        events, denies, capabilities, harness=harness, overrides=_overrides_from_meta(meta)
    )
    result.update(
        harness=harness,
        synthetic=synthetic,
        skipped_malformed=stream["skipped_malformed"] + hook_skipped,
    )
    if len(_REDUCE_CACHE) >= _REDUCE_CACHE_MAX:
        _REDUCE_CACHE.clear()
    _REDUCE_CACHE[key] = result
    return result


# --------------------------------------------------------------------------------------
# Responses — core (status, body)
# --------------------------------------------------------------------------------------


def _missing_body(run_state: str, run: _Run | None, snap: _Snapshot | None) -> tuple[int, dict]:
    if run_state == "invalid":
        return 400, {"error": "invalid_session_id"}
    if run_state == "missing" or run is None:
        return 404, {"error": "session_not_found"}
    return 404, {"error": "no_spectate_stream", "has_hook_events": bool(snap and snap.hfd)}


def nodes_response(
    project_root: Path | str,
    session_id: str,
    capabilities: dict | None = None,
    *,
    if_none_match: str | None = None,
    now: datetime | None = None,
    capabilities_path: Path | str | None = None,
) -> tuple[int, dict | None, str | None]:
    """``/__spectate/nodes`` → ``(status, body, etag)``; ``body`` is None on 304."""
    state, run = open_run(project_root, session_id)
    if run is None:
        code, body = _missing_body(state, None, None)
        return code, body, None
    snap = _Snapshot(run)
    try:
        if not snap.has_stream:
            code, body = _missing_body("ok", run, snap)
            return code, body, None
        caps = capabilities if capabilities is not None else load_capabilities(capabilities_path)
        caps_mtime = capabilities_mtime_ns(capabilities_path)
        etag = _etag(snap.fingerprint(caps_mtime))
        if etag in _etag_tokens(if_none_match) or "*" in _etag_tokens(if_none_match):
            return 304, None, etag
        red = _load_reduced(snap, session_id, caps, caps_mtime)
        server_now = now_rfc3339(now)
        last_dt = _parse_ts(red["last_event_ts"])
        now_dt = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if red["synthetic"]:
            hint = "demo"
        elif (
            last_dt
            and not red["session_ended"]
            and 0 <= (now_dt - last_dt).total_seconds() <= LIVE_WINDOW_SECONDS
        ):
            hint = "live"
        else:
            hint = "recorded"
        body = {
            "session_id": session_id,
            "harness": red["harness"],
            "synthetic": red["synthetic"],
            "server_now": server_now,
            "last_event_ts": red["last_event_ts"],
            "session_ended": red["session_ended"],
            "source_hint": hint,
            "etag": etag,
            "nodes_truncated": red["nodes_truncated"],
            "skipped_malformed": red["skipped_malformed"],
            "nodes": red["nodes"],
        }
        return 200, body, etag
    finally:
        snap.close()


def events_response(
    project_root: Path | str,
    session_id: str,
    *,
    cursor: int | str | None = None,
    limit: int = 100,
) -> tuple[int, dict]:
    """``/__spectate/events`` — inspector timeline over absolute byte-offset cursors."""
    cursor = parse_query_int(cursor, None)
    state, run = open_run(project_root, session_id)
    if run is None:
        return _missing_body(state, None, None)
    snap = _Snapshot(run)
    try:
        if not snap.has_stream:
            return _missing_body("ok", run, snap)
        limit = max(1, min(int(limit), 500))
        stream = _read_stream(snap, session_id, cursor=cursor, limit=limit)
        events = stream["events"]
        fresh_view = cursor is None or stream["cursor_reset"]
        if stream["truncated"] and fresh_view:
            marker = _truncation_marker(
                session_id,
                stream["harness"] or "unknown",
                events[0]["ts"] if events else None,
                stream["window_start"],
            )
            events = [marker, *events]
        return 200, {
            "session_id": session_id,
            "events": events,
            "next_cursor": str(stream["next_cursor"]),
            "cursor_reset": stream["cursor_reset"],
            "truncated": stream["truncated"],
            "skipped_malformed": stream["skipped_malformed"],
        }
    finally:
        snap.close()


def _session_item(
    project_root: Path | str, name: str, capabilities: dict, caps_mtime: int
) -> dict | None:
    state, run = open_run(project_root, name)
    if run is None:
        return None
    snap = _Snapshot(run)
    try:
        if snap.sfd is None and snap.hfd is None:
            return None
        meta = _read_json_file(snap.mfd)
        mtime_ns = max(snap.s_stat[0], snap.h_stat[0], snap.m_stat[0])
        item = {
            "session_id": name,
            "harness": "unknown",
            "synthetic": bool(meta and meta.get("synthetic") is True),
            "mtime": mtime_ns / 1e9,
            "latest_status": "idle",
            "has_stream": snap.sfd is not None,
        }
        if snap.sfd is not None:
            red = _load_reduced(snap, name, capabilities, caps_mtime)
            item["harness"] = red["harness"]
            item["synthetic"] = red["synthetic"]
            item["latest_status"] = red["latest_status"]
        return item
    finally:
        snap.close()


def parse_query_int(value: Any, default: int | None) -> int | None:
    """Unsigned-int query value → int; absent/blank → ``default``; malformed → None."""
    if value is None or value == "":
        return default
    text = str(value)
    return int(text) if UINT_RE.fullmatch(text) else None


def list_sessions(
    project_root: Path | str,
    *,
    cursor: int | str | None = 0,
    limit: int = 50,
    harness: str | None = None,
    capabilities: dict | None = None,
    capabilities_path: Path | str | None = None,
) -> dict:
    """``/__spectate/sessions`` → ``{"sessions": [...], "next_cursor": None|str}``.

    Ranking (G3-8): non-synthetic with stream > non-synthetic without stream > synthetic,
    each by mtime descending. ``harness`` filters the list."""
    limit = max(1, min(int(limit), 200))
    cursor = parse_query_int(cursor, 0) or 0
    root = runs_root(project_root)
    caps = capabilities if capabilities is not None else load_capabilities(capabilities_path)
    caps_mtime = capabilities_mtime_ns(capabilities_path)
    items: list[dict] = []
    try:
        names = sorted(e.name for e in os.scandir(root) if e.is_dir(follow_symlinks=False))
    except OSError:
        names = []
    for name in names:
        if not validate_session_id(name):
            continue
        item = _session_item(project_root, name, caps, caps_mtime)
        if item is None or (harness and item["harness"] != harness):
            continue
        items.append(item)

    def rank(it: dict) -> tuple:
        group = 2 if it["synthetic"] else (0 if it["has_stream"] else 1)
        return (group, -it["mtime"], it["session_id"])

    items.sort(key=rank)
    page = items[cursor : cursor + limit]
    nxt = str(cursor + limit) if cursor + limit < len(items) else None
    return {"sessions": page, "next_cursor": nxt}


# --------------------------------------------------------------------------------------
# HTTP helpers — (status, headers, body)
# --------------------------------------------------------------------------------------


def base_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
    }


def _query(query: str | Mapping[str, str] | None) -> dict[str, str] | None:
    """Parse a raw query string or mapping. Repeated keys are refused (→ None)."""
    if query is None:
        return {}
    if isinstance(query, Mapping):
        return {str(k): str(v) for k, v in query.items()}
    try:
        pairs = urllib.parse.parse_qsl(query, keep_blank_values=True, max_num_fields=32)
    except ValueError:
        return None
    out: dict[str, str] = {}
    for k, v in pairs:
        if k in out:
            return None
        out[k] = v
    return out


def _uint(q: Mapping[str, str], name: str, default: int | None) -> int | None | bool:
    """→ int | default | False (invalid)."""
    if name not in q or q[name] == "":
        return default
    return int(q[name]) if UINT_RE.fullmatch(q[name]) else False


def _invalid_query() -> tuple[int, dict, dict]:
    return 400, base_headers(), {"error": "invalid_query"}


def http_capabilities(capabilities_path: Path | str | None = None) -> tuple[int, dict, dict]:
    return 200, base_headers(), load_capabilities(capabilities_path)


def http_sessions(
    project_root: Path | str,
    query: str | Mapping[str, str] | None = None,
    *,
    capabilities_path: Path | str | None = None,
) -> tuple[int, dict, dict]:
    q = _query(query)
    if q is None:
        return _invalid_query()
    cursor = _uint(q, "cursor", 0)
    limit = _uint(q, "limit", 50)
    harness = q.get("harness") or None
    if cursor is False or limit is False or limit == 0:
        return _invalid_query()
    if harness is not None and harness not in HARNESS_ENUM:
        return _invalid_query()
    body = list_sessions(
        project_root,
        cursor=int(cursor or 0),
        limit=int(limit if limit is not None else 50),
        harness=harness,
        capabilities_path=capabilities_path,
    )
    return 200, base_headers(), body


def http_events(
    project_root: Path | str,
    query: str | Mapping[str, str] | None = None,
) -> tuple[int, dict, dict]:
    q = _query(query)
    if q is None:
        return _invalid_query()
    session = q.get("session", "")
    if not validate_session_id(session):
        return 400, base_headers(), {"error": "invalid_session_id"}
    cursor = _uint(q, "cursor", None)
    limit = _uint(q, "limit", 100)
    if cursor is False or limit is False or limit == 0:
        return _invalid_query()
    code, body = events_response(
        project_root,
        session,
        cursor=cursor if isinstance(cursor, int) else None,
        limit=int(limit if limit is not None else 100),
    )
    return code, base_headers(), body


def http_nodes(
    project_root: Path | str,
    query: str | Mapping[str, str] | None = None,
    *,
    if_none_match: str | None = None,
    now: datetime | None = None,
    capabilities_path: Path | str | None = None,
) -> tuple[int, dict, dict | None]:
    """``If-None-Match`` is primary; ``since_etag=`` is an alias carrying the same value."""
    q = _query(query)
    if q is None:
        return _invalid_query()
    session = q.get("session", "")
    if not validate_session_id(session):
        return 400, base_headers(), {"error": "invalid_session_id"}
    code, body, etag = nodes_response(
        project_root,
        session,
        if_none_match=if_none_match or q.get("since_etag"),
        now=now,
        capabilities_path=capabilities_path,
    )
    headers = base_headers()
    if etag:
        headers["ETag"] = etag
    if code == 304:
        headers["X-Spectate-Server-Now"] = now_rfc3339(now)
        headers.pop("Content-Type")
    return code, headers, body


# --------------------------------------------------------------------------------------
# v0.3 — SSE stream slots + opt-in steer (pause-as-deny / capped note)
# --------------------------------------------------------------------------------------

STEER_FILE = "spectate-steer.json"
POSTURE_REL = Path(".ravenclaude") / "comfort-posture.yaml"
MAX_STEER_NOTE = 500
MAX_SSE_STREAMS = 4
SSE_HEARTBEAT_S = 15.0
SSE_POLL_S = 0.35
STEER_ACTIONS = frozenset({"pause", "resume", "note", "approve", "deny", "interrupt"})
STEER_DECISIONS = frozenset({"allow", "deny"})
INTERRUPT_ACTION = "interrupt"
PERMISSION_WAIT_S = 45.0
PERMISSION_POLL_S = 0.25
STOP_REASON_INTERRUPT = "Spectate interrupt from /spectate"

_SSE_LOCK = __import__("threading").Lock()
_SSE_ACTIVE = 0


def spectate_steer_enabled(project_root: Path | str) -> bool:
    """``spectate_steer: on`` in comfort-posture.yaml (absent ⇒ off)."""
    path = Path(project_root) / POSTURE_REL
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line.lower().startswith("spectate_steer"):
            continue
        if ":" not in line:
            continue
        val = line.split(":", 1)[1].strip().strip("\"'").lower()
        return val == "on"
    return False


def acquire_sse_slot() -> bool:
    global _SSE_ACTIVE
    with _SSE_LOCK:
        if _SSE_ACTIVE >= MAX_SSE_STREAMS:
            return False
        _SSE_ACTIVE += 1
        return True


def release_sse_slot() -> None:
    global _SSE_ACTIVE
    with _SSE_LOCK:
        if _SSE_ACTIVE > 0:
            _SSE_ACTIVE -= 1


def sse_active_count() -> int:
    with _SSE_LOCK:
        return _SSE_ACTIVE


def _harness_of_stream(project_root: Path | str, session_id: str) -> str | None:
    state, run = open_run(project_root, session_id)
    if state != "ok" or run is None:
        return None
    snap = _Snapshot(run)
    try:
        if not snap.has_stream:
            return None
        size = snap.s_stat[1]
        return _stream_harness(snap, session_id, size)
    finally:
        snap.close()


def read_steer_pending(project_root: Path | str, session_id: str) -> dict | None:
    if not validate_session_id(session_id):
        return None
    path = runs_root(project_root) / session_id / STEER_FILE
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if len(raw) > MAX_META_BYTES:
        return None
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def write_steer_pending(project_root: Path | str, session_id: str, payload: dict) -> None:
    root = runs_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    d = root / session_id
    d.mkdir(parents=True, exist_ok=True)
    target = d / STEER_FILE
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    fd, tmp = tempfile.mkstemp(prefix=".steer-", suffix=".tmp", dir=str(d))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, target)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def append_spectate_event(project_root: Path | str, event: dict) -> tuple[bool, str | None]:
    """Validate + append one event. Refuses harness mismatch with the stream head."""
    if not isinstance(event, dict):
        return False, "invalid_event"
    sid = event.get("session_id")
    if not validate_session_id(sid):
        return False, "invalid_session_id"
    errs = check_event(event)
    if errs:
        return False, "schema:" + errs[0]
    existing = _harness_of_stream(project_root, sid)
    if existing and event.get("harness") not in (None, existing):
        return False, "harness_mismatch"
    root = runs_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    d = root / sid
    d.mkdir(parents=True, exist_ok=True)
    path = d / SPECTATE_FILE
    line = json.dumps(event, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
    if len(line) > MAX_LINE_BYTES:
        return False, "line_too_long"
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | _O_CLOEXEC
    if _O_NOFOLLOW:
        flags |= _O_NOFOLLOW
    try:
        fd = os.open(str(path), flags, 0o644)
    except OSError:
        return False, "open_failed"
    try:
        os.write(fd, line)
        os.fsync(fd)
    finally:
        os.close(fd)
    return True, None


def apply_steer(
    project_root: Path | str,
    *,
    session_id: str,
    action: str,
    note: str | None = None,
    agent_id: str = "main",
) -> tuple[int, dict]:
    """Apply a steer action. Requires ``spectate_steer: on``."""
    if action not in STEER_ACTIONS:
        return 400, {"error": "invalid_action"}
    if not spectate_steer_enabled(project_root):
        return 403, {"error": "spectate_steer_off"}
    if not validate_session_id(session_id):
        return 400, {"error": "invalid_session_id"}
    if agent_id is None or not ID_RE.match(str(agent_id)):
        agent_id = "main"
    note_text = (note or "").strip()
    if len(note_text) > MAX_STEER_NOTE:
        note_text = note_text[:MAX_STEER_NOTE]
    if action == "note" and not note_text:
        return 400, {"error": "note_required"}

    state, run = open_run(project_root, session_id)
    if state == "invalid":
        return 400, {"error": "invalid_session_id"}
    if state == "missing" or run is None:
        return 404, {"error": "session_not_found"}
    snap = _Snapshot(run)
    try:
        if not snap.has_stream:
            return 404, {
                "error": "no_spectate_stream",
                "has_hook_events": snap.h_stat[1] > 0,
            }
        harness = _stream_harness(snap, session_id, snap.s_stat[1]) or "unknown"
    finally:
        snap.close()

    pending = read_steer_pending(project_root, session_id) or {}
    ts = now_rfc3339()
    decision = pending.get("decision") if pending.get("decision") in STEER_DECISIONS else None
    interrupt_pending = bool(pending.get("interrupt_pending"))
    if action == "pause":
        pending = {
            "paused": True,
            "ts": ts,
            "note": note_text,
            "note_chars": len(note_text),
            "note_pending": bool(note_text),
            "decision": decision,
            "interrupt_pending": interrupt_pending,
        }
    elif action == "resume":
        pending = {
            "paused": False,
            "ts": ts,
            "note": pending.get("note") if pending.get("note_pending") else "",
            "note_chars": int(pending.get("note_chars") or 0) if pending.get("note_pending") else 0,
            "note_pending": bool(pending.get("note_pending")),
            "decision": decision,
            "interrupt_pending": interrupt_pending,
        }
    elif action == "note":
        pending = {
            "paused": bool(pending.get("paused")),
            "ts": ts,
            "note": note_text,
            "note_chars": len(note_text),
            "note_pending": True,
            "decision": decision,
            "interrupt_pending": interrupt_pending,
        }
    elif action == INTERRUPT_ACTION:
        # v0.5 — arm continue:false on the next PreToolUse/PostToolUse/…
        pending = {
            "paused": bool(pending.get("paused")),
            "ts": ts,
            "note": pending.get("note") if pending.get("note_pending") else "",
            "note_chars": int(pending.get("note_chars") or 0) if pending.get("note_pending") else 0,
            "note_pending": bool(pending.get("note_pending")),
            "decision": None,
            "decision_ts": None,
            "interrupt_pending": True,
            "interrupt_ts": ts,
        }
    else:  # approve / deny — arms PermissionRequest wait (v0.4)
        pending = {
            "paused": bool(pending.get("paused")),
            "ts": ts,
            "note": pending.get("note") if pending.get("note_pending") else "",
            "note_chars": int(pending.get("note_chars") or 0) if pending.get("note_pending") else 0,
            "note_pending": bool(pending.get("note_pending")),
            "decision": "allow" if action == "approve" else "deny",
            "decision_ts": ts,
            "interrupt_pending": interrupt_pending,
        }
    write_steer_pending(project_root, session_id, pending)

    node_id = f"steer-{action}-{ts.replace(':', '').replace('.', '')[-12:]}"
    if not ID_RE.match(node_id):
        node_id = f"steer-{action}"
    event = {
        "schema": "rc.spectate.v1",
        "ts": ts,
        "session_id": session_id,
        "harness": harness if harness in HARNESS_ENUM else "unknown",
        "source": "steer",
        "kind": "steer.applied",
        "node_id": node_id,
        "agent_id": agent_id,
        "detail": "minimal",
        "steer": {
            "action": action,
            "note_chars": len(note_text) if action == "note" or note_text else 0,
        },
    }
    if pending.get("decision") in STEER_DECISIONS:
        event["steer"]["decision"] = pending["decision"]
    ok, err = append_spectate_event(project_root, event)
    if not ok:
        return 500, {"error": "append_failed", "detail": err}
    return 200, {
        "ok": True,
        "session_id": session_id,
        "action": action,
        "pending": _steer_pending_public(pending),
        "event": event,
    }


def _steer_pending_public(pending: dict | None) -> dict | None:
    if not pending:
        return None
    return {
        "paused": bool(pending.get("paused")),
        "note_pending": bool(pending.get("note_pending")),
        "note_chars": int(pending.get("note_chars") or 0),
        "decision": pending.get("decision") if pending.get("decision") in STEER_DECISIONS else None,
        "interrupt_pending": bool(pending.get("interrupt_pending")),
        "ts": pending.get("ts"),
    }


def steer_status(project_root: Path | str, session_id: str | None = None) -> dict:
    out: dict[str, Any] = {
        "enabled": spectate_steer_enabled(project_root),
        "pending": None,
    }
    if session_id and validate_session_id(session_id):
        pending = read_steer_pending(project_root, session_id)
        if pending:
            out["pending"] = _steer_pending_public(pending)
    return out


def consume_steer_decision(project_root: Path | str, session_id: str) -> str | None:
    """Return pending allow/deny and clear it. Pause/note/interrupt state kept."""
    pending = read_steer_pending(project_root, session_id)
    if not pending:
        return None
    decision = pending.get("decision")
    if decision not in STEER_DECISIONS:
        return None
    pending["decision"] = None
    pending["decision_ts"] = None
    write_steer_pending(project_root, session_id, pending)
    return decision


def consume_steer_interrupt(project_root: Path | str, session_id: str) -> bool:
    """Return True and clear interrupt_pending when armed. Clears armed approve/deny too."""
    pending = read_steer_pending(project_root, session_id)
    if not pending or not pending.get("interrupt_pending"):
        return False
    pending["interrupt_pending"] = False
    pending["interrupt_ts"] = None
    pending["decision"] = None
    pending["decision_ts"] = None
    write_steer_pending(project_root, session_id, pending)
    return True


def wait_for_steer_decision(
    project_root: Path | str,
    session_id: str,
    *,
    timeout_s: float | None = None,
    poll_s: float | None = None,
) -> str | None:
    """Poll for approve/deny/interrupt; consume when present. Timeout → None.

    Returns ``allow`` / ``deny`` / ``interrupt`` (interrupt wins over a concurrent
    approve/deny arm).
    """
    import time

    wait = PERMISSION_WAIT_S if timeout_s is None else float(timeout_s)
    step = PERMISSION_POLL_S if poll_s is None else float(poll_s)
    if wait < 0:
        wait = 0.0
    if step <= 0:
        step = PERMISSION_POLL_S
    deadline = time.monotonic() + wait
    while True:
        if consume_steer_interrupt(project_root, session_id):
            return INTERRUPT_ACTION
        decision = consume_steer_decision(project_root, session_id)
        if decision is not None:
            return decision
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(step, remaining))


def append_permission_resolve(
    project_root: Path | str,
    *,
    session_id: str,
    harness: str,
    decision: str,
    agent_id: str = "main",
    node_id: str | None = None,
) -> None:
    """Append permission.resolve so the reducer leaves waiting-approval."""
    if decision not in STEER_DECISIONS:
        return
    ts = now_rfc3339()
    nid = node_id or f"perm-resolve-{ts.replace(':', '').replace('.', '')[-12:]}"
    if not ID_RE.match(str(nid)):
        nid = "perm-resolve"
    event = {
        "schema": "rc.spectate.v1",
        "ts": ts,
        "session_id": session_id,
        "harness": harness if harness in HARNESS_ENUM else "unknown",
        "source": "steer",
        "kind": "permission.resolve",
        "node_id": nid,
        "agent_id": agent_id if ID_RE.match(str(agent_id)) else "main",
        "detail": "minimal",
        "asserted_status": "succeeded" if decision == "allow" else "failed",
    }
    append_spectate_event(project_root, event)


def consume_steer_note(project_root: Path | str, session_id: str) -> str | None:
    """Return pending note text (capped) and clear note_pending. Pause state kept."""
    pending = read_steer_pending(project_root, session_id)
    if not pending or not pending.get("note_pending"):
        return None
    note = str(pending.get("note") or "")[:MAX_STEER_NOTE]
    pending["note_pending"] = False
    pending["note"] = ""
    pending["note_chars"] = 0
    write_steer_pending(project_root, session_id, pending)
    return note or None


def spectate_file_size(project_root: Path | str, session_id: str) -> tuple[str, int]:
    """→ ``(state, size)`` where state is invalid|missing|no_stream|ok."""
    state, run = open_run(project_root, session_id)
    if state != "ok" or run is None:
        return state if state != "ok" else "missing", 0
    snap = _Snapshot(run)
    try:
        if not snap.has_stream:
            return "no_stream", 0
        return "ok", snap.s_stat[1]
    finally:
        snap.close()


def iter_new_spectate_lines(
    project_root: Path | str, session_id: str, cursor: int
) -> tuple[str, list[tuple[dict, int]], int]:
    """Read complete lines after absolute ``cursor``.

    → ``(state, [(event, end_offset), ...], next_cursor)``.
    """
    state, run = open_run(project_root, session_id)
    if state != "ok" or run is None:
        return state if state != "ok" else "missing", [], cursor
    snap = _Snapshot(run)
    try:
        if not snap.has_stream or snap.sfd is None:
            return "no_stream", [], cursor
        size = snap.s_stat[1]
        if cursor < 0:
            cursor = 0
        if cursor > size:
            # resume past EOF → reset to tail (live)
            cursor = size
        lines, next_cur = _complete_lines(snap.sfd, cursor, size)
        out: list[tuple[dict, int]] = []
        for raw, end in lines:
            ev, _err = parse_event_line(raw.strip(b" \t\r"), session_id)
            if ev is not None:
                out.append((ev, end))
        return "ok", out, next_cur
    finally:
        snap.close()
