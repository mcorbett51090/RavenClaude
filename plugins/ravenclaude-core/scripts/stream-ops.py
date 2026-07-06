#!/usr/bin/env python3
"""stream-ops.py — store layer for Agentic Work-Streams (P0).

Owns the on-disk store under a project's ``.ravenclaude/streams/``:

  .ravenclaude/streams/
    registry.json                 small, hot — read on every classify; the index of streams
    active-stream                 a one-line pointer file: the currently-active stream id
    <stream-id>/
      history.jsonl               append-only, cold — DERIVED events only (no raw prompt text)
      state.md                    a resume snapshot (last-known summary for crash-recovery)

DESIGN — reuse, don't duplicate
  Per the FORGE plan: this store does NOT duplicate the runs/ substrate. Each history event
  carries a ``session_id`` foreign key back to ``.ravenclaude/runs/<session_id>/`` so a reader
  can join a stream's events to the full run record without copying it here.

THE NO-EGRESS INVARIANT (load-bearing, gated)
  ``append_event`` accepts only DERIVED fields (label / terms / word_count / summary / kind /
  session_id / a derived score). It REFUSES a raw ``prompt`` / ``text`` key (raises ValueError)
  so a careless caller cannot persist prompt text. The stored line therefore never contains a
  prompt substring. Gate 110 greps a written history for a distinctive prompt phrase -> absent.

  ``summary`` is allowed because it is a caller-supplied DERIVED string (a short human label),
  not the raw prompt — but to keep the invariant robust it is length-capped and newline-stripped.

SLUG SAFETY (anti-traversal, gated in P1)
  Stream ids are slugified to ``[a-z0-9-]`` and rejected if they contain ``/``, ``..``, a leading
  dot, or resolve outside the streams root. ``_stream_dir`` re-checks containment after resolve.

DETERMINISM / FAIL-SAFE
  - registry.json is written sorted + indented (stable bytes).
  - JSONL append is one newline-terminated line per call (< PIPE_BUF for small lines).
  - A timestamp is RFC3339 UTC; callers may inject a fixed ``ts`` for deterministic tests.
  - Read helpers tolerate a missing/corrupt store (return empties), never raise to the caller.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

STREAMS_DIRNAME = "streams"
RAVENCLAUDE_DIRNAME = ".ravenclaude"
REGISTRY_NAME = "registry.json"
ACTIVE_POINTER_NAME = "active-stream"
HISTORY_NAME = "history.jsonl"
STATE_NAME = "state.md"

REGISTRY_SCHEMA_VERSION = 1
EVENT_SCHEMA_VERSION = 1

_SLUG_RE = re.compile(r"[^a-z0-9-]+")
_MAX_SLUG_LEN = 64
_MAX_SUMMARY_LEN = 280
# A derived `terms` element is a single stemmed token; cap its length and reject
# any whitespace-bearing element so a caller can't smuggle a multi-word phrase
# (which would defeat the no-egress invariant the way an uncapped summary would).
_MAX_TERM_LEN = 64
_MAX_TERMS = 64

# Keys a caller is FORBIDDEN to pass to append_event — the no-egress tripwire.
# A raw prompt/text/content/command field must never reach the history line.
_FORBIDDEN_EVENT_KEYS = frozenset({"prompt", "text", "content", "command", "raw", "body"})

# The only fields persisted to a history event (besides the auto schema/ts/kind).
_ALLOWED_EVENT_FIELDS = frozenset(
    {"label", "terms", "word_count", "summary", "session_id", "score", "stream_id"}
)


# ── Slug / path safety ───────────────────────────────────────────────────────


def slugify(name: str) -> str:
    """Turn an arbitrary stream name into a safe ``[a-z0-9-]`` slug.

    Lowercases, replaces runs of non-slug chars with a single ``-``, trims leading/trailing
    ``-``, caps length. Returns "" if nothing survives (the caller should reject "").
    """
    if not name:
        return ""
    s = name.strip().casefold()
    s = _SLUG_RE.sub("-", s)
    s = s.strip("-")
    return s[:_MAX_SLUG_LEN]


def is_safe_slug(slug: str) -> bool:
    """True iff the slug is a single safe path segment (no traversal, no separators)."""
    if not slug or len(slug) > _MAX_SLUG_LEN:
        return False
    if slug != slugify(slug):
        return False
    # belt-and-suspenders against the obvious traversal shapes
    if "/" in slug or "\\" in slug or ".." in slug or slug.startswith("."):
        return False
    return True


def streams_root(project_root: str | os.PathLike) -> Path:
    return Path(project_root) / RAVENCLAUDE_DIRNAME / STREAMS_DIRNAME


def _stream_dir(project_root: str | os.PathLike, stream_id: str) -> Path:
    """Resolve a stream's directory, re-checking it stays INSIDE the streams root.

    Raises ValueError on an unsafe slug or a path that escapes the root after resolve.
    """
    if not is_safe_slug(stream_id):
        raise ValueError(f"unsafe stream id: {stream_id!r}")
    root = streams_root(project_root)
    target = (root / stream_id).resolve()
    root_resolved = root.resolve()
    # Containment check: target must be root_resolved itself or a descendant.
    if target != root_resolved and root_resolved not in target.parents:
        raise ValueError(f"stream dir escapes streams root: {stream_id!r}")
    return target


# ── Time helper (injectable for deterministic tests) ──────────────────────────


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Registry ──────────────────────────────────────────────────────────────────


def _registry_path(project_root: str | os.PathLike) -> Path:
    return streams_root(project_root) / REGISTRY_NAME


def read_registry(project_root: str | os.PathLike) -> dict:
    """Read registry.json. Returns an empty, schema-stamped registry if absent/corrupt."""
    path = _registry_path(project_root)
    empty = {"schema_version": REGISTRY_SCHEMA_VERSION, "streams": {}}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or "streams" not in data:
            return empty
        data.setdefault("schema_version", REGISTRY_SCHEMA_VERSION)
        if not isinstance(data["streams"], dict):
            data["streams"] = {}
        return data
    except (OSError, json.JSONDecodeError):
        return empty


def write_registry(project_root: str | os.PathLike, registry: dict) -> None:
    """Write registry.json sorted + indented (stable bytes). Creates the streams root."""
    root = streams_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    path = _registry_path(project_root)
    payload = {
        "schema_version": registry.get("schema_version", REGISTRY_SCHEMA_VERSION),
        "streams": registry.get("streams", {}),
    }
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)  # atomic on POSIX


def create_stream(
    project_root: str | os.PathLike,
    name: str,
    *,
    description: str = "",
    ts: str | None = None,
) -> str:
    """Create (or no-op return) a stream from a human name. Returns the stream id (slug).

    Idempotent: creating an existing stream id updates nothing destructive; it just returns
    the id. Initializes the stream dir + an empty centroid in the registry entry.
    """
    stream_id = slugify(name)
    if not is_safe_slug(stream_id):
        raise ValueError(f"name does not slugify to a safe stream id: {name!r}")
    registry = read_registry(project_root)
    streams = registry["streams"]
    now = ts or _now_iso()
    if stream_id not in streams:
        streams[stream_id] = {
            "name": name,
            "description": description,
            "created": now,
            "updated": now,
            "event_count": 0,
            "centroid": {},
        }
        write_registry(project_root, registry)
    # ensure the dir exists
    _stream_dir(project_root, stream_id).mkdir(parents=True, exist_ok=True)
    return stream_id


def list_streams(project_root: str | os.PathLike) -> list[dict]:
    """Return a sorted list of stream summary dicts (id + name + counts + dates).

    Read-only; never raises. The active stream id (if any) is included on each entry as
    ``active: bool``.
    """
    registry = read_registry(project_root)
    active = read_active(project_root)
    out: list[dict] = []
    for sid in sorted(registry["streams"].keys()):
        meta = registry["streams"][sid]
        out.append(
            {
                "id": sid,
                "name": meta.get("name", sid),
                "description": meta.get("description", ""),
                "created": meta.get("created", ""),
                "updated": meta.get("updated", ""),
                "event_count": meta.get("event_count", 0),
                "active": sid == active,
            }
        )
    return out


# ── Active-stream pointer ──────────────────────────────────────────────────────


def _active_path(project_root: str | os.PathLike) -> Path:
    return streams_root(project_root) / ACTIVE_POINTER_NAME


def read_active(project_root: str | os.PathLike) -> str | None:
    """Read the active-stream pointer. Returns None if unset/missing/unsafe."""
    path = _active_path(project_root)
    try:
        sid = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not sid or not is_safe_slug(sid):
        return None
    return sid


def set_active(project_root: str | os.PathLike, stream_id: str) -> None:
    """Point active-stream at ``stream_id`` (must be a known, safe stream)."""
    if not is_safe_slug(stream_id):
        raise ValueError(f"unsafe stream id: {stream_id!r}")
    registry = read_registry(project_root)
    if stream_id not in registry["streams"]:
        raise ValueError(f"unknown stream id: {stream_id!r}")
    root = streams_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    _active_path(project_root).write_text(stream_id + "\n", encoding="utf-8")


def clear_active(project_root: str | os.PathLike) -> None:
    """Remove the active-stream pointer (no stream is active)."""
    try:
        _active_path(project_root).unlink()
    except OSError:
        pass


# ── History (append-only, DERIVED-only) ───────────────────────────────────────


def _validate_event_fields(fields: dict) -> None:
    """Raise ValueError if a caller passed a forbidden or non-allow-listed field.

    This is the no-egress tripwire enforced in code (the gate proves it bidirectionally).
    The check is an ALLOWLIST, not just a 6-key denylist: any key outside
    ``_ALLOWED_EVENT_FIELDS`` is refused, so a raw prompt smuggled under an
    arbitrary key name (e.g. ``extra={"note": <raw prompt>}``) can never reach
    the append-only history line. The forbidden-key check runs first so the
    common mistake still gets the specific, clearer error.
    """
    for key in fields:
        kl = key.casefold()
        if kl in _FORBIDDEN_EVENT_KEYS:
            raise ValueError(
                f"refusing to persist forbidden raw-content field {key!r} to stream history "
                "(no-egress invariant: history stores DERIVED labels/terms only)"
            )
        if kl not in _ALLOWED_EVENT_FIELDS:
            raise ValueError(
                f"refusing to persist non-allow-listed field {key!r} to stream history "
                "(no-egress invariant: only DERIVED allow-listed fields are permitted)"
            )


def append_event(
    project_root: str | os.PathLike,
    stream_id: str,
    *,
    kind: str = "classified",
    label: str | None = None,
    terms: list[str] | None = None,
    word_count: int | None = None,
    summary: str | None = None,
    session_id: str | None = None,
    score: float | None = None,
    ts: str | None = None,
    extra: dict | None = None,
) -> dict:
    """Append one DERIVED event to a stream's history.jsonl and bump the registry count.

    Only derived fields are accepted. ``extra`` is an escape hatch for additional DERIVED
    keys, but it is validated against the forbidden-key set first, so a raw prompt can never
    sneak in. Returns the written event dict. Creates the stream dir if needed.
    """
    if not is_safe_slug(stream_id):
        raise ValueError(f"unsafe stream id: {stream_id!r}")

    # Build the candidate field set and validate it against the no-egress tripwire.
    candidate: dict = {}
    if extra:
        _validate_event_fields(extra)
        candidate.update(extra)
    if label is not None:
        candidate["label"] = str(label)
    if terms is not None:
        # Enforce the single-token contract at the API boundary (like `summary` is
        # capped): drop any element that is empty, over the per-term cap, or carries
        # whitespace (a multi-word phrase) — so a current or future caller can't
        # smuggle a raw phrase into history.jsonl and defeat the no-egress invariant.
        cleaned_terms = []
        for t in terms:
            tok = str(t).strip()
            if not tok or len(tok) > _MAX_TERM_LEN or any(ch.isspace() for ch in tok):
                continue
            cleaned_terms.append(tok)
        candidate["terms"] = cleaned_terms[:_MAX_TERMS]
    if word_count is not None:
        candidate["word_count"] = int(word_count)
    if summary is not None:
        # summary is a DERIVED short label — cap + strip newlines to keep it from carrying
        # a multi-line prompt body, which would defeat the no-egress invariant.
        s = " ".join(str(summary).split())[:_MAX_SUMMARY_LEN]
        candidate["summary"] = s
    if session_id is not None:
        candidate["session_id"] = str(session_id)
    if score is not None:
        candidate["score"] = round(float(score), 6)

    # Normalize `summary` from ANY source (the `summary=` kwarg OR an `extra`
    # dict) so the cap + newline-strip no-egress protection can't be bypassed by
    # routing a multi-line prompt body through `extra={"summary": ...}`.
    if "summary" in candidate:
        candidate["summary"] = " ".join(str(candidate["summary"]).split())[:_MAX_SUMMARY_LEN]

    # Final guard: every persisted key must be an allowed derived field (extra may add
    # benign keys, but they cannot be forbidden or non-allow-listed — checked above).
    _validate_event_fields(candidate)

    event = {
        "schema_version": EVENT_SCHEMA_VERSION,
        "ts": ts or _now_iso(),
        "kind": str(kind),
        "stream_id": stream_id,
    }
    event.update(candidate)

    sdir = _stream_dir(project_root, stream_id)
    sdir.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, sort_keys=True)
    with open(sdir / HISTORY_NAME, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    # Bump the registry event_count + updated; tolerate an absent entry.
    registry = read_registry(project_root)
    meta = registry["streams"].get(stream_id)
    if meta is not None:
        meta["event_count"] = int(meta.get("event_count", 0)) + 1
        meta["updated"] = event["ts"]
        write_registry(project_root, registry)

    return event


def read_history(project_root: str | os.PathLike, stream_id: str, *, limit: int = 0) -> list[dict]:
    """Read a stream's history events (newest last). Tolerant of torn/corrupt lines.

    ``limit`` > 0 returns only the last ``limit`` events. Never raises to the caller.
    """
    if not is_safe_slug(stream_id):
        return []
    try:
        path = _stream_dir(project_root, stream_id) / HISTORY_NAME
    except ValueError:
        return []
    events: list[dict] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError:
                    continue  # torn write / corrupt line — drop it, never raise
                if isinstance(obj, dict):
                    events.append(obj)
    except OSError:
        return []
    if limit and limit > 0:
        return events[-limit:]
    return events


# ── Resume snapshot (state.md) ────────────────────────────────────────────────


def write_state(
    project_root: str | os.PathLike,
    stream_id: str,
    *,
    summary: str,
    session_id: str | None = None,
    ts: str | None = None,
) -> Path:
    """Write a crash-resume snapshot (state.md) for a stream.

    The summary is a DERIVED resume note (what to pick back up), NOT a raw prompt — it is the
    caller's responsibility to keep it derived; we cap + strip to keep the no-egress posture.
    Returns the state.md path.
    """
    if not is_safe_slug(stream_id):
        raise ValueError(f"unsafe stream id: {stream_id!r}")
    safe_summary = " ".join(str(summary).split())[: _MAX_SUMMARY_LEN * 4]
    when = ts or _now_iso()
    sdir = _stream_dir(project_root, stream_id)
    sdir.mkdir(parents=True, exist_ok=True)
    body_lines = [
        f"# Stream resume snapshot — {stream_id}",
        "",
        f"_Updated: {when}_",
    ]
    if session_id:
        body_lines.append(f"_Last session: {session_id}_")
    body_lines += ["", "## Where to pick up", "", safe_summary, ""]
    state_path = sdir / STATE_NAME
    state_path.write_text("\n".join(body_lines), encoding="utf-8")
    return state_path


def read_state(project_root: str | os.PathLike, stream_id: str) -> str | None:
    """Read a stream's state.md resume snapshot, or None if absent. Never raises."""
    if not is_safe_slug(stream_id):
        return None
    try:
        path = _stream_dir(project_root, stream_id) / STATE_NAME
        return path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None


