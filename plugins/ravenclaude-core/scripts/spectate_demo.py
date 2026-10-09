#!/usr/bin/env python3
"""spectate_demo.py — write the synthetic Spectate gallery (CLI write path only).

One run directory per harness, ``.ravenclaude/runs/demo-<harness>/``, each holding a
``meta.json`` provenance stamp (``synthetic: true``) and a single-harness
``spectate-events.jsonl`` (G4-2: one harness per stream). Together the eight streams cover
all 11 reducer statuses, and ``grok-bot`` / ``grok-build`` show capability-unknown, never a
false ``unavailable-harness`` (G9-11).

``unavailable-harness`` needs an ``unsupported`` capability cell and the atlas has none, so
``demo-copilot-vscode`` carries ``capability_overrides`` in its ``meta.json``. The store only
honours that key on sessions stamped ``synthetic: true``.

Re-running overwrites the three files in each ``demo-<harness>`` directory (idempotent);
nothing else under ``.ravenclaude/runs/`` is touched.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import spectate_store as store  # noqa: E402

HARNESSES = store.HARNESSES
STEP_MS = 400


class _Stream:
    def __init__(self, harness: str, session_id: str, base: datetime):
        self.harness = harness
        self.session_id = session_id
        self.base = base
        self.i = 0
        self.events: list[dict] = []
        self.hooks: list[dict] = []

    def _ts(self) -> str:
        t = self.base + timedelta(milliseconds=STEP_MS * self.i)
        self.i += 1
        return store.now_rfc3339(t)

    def add(self, kind: str, node_id: str | None = None, **fields) -> dict:
        ev: dict = {
            "schema": "rc.spectate.v1",
            "ts": self._ts(),
            "session_id": self.session_id,
            "harness": self.harness,
            "source": "demo",
            "kind": kind,
            "agent_id": fields.pop("agent_id", "main"),
            "synthetic": True,
            "detail": "minimal",
        }
        if node_id:
            ev["node_id"] = node_id
        ev.update({k: v for k, v in fields.items() if v is not None})
        self.events.append(ev)
        return ev

    def tool(self, node_id, name, family, target=None, **kw) -> dict:
        t: dict = {"name": name, "family": family}
        if target:
            t["target"] = target
        return self.add("tool.pre", node_id, tool=t, step="execute-tools", **kw)

    def end(self, node_id, kind="tool.post", **kw) -> dict:
        return self.add(kind, node_id, step="execute-tools", **kw)


def _start(s: _Stream) -> None:
    s.add("session.start", "session")
    s.add("prompt.submit", "prompt-0", step="assemble", metrics={"prompt_chars": 118})


def _claude_code(s: _Stream) -> dict:
    _start(s)
    s.tool("read-1", "Read", "path", "plugins/ravenclaude-core/CLAUDE.md", corr_id="c-read")
    s.end("read-1", corr_id="c-read", metrics={"duration_ms": 14, "out_bytes": 4096})
    s.tool("edit-1", "Edit", "path", "src/app.ts", corr_id="c-edit")
    s.end("edit-1", "tool.fail", corr_id="c-edit", metrics={"duration_ms": 31})
    s.tool("rm-1", "Bash", "shell", "rm", corr_id="c-rm")
    s.end("rm-1", corr_id="c-rm", asserted_status="succeeded")
    s.hooks += [
        {"ts": s.events[-1]["ts"], "hook": "guard-destructive.sh", "verdict": "warn", "rule": "x"},
        {
            "schema_version": 1,
            "ts": s.events[-2]["ts"],
            "hook": "guard-destructive.sh",
            "verdict": "deny",
            "tool": "Bash",
            "path": "rm -rf ./build",
            "rule": "rm-recursive",
            "session_id": s.session_id,
            "exit_code": 2,
            "corr_id": "c-rm",
        },
    ]
    s.add("turn.end", "turn-0")
    s.add("session.end", "session")
    return {}


def _codex_cli(s: _Stream) -> dict:
    _start(s)
    s.tool("build-1", "Bash", "shell", "make", corr_id="c-build")
    s.tool("push-1", "Bash", "shell", "git", corr_id="c-push")
    s.add("permission.request", "push-1", step="execute-tools", corr_id="c-push")
    s.add("subagent.start", "sub-a", step="execute-tools", corr_id="c-sub")
    s.tool("sub-read", "Read", "path", "docs/README.md", agent_id="sub-a")
    s.end("sub-read", agent_id="sub-a", metrics={"duration_ms": 9})
    s.tool("sub-grep", "Grep", "other", agent_id="sub-a")
    return {}


def _copilot_cli(s: _Stream) -> dict:
    _start(s)
    s.tool("curl-1", "WebFetch", "url", "https://example.com", corr_id="c-curl")
    s.add("permission.request", "curl-1", step="execute-tools", corr_id="c-curl")
    s.add(
        "permission.resolve",
        "curl-1",
        step="execute-tools",
        corr_id="c-curl",
        deny={"by": "user", "source": "permission-prompt", "rule": "user-declined"},
    )
    s.tool("ls-1", "Bash", "shell", "ls", corr_id="c-ls")
    s.end("ls-1", corr_id="c-ls", metrics={"duration_ms": 6})
    s.add("turn.end", "turn-0")
    s.add("session.end", "session")
    return {}


def _copilot_vscode(s: _Stream) -> dict:
    _start(s)
    s.tool("term-1", "RunInTerminal", "shell", "npm", corr_id="c-term")
    s.end(
        "term-1",
        "tool.fail",
        corr_id="c-term",
        deny={"by": "harness", "source": "workspace-trust", "rule": "untrusted-workspace"},
    )
    s.add("turn.end", "turn-0")
    s.add("prompt.submit", "prompt-1", step="assemble")
    s.tool("edit-2", "ApplyPatch", "path", "src/index.ts", corr_id="c-patch")
    s.end("edit-2", corr_id="c-patch", metrics={"duration_ms": 22})
    s.add("turn.end", "turn-1")
    s.add("session.end", "session")
    return {"capability_overrides": {"compact": "unsupported"}}


def _cursor(s: _Stream) -> dict:
    _start(s)
    s.tool("fetch-1", "WebFetch", "url", "https://internal.example.com", corr_id="c-fetch")
    s.end(
        "fetch-1",
        "tool.fail",
        corr_id="c-fetch",
        deny={"by": "org", "source": "managed-policy", "rule": "block-external"},
    )
    s.add("subagent.start", "sub-b", step="execute-tools")
    s.tool("sub-edit", "Edit", "path", "src/lib.ts", agent_id="sub-b")
    s.end("sub-edit", agent_id="sub-b", metrics={"duration_ms": 40})
    s.add("subagent.stop", "sub-b", step="execute-tools")
    s.add("turn.end", "turn-0")
    s.add("prompt.submit", "prompt-1", step="assemble")
    s.add("compact.pre", "compact-1", step="update-context")
    s.add("turn.end", "turn-1")
    s.add("session.end", "session")
    return {}


def _gemini_cli(s: _Stream) -> dict:
    _start(s)
    s.tool("read-g", "read_file", "path", "README.md", corr_id="g-read")
    s.end("read-g", corr_id="g-read", metrics={"duration_ms": 8})
    s.tool("shell-g", "run_shell_command", "shell", "pytest", corr_id="g-test")
    s.end("shell-g", "tool.fail", corr_id="g-test", metrics={"duration_ms": 950})
    s.tool("shell-g2", "run_shell_command", "shell", "pytest", corr_id="g-test2")
    s.end("shell-g2", corr_id="g-test2", metrics={"duration_ms": 910})
    s.add("turn.end", "turn-0")
    s.add("session.end", "session")
    return {}


def _grok_build(s: _Stream) -> dict:
    _start(s)
    s.tool("ok-1", "Read", "path", "notes.md", corr_id="gb-read")
    s.end("ok-1", corr_id="gb-read")
    return {}


def _grok_bot(s: _Stream) -> dict:
    s.add("session.start", "session")
    return {}


SCENARIOS = {
    "claude-code": _claude_code,
    "codex-cli": _codex_cli,
    "copilot-cli": _copilot_cli,
    "copilot-vscode": _copilot_vscode,
    "cursor": _cursor,
    "gemini-cli": _gemini_cli,
    "grok-build": _grok_build,
    "grok-bot": _grok_bot,
}


def build_session(harness: str, session_id: str, base: datetime) -> dict:
    """→ ``{"events": [...], "hooks": [...], "meta_extra": {...}}`` for one harness."""
    s = _Stream(harness, session_id, base)
    meta_extra = SCENARIOS[harness](s)
    return {"events": s.events, "hooks": s.hooks, "meta_extra": meta_extra}


def _atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(r, separators=(",", ":"), ensure_ascii=True) + "\n" for r in rows)


def write_demo(
    project_root: Path | str,
    harnesses: list[str] | None = None,
    *,
    now: datetime | None = None,
) -> list[str]:
    """Write ``demo-<harness>`` run dirs (overwrite-on-rerun). → session ids written."""
    runs = store.runs_root(project_root)
    runs.mkdir(parents=True, exist_ok=True)
    created = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    written: list[str] = []
    for harness in harnesses or list(HARNESSES):
        if harness not in SCENARIOS:
            raise ValueError(f"unknown harness {harness!r}")
        sid = f"demo-{harness}"
        run_dir = runs / sid
        if run_dir.is_symlink():
            raise OSError(f"refusing to write through symlink: {run_dir}")
        run_dir.mkdir(exist_ok=True)
        # The last event lands a few seconds before `created`, so a freshly written demo
        # reads as just-finished rather than from the future.
        base = created - timedelta(seconds=30)
        built = build_session(harness, sid, base)
        for ev in built["events"]:
            bad = store.check_event(ev)
            if bad:
                raise ValueError(f"{sid}: demo event fails the schema: {bad}")
        meta = {
            "task_id": sid,
            "cli": "spectate_demo.py",
            "host": "rc",
            "created_at": store.now_rfc3339(created),
            "synthetic": True,
            "harness": harness,
            **built["meta_extra"],
        }
        _atomic_write(run_dir / store.META_FILE, json.dumps(meta, indent=2) + "\n")
        _atomic_write(run_dir / store.SPECTATE_FILE, _jsonl(built["events"]))
        hook_path = run_dir / store.HOOK_FILE
        if built["hooks"]:
            _atomic_write(hook_path, _jsonl(built["hooks"]))
        else:
            try:
                hook_path.unlink()
            except FileNotFoundError:
                pass
        written.append(sid)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".", help="project containing .ravenclaude/runs")
    ap.add_argument(
        "--harness",
        action="append",
        choices=sorted(SCENARIOS),
        help="limit to one harness (repeatable); default all eight",
    )
    args = ap.parse_args(argv)
    ids = write_demo(Path(args.project_root), args.harness)
    root = store.runs_root(args.project_root)
    print(f"spectate_demo: wrote {len(ids)} synthetic session(s) under {root}")
    for sid in ids:
        print(f"  {sid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
