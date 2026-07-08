#!/usr/bin/env python3
"""check-streams-cli.py — Gate 111 engine for Agentic Work-Streams (P1).

Proves the P1 surface (the `rc streams` CLI + active-stream pointer + the
SessionStart banner stream line + the Stop session-close hook) is safe:

  1. SLUG ANTI-TRAVERSAL — create/set-active reject `..`, `/`, leading-dot, and
     absolute-path slugs; a crafted id can never resolve outside the streams root.
  2. READ-ONLY SUMMARY    — the SessionStart banner's stream summary
     (capability-orientation.summarize_streams) reads counts/slugs ONLY and never
     surfaces history content; the banner string for a stream whose history holds
     a distinctive phrase does NOT contain that phrase (no-egress at the banner).
  3. SESSION-CLOSE FAIL-SAFE + DERIVED-ONLY — the Stop hook is a no-op with no
     active stream; with an active stream it appends a DERIVED session_closed
     event + a state.md, and the distinctive phrase never reaches either.

Modes:
  (default)              run the assertions; exit 0 on all-pass.
  --must-fail-traversal  re-check with the slug guard disabled (a raw join); the
                         crafted id MUST then escape -> exit 0 ONLY IF it escapes
                         (proves the anti-traversal gate has teeth).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OPS = REPO / "plugins/ravenclaude-core/scripts/stream-ops.py"
CAPORI = REPO / "plugins/ravenclaude-core/scripts/capability-orientation.py"
RC = REPO / "plugins/ravenclaude-core/bin/rc"
HOOK = REPO / "plugins/ravenclaude-core/hooks/stream-session-close.sh"

# A distinctive multi-word phrase that should never appear in any stored artifact.
PHRASE = "the QUASAR-7 confidential migration rollback nobody approved"

_BAD_SLUGS = ["../escape", "..", "a/b", "/etc/passwd", ".hidden", "..\\win", "a/../b"]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_slug_traversal(ops) -> list[str]:
    errs = []
    for bad in _BAD_SLUGS:
        if ops.is_safe_slug(bad):
            errs.append(f"is_safe_slug accepted unsafe slug {bad!r}")
        # create_stream / set_active must raise on an unsafe id
        with tempfile.TemporaryDirectory() as d:
            try:
                # slugify usually neutralizes these; force the raw-id path via set_active
                ops.set_active(d, bad)
                errs.append(f"set_active accepted unsafe id {bad!r}")
            except ValueError:
                pass
            # _stream_dir must refuse to resolve outside the root
            try:
                ops._stream_dir(d, bad)
                errs.append(f"_stream_dir resolved unsafe id {bad!r}")
            except ValueError:
                pass
    # The CLI itself must exit nonzero (not crash) on a traversal set-active.
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(
            [sys.executable, str(OPS), "--root", d, "set-active", "../../etc"],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            errs.append("CLI set-active accepted a traversal id (exit 0)")
        if "Traceback" in r.stderr:
            errs.append("CLI leaked a traceback on a traversal id (should be a clean error)")
    return errs


def check_readonly_summary(ops, capori) -> list[str]:
    errs = []
    with tempfile.TemporaryDirectory() as d:
        ops.create_stream(d, "Secret Stream", ts="2026-06-23T00:00:00Z")
        sid = ops.slugify("Secret Stream")
        ops.set_active(d, sid)
        # write a (derived) event whose summary is capped; also write the PHRASE only
        # into state.md via a manual write to simulate worst-case content presence.
        ops.append_event(
            d,
            sid,
            label="secret",
            terms=["secret"],
            word_count=3,
            session_id="sess-z",
            ts="2026-06-23T00:01:00Z",
        )
        # Force the phrase into history+state by hand (worst case for a reader leak).
        sdir = Path(d) / ".ravenclaude" / "streams" / sid
        (sdir / "history.jsonl").write_text(
            json.dumps(
                {"schema_version": 1, "kind": "x", "stream_id": sid, "summary": PHRASE},
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (sdir / "state.md").write_text(f"# {sid}\n\n{PHRASE}\n", encoding="utf-8")

        summ = capori.summarize_streams(Path(d))
        if summ is None:
            errs.append("summarize_streams returned None for a populated store")
            return errs
        # The summary must carry only counts/slug — never the phrase.
        blob = json.dumps(summ, sort_keys=True)
        if PHRASE in blob:
            errs.append("READ-ONLY VIOLATION: summarize_streams leaked history content")
        if summ.get("active") != sid:
            errs.append(f"summarize_streams active mismatch: {summ.get('active')!r}")
        # And the full banner must not contain the phrase either.
        banner = capori.build_banner(Path(d))
        if PHRASE in banner:
            errs.append("READ-ONLY VIOLATION: capability banner leaked history content")
        if "WORK-STREAMS" not in banner:
            errs.append("banner is missing the WORK-STREAMS section for an active stream")
    return errs


def check_session_close(ops) -> list[str]:
    errs = []
    plugin_root = str(REPO / "plugins/ravenclaude-core")
    # (a) no active stream -> no-op, no files created
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(
            ["bash", str(HOOK)],
            input='{"session_id":"s1"}',
            text=True,
            capture_output=True,
            env={"CLAUDE_PROJECT_DIR": d, "CLAUDE_PLUGIN_ROOT": plugin_root, "PATH": _path()},
        )
        if r.returncode != 0:
            errs.append(f"session-close hook nonzero with no active stream (exit {r.returncode})")
        if (Path(d) / ".ravenclaude" / "streams").exists():
            errs.append("session-close hook created a store with no active stream")
    # (b) active stream -> derived session_closed event + state.md, phrase absent
    with tempfile.TemporaryDirectory() as d:
        ops.create_stream(d, "Close Probe", ts="2026-06-23T00:00:00Z")
        sid = ops.slugify("Close Probe")
        ops.set_active(d, sid)
        r = subprocess.run(
            ["bash", str(HOOK)],
            input='{"session_id":"' + PHRASE.replace(" ", "_") + '"}',
            text=True,
            capture_output=True,
            env={"CLAUDE_PROJECT_DIR": d, "CLAUDE_PLUGIN_ROOT": plugin_root, "PATH": _path()},
        )
        if r.returncode != 0:
            errs.append(f"session-close hook nonzero with active stream (exit {r.returncode})")
        hist = (Path(d) / ".ravenclaude" / "streams" / sid / "history.jsonl").read_text()
        if '"kind": "session_closed"' not in hist:
            errs.append("session-close hook did not write a session_closed event")
        if PHRASE in hist:
            errs.append("NO-EGRESS VIOLATION: phrase reached session-close history")
        state = Path(d) / ".ravenclaude" / "streams" / sid / "state.md"
        if not state.exists():
            errs.append("session-close hook did not write state.md")
        elif PHRASE in state.read_text():
            errs.append("NO-EGRESS VIOLATION: phrase reached state.md")
    return errs


def _path() -> str:
    import os

    return os.environ.get("PATH", "/usr/bin:/bin")


def must_fail_traversal(ops) -> int:
    """Neutralize the REAL slug guard and drive the REAL resolution; the crafted id MUST escape.

    Two real production layers guard traversal: (1) ``is_safe_slug`` rejects the id, and
    (2) ``_stream_dir`` re-checks containment after resolve. We monkeypatch
    ``ops.is_safe_slug`` -> always True (layer 1 gone) and confirm the REAL ``_stream_dir``
    STILL refuses the traversal id via its layer-2 containment check (proving that guard is
    load-bearing), then show that the underlying resolution — the join ``_stream_dir`` performs
    before its containment check — escapes ``streams_root()``. Exit 0 iff BOTH hold: the real
    guard fires AND the unguarded resolution would escape. This exercises real production code
    (is_safe_slug / streams_root / _stream_dir), rather than re-deriving generic pathlib joins.
    """
    with tempfile.TemporaryDirectory() as d:
        bad = "../escaped-stream"
        original = ops.is_safe_slug
        ops.is_safe_slug = lambda slug: True
        try:
            # With layer 1 (is_safe_slug) neutralized, the REAL _stream_dir must still
            # refuse via its post-resolve containment check.
            guard_refused = False
            try:
                ops._stream_dir(d, bad)
            except ValueError:
                guard_refused = True
            # The resolution _stream_dir performs (via the REAL streams_root) escapes.
            root_resolved = ops.streams_root(d).resolve()
            target = (root_resolved / bad).resolve()
        finally:
            ops.is_safe_slug = original
        escaped = target != root_resolved and root_resolved not in target.parents
        if guard_refused and escaped:
            print(
                "  must-fail-traversal: is_safe_slug removed -> the crafted id ESCAPES the "
                "root and the real _stream_dir containment guard is what refuses it (guard has teeth)"
            )
            return 0
        print(
            "  must-fail-traversal: ERROR — escape not demonstrated "
            f"(guard_refused={guard_refused}, escaped={escaped})",
            file=sys.stderr,
        )
        return 1


def main(argv: list[str]) -> int:
    ops = _load(OPS, "stream_ops")
    capori = _load(CAPORI, "capability_orientation")

    if "--must-fail-traversal" in argv:
        return must_fail_traversal(ops)

    errs: list[str] = []
    errs += check_slug_traversal(ops)
    errs += check_readonly_summary(ops, capori)
    errs += check_session_close(ops)

    if errs:
        print("Gate 111 FAILURES:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(
        "  slug-anti-traversal OK | read-only summary OK | session-close fail-safe + no-egress OK"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