# ── Centroid helpers (registry-resident) ──────────────────────────────────────


def get_centroids(project_root: str | os.PathLike) -> dict[str, dict[str, float]]:
    """Return {stream_id: centroid} for all streams — the input to classify()."""
    registry = read_registry(project_root)
    return {
        sid: dict(meta.get("centroid", {}))
        for sid, meta in registry["streams"].items()
    }


def set_centroid(
    project_root: str | os.PathLike,
    stream_id: str,
    centroid: dict[str, float],
) -> None:
    """Persist a stream's updated centroid into the registry."""
    if not is_safe_slug(stream_id):
        raise ValueError(f"unsafe stream id: {stream_id!r}")
    registry = read_registry(project_root)
    meta = registry["streams"].get(stream_id)
    if meta is None:
        raise ValueError(f"unknown stream id: {stream_id!r}")
    meta["centroid"] = {k: round(float(v), 6) for k, v in centroid.items()}
    write_registry(project_root, registry)


# ── CLI shim — JSON in / JSON out, for the gate + manual use ───────────────────


def _main(argv: list[str]) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(description="Stream store operations (P0).")
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    p_create = sub.add_parser("create")
    p_create.add_argument("name")
    p_create.add_argument("--description", default="")

    p_active = sub.add_parser("set-active")
    p_active.add_argument("stream_id")

    sub.add_parser("get-active")

    p_show = sub.add_parser("show")
    p_show.add_argument("stream_id")
    p_show.add_argument("--limit", type=int, default=0)

    args = ap.parse_args(argv)

    try:
        return _dispatch(args)
    except ValueError as exc:
        # Clean CLI error (e.g. unsafe slug / unknown stream) — no traceback.
        print(f"rc streams: {exc}", file=sys.stderr)
        return 1


def _dispatch(args) -> int:
    if args.cmd == "list":
        print(json.dumps(list_streams(args.root), sort_keys=True))
    elif args.cmd == "create":
        sid = create_stream(args.root, args.name, description=args.description)
        print(json.dumps({"id": sid}, sort_keys=True))
    elif args.cmd == "set-active":
        set_active(args.root, args.stream_id)
        print(json.dumps({"active": args.stream_id}, sort_keys=True))
    elif args.cmd == "get-active":
        print(json.dumps({"active": read_active(args.root)}, sort_keys=True))
    elif args.cmd == "show":
        print(
            json.dumps(
                {
                    "history": read_history(args.root, args.stream_id, limit=args.limit),
                    "state": read_state(args.root, args.stream_id),
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(_main(sys.argv[1:]))
