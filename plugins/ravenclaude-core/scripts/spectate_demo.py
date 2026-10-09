#!/usr/bin/env python3
"""spectate_demo.py — write synthetic per-harness Spectate gallery sessions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

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

STATUSES_DEMO = [
    ("tool.pre", "running", "Bash"),
    ("tool.post", "succeeded", "Read"),
    ("tool.fail", "failed", "Edit"),
    ("permission.request", "waiting-approval", "Shell"),
]


def _ts(base: datetime, i: int) -> str:
    t = base + timedelta(seconds=i)
    return t.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def build_events(harness: str, session_id: str, base: datetime) -> list[dict]:
    evs: list[dict] = []
    i = 0
    evs.append(
        {
            "schema": "rc.spectate.v1",
            "ts": _ts(base, i),
            "session_id": session_id,
            "harness": harness,
            "source": "demo",
            "kind": "session.start",
            "node_id": "sess:start",
            "agent_id": "main",
            "synthetic": True,
            "detail": "minimal",
        }
    )
    i += 1
    evs.append(
        {
            "schema": "rc.spectate.v1",
            "ts": _ts(base, i),
            "session_id": session_id,
            "harness": harness,
            "source": "demo",
            "kind": "prompt.submit",
            "step": "assemble",
            "node_id": "prompt:0",
            "agent_id": "main",
            "synthetic": True,
            "detail": "minimal",
        }
    )
    for kind, _status, tool in STATUSES_DEMO:
        i += 1
        nid = f"tool:{tool.lower()}"
        ev: dict = {
            "schema": "rc.spectate.v1",
            "ts": _ts(base, i),
            "session_id": session_id,
            "harness": harness,
            "source": "demo",
            "kind": kind,
            "step": "execute-tools",
            "node_id": nid,
            "parent_id": "step:main:0:execute-tools",
            "agent_id": "main",
            "corr_id": f"corr-{tool.lower()}",
            "tool": {"name": tool, "family": "shell", "target": tool.lower()},
            "synthetic": True,
            "detail": "minimal",
        }
        if kind == "tool.fail":
            ev["asserted_status"] = "failed"
        if kind == "tool.post":
            ev["metrics"] = {"duration_ms": 12}
        evs.append(ev)
        if kind == "tool.pre":
            i += 1
            evs.append(
                {
                    **ev,
                    "ts": _ts(base, i),
                    "kind": "tool.post",
                    "metrics": {"duration_ms": 5},
                }
            )
    # deny-plugin example
    i += 1
    evs.append(
        {
            "schema": "rc.spectate.v1",
            "ts": _ts(base, i),
            "session_id": session_id,
            "harness": harness,
            "source": "demo",
            "kind": "tool.pre",
            "step": "execute-tools",
            "node_id": "tool:rm",
            "agent_id": "main",
            "corr_id": "corr-rm",
            "tool": {"name": "Bash", "family": "shell", "target": "rm"},
            "deny": {"by": "plugin", "source": "guard-destructive", "rule": "rm-block"},
            "synthetic": True,
            "detail": "minimal",
        }
    )
    i += 1
    evs.append(
        {
            "schema": "rc.spectate.v1",
            "ts": _ts(base, i),
            "session_id": session_id,
            "harness": harness,
            "source": "demo",
            "kind": "turn.end",
            "node_id": "turn:0:end",
            "agent_id": "main",
            "synthetic": True,
            "detail": "minimal",
        }
    )
    return evs


def write_demo(project_root: Path) -> list[str]:
    runs = project_root / ".ravenclaude" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    base = datetime.now(timezone.utc)
    written = []
    for h in HARNESSES:
        sid = f"demo-{h}"
        d = runs / sid
        d.mkdir(parents=True, exist_ok=True)
        meta = {
            "synthetic": True,
            "harness": h,
            "source": "spectate_demo",
            "created": base.isoformat(),
        }
        (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        events = build_events(h, sid, base)
        lines = "\n".join(json.dumps(e, separators=(",", ":")) for e in events) + "\n"
        (d / "spectate-events.jsonl").write_text(lines, encoding="utf-8")
        # deny join fixture for plugin deny
        hook = {
            "ts": events[-2]["ts"],
            "corr_id": "corr-rm",
            "verdict": "deny",
            "hook": "guard-destructive",
            "rule": "rm-block",
            "by": "plugin",
        }
        (d / "hook-events.jsonl").write_text(
            json.dumps(hook, separators=(",", ":")) + "\n", encoding="utf-8"
        )
        written.append(sid)
    return written


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--project-root",
        default=".",
        help="project root containing .ravenclaude/runs",
    )
    args = p.parse_args()
    root = Path(args.project_root).resolve()
    ids = write_demo(root)
    print(f"spectate_demo: wrote {len(ids)} sessions under {root / '.ravenclaude' / 'runs'}")
    for sid in ids:
        print(f"  {sid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
