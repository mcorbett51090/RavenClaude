#!/usr/bin/env python3
"""test-spectate-store-review.py — repo-review 2026-10-19 fixes in spectate_store.py.

  secret   SECRET_SPEC R-set: benign kebab text is not a secret; ghu_ app tokens,
           AWS ASIA keys and PEM bodies are (corescripts-1 / hooks-13).
  1b-4     list_sessions ranks on cheap per-session facts, pages, then reduces ONLY
           the page; the result is identical to reducing every session; the reduce
           cache evicts least-recently-used entries instead of clearing at 256.
  1b-7     iter_new_spectate_lines (SSE replay) never reads more than TAIL_BYTES,
           even for Last-Event-ID 0 on a large stream.
  1b-8     apply_steer validates agent_id with fullmatch ("main\\n" -> "main"), and a
           failed event append leaves no steer state persisted.

Run standalone: python3 test-spectate-store-review.py [path/to/spectate_store.py]
(the optional path lets the same assertions run against another copy, e.g. the
pre-fix module, to show they fail there).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SRC = HERE.parent.parent / "scripts" / "spectate_store.py"

_fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print("  %s %s%s" % ("ok  " if cond else "FAIL", name, "" if cond else " — " + detail))
    if not cond:
        _fails.append(name)


def load(path: Path):
    spec = importlib.util.spec_from_file_location("spectate_store_review", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row(sid: str, i: int, kind: str = "tool.pre", synthetic: bool = False, **extra) -> dict:
    ev = {
        "schema": "rc.spectate.v1",
        "ts": "2026-10-19T10:%02d:%02d.000Z" % ((i // 60) % 60, i % 60),
        "session_id": sid,
        "harness": "claude-code",
        "source": "hook",
        "kind": kind,
        "agent_id": "main",
        "detail": "minimal",
        "node_id": "n-%d" % i,
    }
    if synthetic:
        ev["synthetic"] = True
    ev.update(extra)
    return ev


def write_session(
    store,
    root: Path,
    sid: str,
    rows: list[dict] | None,
    meta: dict | None = None,
    hook_only: bool = False,
    mtime: float | None = None,
) -> Path:
    d = root / ".ravenclaude" / "runs" / sid
    d.mkdir(parents=True, exist_ok=True)
    if hook_only:
        (d / store.HOOK_FILE).write_text('{"verdict":"warn"}\n', encoding="utf-8")
    if rows is not None:
        body = "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows)
        (d / store.SPECTATE_FILE).write_text(body, encoding="utf-8")
    if meta is not None:
        (d / store.META_FILE).write_text(json.dumps(meta), encoding="utf-8")
    if mtime is not None:
        for f in d.iterdir():
            os.utime(f, (mtime, mtime))
    return d


def test_secrets(store) -> None:
    print("== secret patterns ==")
    kebab = "Refactor the task-management-and-planning module"
    check("benign kebab-case text is not a secret", not store.secret_hit(kebab))
    check("a ghu_ app token is a secret", store.secret_hit("gh" + "u_" + "E" * 36))
    check("an AWS ASIA key is a secret", store.secret_hit("AS" + "IA" + "IOSFODNN7EXAMPLE"))
    check(
        "a real sk- key after '=' is still a secret",
        store.secret_hit("key=sk-" + "ant-" + "a1b2c3d4e5f6g7h8i9j0k1"),
    )


def test_list_sessions(store) -> None:
    print("== list_sessions: page before reduce ==")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        base = 1_760_000_000.0
        for i in range(300):
            sid = "s%03d" % i
            if i % 50 == 7:
                write_session(store, root, sid, None, hook_only=True, mtime=base + i)
                continue
            synth_first = i % 37 == 3
            rows = [row(sid, 0, "prompt.submit", synthetic=synth_first, node_id="prompt")]
            rows += [row(sid, k) for k in range(1, 4)]
            meta = {"synthetic": True} if i % 41 == 5 else None
            write_session(store, root, sid, rows, meta=meta, mtime=base + (i * 7919) % 300)

        calls = {"n": 0}
        real = store._load_reduced

        def counting(*a, **k):
            calls["n"] += 1
            return real(*a, **k)

        store._REDUCE_CACHE.clear()
        store._load_reduced = counting
        try:
            page = store.list_sessions(root, cursor=0, limit=50)
            first_page_calls = calls["n"]
        finally:
            store._load_reduced = real
        check(
            "a 50-item page over 300 sessions reduces at most 50 streams",
            first_page_calls <= 50,
            "reduced %d" % first_page_calls,
        )

        # Reference: reduce EVERY session, rank, page — the pre-change semantics.
        caps = store.load_capabilities()
        caps_mtime = store.capabilities_mtime_ns()
        ref = []
        for i in range(300):
            it = store._session_item(root, "s%03d" % i, caps, caps_mtime)
            if it is not None:
                ref.append(it)
        ref.sort(
            key=lambda it: (
                2 if it["synthetic"] else (0 if it["has_stream"] else 1),
                -it["mtime"],
                it["session_id"],
            )
        )
        got_all = []
        cur = 0
        while True:
            body = store.list_sessions(root, cursor=cur, limit=50)
            got_all.extend(body["sessions"])
            if body["next_cursor"] is None:
                break
            cur = int(body["next_cursor"])
        check(
            "paging the cheap ranking yields exactly the fully-reduced ranking",
            got_all == ref,
            "first diff at %s"
            % next((i for i, (a, b) in enumerate(zip(got_all, ref)) if a != b), len(got_all)),
        )
        check("the first page equals the reference first page", page["sessions"] == ref[:50])
        filtered = store.list_sessions(root, cursor=0, limit=200, harness="claude-code")
        want = [r for r in ref if r["harness"] == "claude-code"][:200]
        check(
            "the harness filter still applies (same items as filtering the full ranking)",
            filtered["sessions"] == want,
            "%d vs %d" % (len(filtered["sessions"]), len(want)),
        )

    print("== reduce cache is LRU, not clear-all ==")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for i in range(5):
            write_session(store, root, "c%d" % i, [row("c%d" % i, k) for k in range(3)])
        saved_max = store._REDUCE_CACHE_MAX
        store._REDUCE_CACHE.clear()
        store._REDUCE_CACHE_MAX = 4
        caps = store.load_capabilities()
        caps_mtime = store.capabilities_mtime_ns()
        try:
            for name in ("c0", "c1", "c2", "c3", "c0", "c4"):
                store._session_item(root, name, caps, caps_mtime)
            paths = {Path(k[0]).name for k in store._REDUCE_CACHE}
        finally:
            store._REDUCE_CACHE_MAX = saved_max
            store._REDUCE_CACHE.clear()
        check("cache stays within its bound", len(paths) <= 4, str(paths))
        check(
            "the recently used entry survives and the least recently used is evicted",
            "c0" in paths and "c4" in paths and "c1" not in paths,
            str(sorted(paths)),
        )


def test_sse_tail(store) -> None:
    print("== SSE replay is clamped to the tail window ==")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        rows = [
            row("big", i, tool={"name": "Read", "family": "path", "target": "x" * 200})
            for i in range(1500)
        ]
        d = write_session(store, root, "big", rows)
        size = (d / store.SPECTATE_FILE).stat().st_size
        saved_tail = store.TAIL_BYTES
        store.TAIL_BYTES = 64 * 1024
        read = {"bytes": 0}
        real = store._pread_all

        def counting(fd, offset, length):
            read["bytes"] += length
            return real(fd, offset, length)

        store._pread_all = counting
        try:
            st, out, _nxt = store.iter_new_spectate_lines(root, "big", 0)
        finally:
            store._pread_all = real
            tail = store.TAIL_BYTES
            store.TAIL_BYTES = saved_tail
        check("fixture stream is larger than the tail window", size > 2 * tail, str(size))
        check(
            "Last-Event-ID 0 reads at most TAIL_BYTES (+1 lead byte)",
            st == "ok" and read["bytes"] <= tail + 1,
            "read %d of %d" % (read["bytes"], size),
        )
        check(
            "and still returns the newest events",
            bool(out) and out[-1][1] == size and out[0][1] >= size - tail,
        )


def test_steer(store) -> None:
    print("== apply_steer: fullmatch agent_id, no state on a failed append ==")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".ravenclaude").mkdir()
        (root / ".ravenclaude" / "comfort-posture.yaml").write_text("spectate_steer: on\n")
        write_session(store, root, "st1", [row("st1", 0, "prompt.submit", node_id="prompt")])
        write_session(store, root, "st2", [row("st2", 0, "prompt.submit", node_id="prompt")])

        code, body = store.apply_steer(root, session_id="st1", action="pause", agent_id="main\n")
        check(
            "agent_id 'main\\n' is not used verbatim: the steer is recorded as 'main'",
            code == 200 and body.get("event", {}).get("agent_id") == "main",
            "%s %s" % (code, body),
        )

        real_append = store.append_spectate_event
        store.append_spectate_event = lambda *_a, **_k: (False, "open_failed")
        try:
            code, body = store.apply_steer(root, session_id="st2", action="pause")
        finally:
            store.append_spectate_event = real_append
        check("a failed append returns 500", code == 500, "%s %s" % (code, body))
        check(
            "and no pause state persists",
            store.read_steer_pending(root, "st2") is None,
            str(store.read_steer_pending(root, "st2")),
        )

        ok_code, _ = store.apply_steer(root, session_id="st2", action="note", note="keep me")
        before = store.read_steer_pending(root, "st2")
        store.append_spectate_event = lambda *_a, **_k: (False, "open_failed")
        try:
            store.apply_steer(root, session_id="st2", action="pause")
        finally:
            store.append_spectate_event = real_append
        check(
            "a failed append restores the previous steer state",
            ok_code == 200 and store.read_steer_pending(root, "st2") == before,
        )


def main(argv: list[str]) -> int:
    src = Path(argv[1]) if len(argv) > 1 else DEFAULT_SRC
    store = load(src)
    test_secrets(store)
    test_list_sessions(store)
    test_sse_tail(store)
    test_steer(store)
    if _fails:
        print("FAIL: test-spectate-store-review.py (%d failing)" % len(_fails))
        return 1
    print("PASS: test-spectate-store-review.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
