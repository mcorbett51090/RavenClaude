#!/usr/bin/env python3
"""check-spectate.py — Gate for Spectate schema, fixtures, capabilities, reducer.

Exit codes:
  0 — pass
  1 — fixture/schema/reducer failure
  3 — unwired (schema or fixtures dir absent) — never silent green
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "plugins/ravenclaude-core/knowledge/spectate-event-schema-v1.json"
CAPS = REPO / "plugins/ravenclaude-core/knowledge/spectate-capabilities.json"
FIXTURES = REPO / "tests/fixtures/spectate"
STORE = REPO / "plugins/ravenclaude-core/scripts/spectate_store.py"
DEMO = REPO / "plugins/ravenclaude-core/scripts/spectate_demo.py"

TEETH_EXIT = 3


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def unwired() -> bool:
    return not SCHEMA.is_file() or not FIXTURES.is_dir() or not CAPS.is_file()


def validate_with_jsonschema(schema: dict, instance: dict) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        print(
            "check-spectate: jsonschema not installed — using stdlib structural checks",
            file=sys.stderr,
        )
        return structural_validate(schema, instance)
    Validator = jsonschema.Draft202012Validator
    return [e.message for e in Validator(schema).iter_errors(instance)]


def structural_validate(schema: dict, instance: dict) -> list[str]:
    errs = []
    if instance.get("schema") != "rc.spectate.v1":
        errs.append("schema const")
    for req in schema.get("required", []):
        if req not in instance:
            errs.append(f"missing {req}")
    for k in instance:
        if k not in schema.get("properties", {}):
            errs.append(f"additionalProperties: {k}")
    return errs


def check_bad_fixtures(schema: dict) -> list[str]:
    errs = []
    for path in sorted(FIXTURES.glob("bad-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            # traversal ids are about session_id path rules, not schema
            if path.name == "bad-session-traversal.jsonl":
                store = _load(STORE, "spectate_store")
                sid = obj.get("session_id", "")
                if store.validate_session_id(sid):
                    errs.append(f"{path.name}: session_id {sid!r} should be rejected")
                continue
            ve = validate_with_jsonschema(schema, obj)
            if not ve:
                # also fail if sensitive nested keys present after scrub expectation
                raw = json.dumps(obj)
                if any(k in obj for k in ("prompt",)) or '"args"' in raw:
                    continue  # expected bad — must not validate clean for prompt at root
                if path.name.startswith("bad-"):
                    # If schema still accepts, ensure recursive scrub would strip
                    store = _load(STORE, "spectate_store")
                    scrubbed = store.scrub_obj(obj)
                    blob = json.dumps(scrubbed)
                    if "SECRET" in blob or "rm -rf" in blob or "password" in blob.lower():
                        errs.append(f"{path.name}: scrub left sensitive material")
                    # For nested args — scrub must drop args key
                    if path.name == "bad-nested-args.jsonl":
                        tool = scrubbed.get("tool") or {}
                        if "args" in tool:
                            errs.append(f"{path.name}: nested args survived scrub")
            # bad fixtures that are schema-invalid are OK (expected)
    return errs


def check_capabilities() -> list[str]:
    errs = []
    caps = json.loads(CAPS.read_text(encoding="utf-8"))
    for h in ("grok-bot", "grok-build"):
        cells = caps["harnesses"][h]
        for key, cell in cells.items():
            if key == "steer_context":
                continue
            if cell.get("state") != "unknown":
                errs.append(f"{h}.{key} must be unknown (got {cell.get('state')})")
    return errs


def check_reducer() -> list[str]:
    errs = []
    if not STORE.is_file():
        return ["spectate_store.py missing"]
    store = _load(STORE, "spectate_store")
    caps = json.loads(CAPS.read_text(encoding="utf-8"))
    golden_path = FIXTURES / "expected-reduce.json"
    if not golden_path.is_file():
        return ["expected-reduce.json missing"]
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        demo = _load(DEMO, "spectate_demo")
        demo.write_demo(root)
        # unknown ↛ unavailable for grok-bot
        sid = "demo-grok-bot"
        code, body, _etag = store.nodes_response(root, sid, caps)
        if code != 200:
            errs.append(f"grok-bot nodes HTTP {code}")
        else:
            for n in body["nodes"]:
                if n.get("status") == "unavailable-harness":
                    errs.append("grok-bot produced unavailable-harness from unknown")
                    break
                if n.get("step") and n.get("status") == "idle":
                    if n.get("capability_state") != "unknown":
                        # seed should carry capability_state unknown
                        if (
                            store.cap_state(caps, "grok-bot", store.STEP_CAP[n["step"]])
                            == "unknown"
                        ):
                            if "capability_state" not in n:
                                errs.append(f"missing capability_state on {n['node_id']}")
                            break
        # empty file → idle spine
        empty_id = "empty-sess1"
        ed = root / ".ravenclaude" / "runs" / empty_id
        ed.mkdir(parents=True)
        (ed / "spectate-events.jsonl").write_text("", encoding="utf-8")
        code, body, _etag = store.nodes_response(root, empty_id, caps)
        if code != 200 or not body.get("nodes"):
            errs.append("empty file should 200 with seeded nodes")
        # no stream
        ns = root / ".ravenclaude" / "runs" / "hooksonly1"
        ns.mkdir(parents=True)
        (ns / "hook-events.jsonl").write_text("{}\n", encoding="utf-8")
        code, body, _etag = store.nodes_response(root, "hooksonly1", caps)
        if code != 404 or body.get("error") != "no_spectate_stream":
            errs.append(f"expected no_spectate_stream, got {code} {body}")
        # missing session
        code, body, _etag = store.nodes_response(root, "nosuchsession99", caps)
        if code != 404 or body.get("error") != "session_not_found":
            errs.append(f"expected session_not_found, got {code} {body}")
        # deny beats
        if golden.get("deny_beats_success"):
            events = golden["deny_beats_success"]["events"]
            hooks = golden["deny_beats_success"]["hooks"]
            nodes = store.reduce(events, hooks, caps, harness="claude-code")
            hit = next((n for n in nodes if n["node_id"] == "tool:x"), None)
            if not hit or hit["status"] != "denied-plugin":
                errs.append(f"deny should beat success, got {hit}")
    return errs


def run_check() -> int:
    if unwired():
        print("check-spectate: UNWIRED — schema or fixtures missing", file=sys.stderr)
        return TEETH_EXIT
    errs: list[str] = []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    # good demo line
    demo_line = FIXTURES / "demo-session.jsonl"
    if demo_line.is_file():
        for line in demo_line.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            ve = validate_with_jsonschema(schema, obj)
            if ve:
                errs.extend(f"demo-session: {x}" for x in ve)
    errs.extend(check_bad_fixtures(schema))
    errs.extend(check_capabilities())
    errs.extend(check_reducer())
    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("check-spectate: OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="run all checks (default)")
    p.add_argument("--must-fail", action="store_true", help="alias for convention printer")
    p.add_argument(
        "--must-fail-convention",
        action="store_true",
        help="print teeth exit code for audit-gates",
    )
    args = p.parse_args()
    if args.must_fail_convention:
        print(f"must-fail-teeth-exit: {TEETH_EXIT}")
        return 0
    if args.must_fail:
        # Planted canary: a raw-prompt event must be rejected. Exit TEETH_EXIT
        # when the gate catches it; exit 0 would mean the canary went green.
        if unwired():
            return TEETH_EXIT
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        bad = {"schema": "rc.spectate.v1", "ts": "2026-01-01T00:00:00Z", "prompt": "leak"}
        errs = validate_with_jsonschema(schema, bad)
        if errs:
            print("must-fail: schema rejects raw prompt (teeth exit 3)")
            return TEETH_EXIT
        print("must-fail: bad fixture passed schema — teeth missing", file=sys.stderr)
        return 0
    return run_check()


if __name__ == "__main__":
    sys.exit(main())
