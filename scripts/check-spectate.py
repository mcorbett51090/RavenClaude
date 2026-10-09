#!/usr/bin/env python3
"""check-spectate.py — Gate 294: Harness Spectate schema, capabilities, fixtures, store.

What it proves (each section fails independently, every failure is named):

  schema        the event schema is strict (``additionalProperties:false`` at every object
                level), carries the id charsets, ``step.seed`` and the status enum
  fixtures      ``demo-session.jsonl`` is accepted; every ``bad-*.jsonl`` line is rejected
                *for the tagged reason*, not merely rejected
  capabilities  8 harnesses x 14 keys; a cell is non-``unknown`` only when the frozen atlas
                row is *verified* and carries evidence; Grok non-unknown cells also require
                a measured ``probe`` id (v0.2); ``tool_use_id.harnesses`` covers all 8
  parity        when ``jsonschema`` is importable, it and the store's interpreter agree on
                every fixture line (the store is the single source of truth at runtime)
  store         path safety (traversal, symlink), 404/400 envelopes, ETag/304, byte cursors,
                the 5 MiB tail window, the 2000-node cap, the reducer golden, and that the
                synthetic gallery reaches all 11 statuses

Exit codes: 0 pass · 1 failure · 3 unwired (schema/fixtures/capabilities/store absent —
never a silent green).

``--must-fail`` plants known-bad events and exits 3 only if the gate rejects every one of
them; ``--must-fail-convention`` declares that exit for ``audit-gates.sh``'s ``rc_mustfail``.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORE = REPO / "plugins/ravenclaude-core"
SCHEMA = CORE / "knowledge/spectate-event-schema-v1.json"
CAPS = CORE / "knowledge/spectate-capabilities.json"
FIXTURES = REPO / "tests/fixtures/spectate"
STORE = CORE / "scripts/spectate_store.py"
DEMO = CORE / "scripts/spectate_demo.py"

TEETH_EXIT = 3
FIXTURE_SESSION = "demo-fixture1"
ALL_STATUSES = frozenset(
    {
        "available",
        "unavailable-harness",
        "denied-org",
        "denied-plugin",
        "denied-user",
        "denied-harness",
        "running",
        "succeeded",
        "failed",
        "waiting-approval",
        "idle",
    }
)
# Reason tag each bad fixture must be rejected for (check_event reason prefix).
BAD_EXPECT = {
    "bad-raw-prompt.jsonl": "sensitive-key",
    "bad-nested-args.jsonl": "sensitive-key",
    "bad-secret-in-target.jsonl": "secret",
    "bad-url-query-target.jsonl": "schema",
    "bad-status.jsonl": "schema",
    "bad-session-traversal.jsonl": "schema",
}


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = mod
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return mod


def unwired() -> list[str]:
    return [
        str(p.relative_to(REPO))
        for p in (SCHEMA, CAPS, STORE, DEMO, FIXTURES / "demo-session.jsonl")
        if not p.is_file()
    ]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8"
    )


# ── schema ───────────────────────────────────────────────────────────────────────────


def _objects(node, path="#"):
    """Yield (path, subschema) for every subschema that declares ``properties``."""
    if isinstance(node, dict):
        if "properties" in node:
            yield path, node
        for k, v in node.items():
            if k == "properties":
                for pk, pv in v.items():
                    yield from _objects(pv, f"{path}/properties/{pk}")
            elif k in ("if", "then", "else"):
                continue  # conditional branches constrain, they do not declare a payload shape
            elif isinstance(v, dict | list):
                yield from _objects(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _objects(v, f"{path}/{i}")


def check_schema(schema: dict) -> list[str]:
    errs: list[str] = []
    if schema.get("properties", {}).get("schema", {}).get("const") != "rc.spectate.v1":
        errs.append("schema: root `schema` const must be rc.spectate.v1")
    for path, sub in _objects(schema):
        if sub.get("additionalProperties") is not False:
            errs.append(f"schema: {path} lacks additionalProperties:false")
    defs = schema.get("$defs", {})
    if "step.seed" not in defs.get("kind", {}).get("enum", []):
        errs.append("schema: kind enum lacks step.seed")
    if set(schema.get("x-statuses", [])) != ALL_STATUSES:
        errs.append("schema: x-statuses is not the 11 reducer statuses")
    if set(defs.get("status", {}).get("enum", [])) != ALL_STATUSES:
        errs.append("schema: status enum is not the 11 reducer statuses")
    want_id = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$"
    want_sid = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"
    if defs.get("id", {}).get("pattern") != want_id:
        errs.append("schema: $defs.id pattern drifted")
    if defs.get("session_id", {}).get("pattern") != want_sid:
        errs.append("schema: $defs.session_id pattern drifted")
    if set(defs.get("deny", {}).get("properties", {}).get("by", {}).get("enum", [])) != {
        "org",
        "plugin",
        "user",
        "harness",
    }:
        errs.append("schema: deny.by enum is not org/plugin/user/harness")
    if not {"prompt", "args", "output", "token", "secret", "password"} <= set(
        schema.get("x-sensitive-keys", [])
    ):
        errs.append("schema: x-sensitive-keys lacks a core forbidden payload key")
    return errs


# ── fixtures ─────────────────────────────────────────────────────────────────────────


def check_fixtures(store, jsonschema_validate) -> list[str]:
    errs: list[str] = []
    demo_rows = read_jsonl(FIXTURES / "demo-session.jsonl")
    if not demo_rows:
        errs.append("fixtures: demo-session.jsonl is empty")
    for i, row in enumerate(demo_rows):
        for reason in store.check_event(row):
            errs.append(f"fixtures: demo-session.jsonl:{i + 1} rejected: {reason}")
        if jsonschema_validate and bool(jsonschema_validate(row)) != bool(
            [r for r in store.check_event(row) if r.startswith("schema:")]
        ):
            errs.append(f"parity: demo-session.jsonl:{i + 1} jsonschema/store disagree")
    for name, tag in BAD_EXPECT.items():
        path = FIXTURES / name
        if not path.is_file():
            errs.append(f"fixtures: {name} missing")
            continue
        rows = read_jsonl(path)
        if not rows:
            errs.append(f"fixtures: {name} is empty")
        for i, row in enumerate(rows):
            reasons = store.check_event(row)
            if not any(r.startswith(tag + ":") for r in reasons):
                errs.append(f"fixtures: {name}:{i + 1} not rejected for `{tag}` (got {reasons})")
            if jsonschema_validate and bool(jsonschema_validate(row)) != bool(
                [r for r in reasons if r.startswith("schema:")]
            ):
                errs.append(f"parity: {name}:{i + 1} jsonschema/store disagree")
            line = json.dumps(row).encode()
            ev, why = store.parse_event_line(line, row.get("session_id", ""))
            if name == "bad-secret-in-target.jsonl":
                # A secret in the optional target is dropped, never persisted or served.
                if ev is None or "sk-ant" in json.dumps(ev) or "target" in (ev.get("tool") or {}):
                    errs.append(f"fixtures: {name}:{i + 1} secret survived parse_event_line")
            elif ev is not None:
                errs.append(f"fixtures: {name}:{i + 1} accepted by parse_event_line")
    for sid in (r["session_id"] for r in read_jsonl(FIXTURES / "bad-session-traversal.jsonl")):
        if store.validate_session_id(sid):
            errs.append(f"fixtures: session id {sid!r} passes validate_session_id")
    return errs


# ── capabilities ─────────────────────────────────────────────────────────────────────

HARNESS_ORDER = (
    "claude-code",
    "codex-cli",
    "copilot-cli",
    "copilot-vscode",
    "cursor",
    "gemini-cli",
    "grok-build",
    "grok-bot",
)


GROK_LANES = ("grok-bot", "grok-build")  # gallery fixtures still require ≥1 unknown cell


def mapped_state(cell: dict | None) -> str:
    """Atlas cell → capability state (F06 mapping): only verified supported/partial/unsupported."""
    if not cell:
        return "unknown"
    if cell.get("verification") == "verified" and cell.get("state") in (
        "supported",
        "partial",
        "unsupported",
    ):
        return cell["state"]
    return "unknown"


def check_capabilities() -> list[str]:
    errs: list[str] = []
    caps = json.loads(CAPS.read_text(encoding="utf-8"))
    keys = caps.get("keys", [])
    if len(keys) != 14 or len(set(keys)) != 14:
        errs.append(f"capabilities: expected 14 distinct keys, got {len(keys)}")
    if set(caps.get("harnesses", {})) != set(HARNESS_ORDER):
        errs.append("capabilities: harness set is not the 8 supported harnesses")
    states = set(caps.get("states", []))
    for h in HARNESS_ORDER:
        cells = caps.get("harnesses", {}).get(h, {})
        if set(cells) != set(keys):
            errs.append(f"capabilities: {h} keys differ from the key list")
        for key, cell in cells.items():
            st = cell.get("state")
            if st not in states:
                errs.append(f"capabilities: {h}.{key} has invalid state {st!r}")
            row = cell.get("source_row")
            atlas = caps.get("atlas_cells", {}).get(h, {}).get(row) if row else None
            # v0.2: Grok lanes use the same atlas map; a non-unknown cell on a
            # previously-pinned lane must cite a probe id (measured upgrade).
            want = mapped_state(atlas)
            if st != want:
                errs.append(f"capabilities: {h}.{key} is {st} but the atlas row maps to {want}")
            if st != "unknown" and not cell.get("evidence"):
                errs.append(f"capabilities: {h}.{key} is {st} with no evidence ids")
            if st != "unknown" and atlas and cell.get("evidence") != atlas.get("evidence"):
                errs.append(f"capabilities: {h}.{key} evidence differs from its atlas row")
            if h in GROK_LANES and st != "unknown" and not cell.get("probe"):
                errs.append(
                    f"capabilities: {h}.{key} is {st} without a probe id "
                    "(Grok non-unknown cells require a measured v0.2 probe)"
                )
    # Per-harness tool_use_id support (corr_id source) — required from v0.2.
    tui = caps.get("tool_use_id") or {}
    tui_h = tui.get("harnesses") or {}
    if set(tui_h) != set(HARNESS_ORDER):
        errs.append("capabilities: tool_use_id.harnesses must cover all 8 harnesses")
    for h, cell in tui_h.items():
        if cell.get("state") not in ("supported", "unsupported", "unknown"):
            errs.append(f"capabilities: tool_use_id.{h} has invalid state {cell.get('state')!r}")
        if not cell.get("evidence"):
            errs.append(f"capabilities: tool_use_id.{h} needs an evidence note")
    return errs


# ── store behaviour ──────────────────────────────────────────────────────────────────


def _mk_run(root: Path, sid: str, spectate=None, hooks=None, meta=None) -> Path:
    d = root / ".ravenclaude" / "runs" / sid
    d.mkdir(parents=True, exist_ok=True)
    if spectate is not None:
        (d / "spectate-events.jsonl").write_bytes(spectate)
    if hooks is not None:
        (d / "hook-events.jsonl").write_bytes(hooks)
    if meta is not None:
        (d / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return d


def _jsonl(rows: list[dict]) -> bytes:
    return "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows).encode()


def check_golden(store) -> list[str]:
    errs: list[str] = []
    golden = json.loads((FIXTURES / "expected-reduce.json").read_text(encoding="utf-8"))
    caps = store.load_capabilities(CAPS)
    events = read_jsonl(FIXTURES / "demo-session.jsonl")
    hooks = []
    for line in (FIXTURES / "hook-events-deny.jsonl").read_bytes().splitlines():
        h, _ = store.parse_hook_line(line)
        if h:
            hooks.append(h)
    want = golden["demo_session"]
    got = store.reduce_session(events, hooks, caps, harness=want["harness"])
    for field in ("session_ended", "latest_status", "event_count"):
        if got[field] != want[field]:
            errs.append(f"golden: {field} is {got[field]!r}, expected {want[field]!r}")
    by_id = {n["node_id"]: n for n in got["nodes"]}
    if set(by_id) != set(want["nodes"]):
        errs.append(f"golden: node ids differ: {sorted(set(by_id) ^ set(want['nodes']))}")
    for nid, exp in want["nodes"].items():
        n = by_id.get(nid)
        if n is None:
            continue
        actual = {
            "status": n["status"],
            "parent_id": n["parent_id"],
            "kind": n["kind"],
            "deny_by": (n["deny"] or {}).get("by"),
        }
        for k, v in exp.items():
            if actual[k] != v:
                errs.append(f"golden: {nid}.{k} is {actual[k]!r}, expected {v!r}")
    # A deny joins on corr_id only: strip it and the denied tool must read as succeeded.
    rule = golden["deny_requires_corr_id"]
    stripped = [
        {k: v for k, v in e.items() if not (k == "corr_id" and e.get("node_id") == rule["node"])}
        for e in events
    ]
    r2 = store.reduce_session(stripped, hooks, caps, harness=want["harness"])
    node = next(n for n in r2["nodes"] if n["node_id"] == rule["node"])
    if node["status"] != rule["status_without_corr_id"]:
        errs.append(f"golden: deny joined without a corr_id ({node['status']})")
    # unknown capability never becomes unavailable-harness
    bot = store.reduce_session(events, [], caps, harness="grok-bot")
    if any(n["status"] == "unavailable-harness" for n in bot["nodes"]):
        errs.append("golden: unknown capability produced unavailable-harness")
    return errs


def check_gallery(store, demo, root: Path) -> list[str]:
    errs: list[str] = []
    when = datetime(2026, 10, 9, 12, 0, 0, tzinfo=timezone.utc)
    written = demo.write_demo(root, now=when)
    if sorted(written) != sorted(f"demo-{h}" for h in HARNESS_ORDER):
        errs.append(f"gallery: demo sessions are {written}")
    before = (root / ".ravenclaude/runs/demo-claude-code/spectate-events.jsonl").read_bytes()
    demo.write_demo(root, now=when)
    after = (root / ".ravenclaude/runs/demo-claude-code/spectate-events.jsonl").read_bytes()
    if before != after:
        errs.append("gallery: re-running spectate_demo is not idempotent")
    seen: set[str] = set()
    for sid in written:
        meta = json.loads((root / ".ravenclaude/runs" / sid / "meta.json").read_text())
        if meta.get("synthetic") is not True:
            errs.append(f"gallery: {sid} meta.json is not stamped synthetic")
        code, body, etag = store.nodes_response(root, sid, store.load_capabilities(CAPS), now=when)
        if code != 200 or not etag:
            errs.append(f"gallery: {sid} nodes → {code}")
            continue
        if body["source_hint"] != "demo" or body["synthetic"] is not True:
            errs.append(f"gallery: {sid} is not served as demo/synthetic")
        seen.update(n["status"] for n in body["nodes"])
        if sid in ("demo-grok-bot", "demo-grok-build"):
            if any(n["status"] == "unavailable-harness" for n in body["nodes"]):
                errs.append(f"gallery: {sid} shows unavailable-harness for an unknown capability")
            if not any(n.get("capability_state") == "unknown" for n in body["nodes"]):
                errs.append(f"gallery: {sid} never reports capability_state unknown")
    if ALL_STATUSES - seen:
        errs.append(f"gallery: statuses never reached: {sorted(ALL_STATUSES - seen)}")
    # The override that makes unavailable-harness reachable is honoured on synthetic only.
    vs = root / ".ravenclaude/runs/demo-copilot-vscode/meta.json"
    meta = json.loads(vs.read_text())
    meta["synthetic"] = False
    vs.write_text(json.dumps(meta))
    _, body, _ = store.nodes_response(root, "demo-copilot-vscode", store.load_capabilities(CAPS))
    if any(n["status"] == "unavailable-harness" for n in body["nodes"]):
        errs.append("gallery: capability_overrides honoured on a non-synthetic session")
    return errs


def check_http(store, root: Path) -> list[str]:
    errs: list[str] = []
    demo_rows = read_jsonl(FIXTURES / "demo-session.jsonl")
    hooks = (FIXTURES / "hook-events-deny.jsonl").read_bytes()
    _mk_run(root, FIXTURE_SESSION, _jsonl(demo_rows), hooks)
    _mk_run(root, "hooksonly1", None, hooks)

    def want(label, got, exp):
        if got != exp:
            errs.append(f"http: {label}: got {got!r}, expected {exp!r}")

    for bad in ("..", "../etc", "foo/bar", "%2e%2e", ".hidden", "", "a" * 129):
        code, _, body = store.http_nodes(root, {"session": bad})
        want(
            f"nodes session {bad!r}", (code, (body or {}).get("error")), (400, "invalid_session_id")
        )
        code, _, body = store.http_events(root, {"session": bad})
        want(
            f"events session {bad!r}",
            (code, (body or {}).get("error")),
            (400, "invalid_session_id"),
        )
    for q in (
        {"session": FIXTURE_SESSION, "limit": "-1"},
        {"session": FIXTURE_SESSION, "cursor": "x"},
    ):
        code, _, body = store.http_events(root, q)
        want(f"events query {q}", (code, body.get("error")), (400, "invalid_query"))
    code, _, body = store.http_sessions(root, {"limit": "0"})
    want("sessions limit=0", (code, body.get("error")), (400, "invalid_query"))
    code, _, body = store.http_sessions(root, {"harness": "nope"})
    want("sessions harness=nope", (code, body.get("error")), (400, "invalid_query"))
    code, _, body = store.http_nodes(root, {"session": "nosuchsession99"})
    want("missing session", (code, body.get("error")), (404, "session_not_found"))
    code, _, body = store.http_nodes(root, {"session": "hooksonly1"})
    want(
        "hook-only session",
        (code, body.get("error"), body.get("has_hook_events")),
        (404, "no_spectate_stream", True),
    )

    code, headers, body = store.http_nodes(root, {"session": FIXTURE_SESSION})
    want("nodes 200", code, 200)
    etag = headers.get("ETag")
    if not etag or body.get("etag") != etag:
        errs.append("http: nodes ETag header/body mismatch")
    for label, kw in (
        ("If-None-Match", {"if_none_match": etag}),
        ("since_etag alias", None),
    ):
        if kw is None:
            code, h2, b2 = store.http_nodes(root, {"session": FIXTURE_SESSION, "since_etag": etag})
        else:
            code, h2, b2 = store.http_nodes(root, {"session": FIXTURE_SESSION}, **kw)
        if code != 304 or b2 is not None or "X-Spectate-Server-Now" not in h2:
            errs.append(f"http: {label} did not yield a bodyless 304 with server-now")
    spec = root / ".ravenclaude/runs" / FIXTURE_SESSION / "spectate-events.jsonl"
    with spec.open("ab") as f:
        f.write(_jsonl([{**demo_rows[-1], "ts": "2026-10-09T12:00:09.000Z"}]))
    code, h3, _ = store.http_nodes(root, {"session": FIXTURE_SESSION}, if_none_match=etag)
    if code != 200 or h3.get("ETag") == etag:
        errs.append("http: ETag did not change after the stream grew")
    spec.write_bytes(_jsonl(demo_rows))

    # Cursor pagination covers every event exactly once; a partial last line is skipped.
    got: list[dict] = []
    cursor = None
    for _ in range(50):
        q = {"session": FIXTURE_SESSION, "limit": "3"}
        if cursor is not None:
            q["cursor"] = cursor
        code, _, page = store.http_events(root, q)
        if code != 200:
            errs.append(f"http: events page → {code}")
            break
        got.extend(page["events"])
        if not page["events"]:
            break
        cursor = page["next_cursor"]
    want("paged event count", len(got), len(demo_rows))
    with spec.open("ab") as f:
        f.write(b'{"schema":"rc.spectate.v1","ts":')
    code, _, page = store.http_events(root, {"session": FIXTURE_SESSION})
    want("partial trailing line ignored", (code, len(page["events"])), (200, len(demo_rows)))
    code, _, page = store.http_events(root, {"session": FIXTURE_SESSION, "cursor": "999999999"})
    if code != 200 or page.get("cursor_reset") is not True:
        errs.append("http: a cursor past EOF did not reset")
    spec.write_bytes(b'garbage\n{"prompt":"x"}\n' + _jsonl(demo_rows))
    code, _, page = store.http_events(root, {"session": FIXTURE_SESSION})
    want(
        "malformed + sensitive lines skipped",
        (len(page["events"]), page["skipped_malformed"]),
        (len(demo_rows), 2),
    )
    spec.write_bytes(_jsonl(demo_rows))

    # Symlinked stream file and symlinked session dir must not be followed.
    secret_dir = root / "outside"
    secret_dir.mkdir()
    (secret_dir / "spectate-events.jsonl").write_bytes(_jsonl(demo_rows))
    link_dir = root / ".ravenclaude/runs/linkedrun1"
    link_dir.mkdir()
    os.symlink(secret_dir / "spectate-events.jsonl", link_dir / "spectate-events.jsonl")
    os.symlink(secret_dir, root / ".ravenclaude/runs/linkedrun2")
    for sid in ("linkedrun1", "linkedrun2"):
        code, _, body = store.http_nodes(root, {"session": sid})
        if code == 200:
            errs.append(f"http: symlinked {sid} was served")

    # 5 MiB tail window: a larger stream is truncated, never fully read.
    template = {**demo_rows[2], "session_id": "bigstream1"}
    first = {**demo_rows[0], "session_id": "bigstream1"}
    per_line = len(_jsonl([{**template, "node_id": "bulk-00000", "corr_id": "c-00000"}]))
    total = store.TAIL_BYTES // per_line + 5000
    bulk = b"".join(
        _jsonl([{**template, "node_id": f"bulk-{i:05d}", "corr_id": f"c-{i:05d}"}])
        for i in range(total)
    )
    _mk_run(root, "bigstream1", _jsonl([first]) + bulk)
    code, _, page = store.http_events(root, {"session": "bigstream1", "limit": "5"})
    if code != 200 or page.get("truncated") is not True:
        errs.append("http: oversized stream was not reported truncated")
    code, _, nbody = store.http_nodes(root, {"session": "bigstream1"})
    if code != 200 or nbody["nodes_truncated"] is not True or len(nbody["nodes"]) > store.MAX_NODES:
        errs.append("http: 2000-node cap not enforced on a bulk stream")

    code, _, body = store.http_sessions(root, {"limit": "200"})
    ids = [s["session_id"] for s in body.get("sessions", [])]
    if "linkedrun2" in ids or FIXTURE_SESSION not in ids:
        errs.append(f"http: sessions listing wrong: {ids}")
    for s in body.get("sessions", []):
        if "has_stream" not in s:
            errs.append("http: session item lacks has_stream")
            break
    return errs


def check_store(store, demo) -> list[str]:
    errs = check_golden(store)
    with tempfile.TemporaryDirectory() as d:
        errs.extend(check_gallery(store, demo, Path(d)))
    with tempfile.TemporaryDirectory() as d:
        errs.extend(check_http(store, Path(d)))
    return errs


# ── driver ───────────────────────────────────────────────────────────────────────────


def get_jsonschema_validator(schema: dict):
    try:
        import jsonschema  # type: ignore
    except ImportError:
        print(
            "check-spectate: jsonschema not installed — LOUD SKIP of jsonschema/store parity "
            "(NOT a pass for that section; the store interpreter still validated everything)",
            file=sys.stderr,
        )
        return None
    validator = jsonschema.Draft202012Validator(schema)
    return lambda inst: [e.message for e in validator.iter_errors(inst)]


def run_check() -> int:
    missing = unwired()
    if missing:
        print(f"check-spectate: UNWIRED — missing {missing}", file=sys.stderr)
        return TEETH_EXIT
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    store = _load(STORE, "spectate_store")
    demo = _load(DEMO, "spectate_demo")
    errs = check_schema(schema)
    errs += check_fixtures(store, get_jsonschema_validator(schema))
    errs += check_capabilities()
    errs += check_store(store, demo)
    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"check-spectate: {len(errs)} failure(s)", file=sys.stderr)
        return 1
    print("check-spectate: OK")
    return 0


def run_must_fail() -> int:
    """Plant known-bad events; exit TEETH_EXIT only if every one is rejected."""
    if unwired():
        print("must-fail: gate is unwired — cannot prove teeth", file=sys.stderr)
        return 1
    store = _load(STORE, "spectate_store")
    base = read_jsonl(FIXTURES / "demo-session.jsonl")[2]
    canaries = {
        "raw prompt": {**base, "prompt": "leak"},
        "nested args": {**base, "tool": {**base["tool"], "args": {"command": "rm -rf /"}}},
        "secret target": {**base, "tool": {**base["tool"], "target": "ghp_" + "a" * 36}},
        "bad status": {**base, "asserted_status": "not-a-status"},
        "traversal": {**base, "session_id": "../etc"},
        "extra root key": {**copy.deepcopy(base), "unexpected": 1},
    }
    survivors = [k for k, row in canaries.items() if not store.check_event(row)]
    if survivors:
        print(f"must-fail: canaries accepted — teeth missing: {survivors}", file=sys.stderr)
        return 0
    print(f"must-fail: all {len(canaries)} planted canaries rejected (teeth exit {TEETH_EXIT})")
    return TEETH_EXIT


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--check", action="store_true", help="run all checks (default)")
    p.add_argument("--must-fail", action="store_true", help="plant canaries; exit 3 if rejected")
    p.add_argument(
        "--must-fail-convention",
        action="store_true",
        help="print the teeth exit code for audit-gates.sh rc_mustfail",
    )
    args = p.parse_args()
    if args.must_fail_convention:
        print(f"must-fail-teeth-exit: {TEETH_EXIT}")
        return 0
    if args.must_fail:
        return run_must_fail()
    return run_check()


if __name__ == "__main__":
    sys.exit(main())
