#!/usr/bin/env python3
"""Project the canonical hook manifest onto Cursor's hooks config.

Multi-host audit MH-13. Sibling of the Copilot projector, and written the same way
for the same reason: MH-12 found that a hand-maintained host hook list drifts
silently and grows more wrong every release. A second hand-maintained list would
have reproduced that defect on a new host within a month.

--------------------------------------------------------------------------------
CURSOR FAILS OPEN, AND THAT DRIVES THE EVENT CHOICE
--------------------------------------------------------------------------------
"malformed JSON response silently allows command instead of blocking"
`[docs-verified 2026-07-28 — Cursor's own bug tracker]`. Every other supported host
fails CLOSED on a broken hook. So the lane is deliberately narrow: it is built on
`beforeShellExecution`, the ONE enforcement event whose full input *and* output
schema Cursor publishes.

`preToolUse` / `postToolUse` exist on Cursor and would map more directly — but
their per-event payload fields were not published on the page verified, and
guessing a payload shape on a host that treats a wrong guess as "allow" is exactly
the trade this repo refuses. The event names are known, so wiring them later is a
small change, not a redesign.

--------------------------------------------------------------------------------
EVENT MAP (Claude -> Cursor)
--------------------------------------------------------------------------------
    PreToolUse   (Bash-shaped guards)  ->  beforeShellExecution   [ENFORCING]
    PostToolUse  (file-shaped)         ->  afterFileEdit          [side-effect]
    SessionStart                       ->  sessionStart           [context]
    Stop                               ->  stop                   [never blocks]
    UserPromptSubmit                   ->  beforeSubmitPrompt     [never blocks]

Anything else is explicitly skipped WITH A REASON, never silently dropped —
`--check` fails the build otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MANIFEST = _REPO.joinpath("plugins", "ravenclaude-core", "hooks", "hooks.json")
_ARGV_TOKEN = '"$CLAUDE_TOOL_FILE_PATH"'

_EVENT = {
    "SessionStart": ("sessionStart", "sessionstart"),
    "PostToolUse": ("afterFileEdit", "file-posttool"),
    "Stop": ("stop", "stop"),
    "UserPromptSubmit": ("beforeSubmitPrompt", "promptsubmit"),
}

# PreToolUse hooks reach Cursor only through beforeShellExecution, which carries a
# shell command. A hook whose matcher covers Bash belongs there; a purely
# file-shaped or web-shaped guard has no Cursor enforcement event we have verified.
_SKIP = {
    "enforce-layout.sh": (
        "file-shaped PreToolUse guard (takes a path as argv). Cursor's verified "
        "enforcement event carries a shell command, not a file path, and the "
        "file-write events we could reach are AFTER the edit. CI remains the "
        "backstop for layout on this host."
    ),
    "guard-web-access.sh": (
        "matches WebFetch. Cursor exposes beforeMCPExecution and its own network "
        "handling, but no verified event for an agent web fetch, so wiring it here "
        "would claim coverage that does not exist."
    ),
    "route-decision-review.sh": (
        "matches AskUserQuestion, a Claude Code tool with no Cursor equivalent."
    ),
    "agent-dispatch-evaluator.sh": (
        "SubagentStart. Cursor does expose subagentStart, but its payload schema is "
        "not published on the page verified, and this hook is an audit-only shadow "
        "that never denies — observability, not enforcement."
    ),
    "mark-web-domain-seen.sh": (
        "PostToolUse on WebFetch; pairs with guard-web-access.sh, which is skipped."
    ),
}


def _script_of(command: str) -> str:
    m = re.search(r"/hooks/([A-Za-z0-9._-]+\.sh)", command)
    return m.group(1) if m else ""


def _extra_args(command: str, script: str) -> str:
    marker = "/hooks/" + script
    tail = command.split(marker, 1)[1].strip() if marker in command else ""
    return tail.replace(_ARGV_TOKEN, "").strip()


def project(manifest: dict, adapter: str, hooks_dir: str) -> tuple:
    out: dict = {}
    wired: list = []
    skipped: list = []
    for event, groups in manifest.get("hooks", {}).items():
        for group in groups:
            matcher = group.get("matcher") or ""
            for entry in group.get("hooks", []):
                command = entry.get("command", "")
                script = _script_of(command)
                if not script:
                    continue
                if script in _SKIP:
                    skipped.append((script, event, _SKIP[script]))
                    continue
                if event == "PreToolUse":
                    if "Bash" not in matcher:
                        skipped.append(
                            (
                                script,
                                event,
                                "PreToolUse matcher does not cover Bash, and Cursor's "
                                "verified enforcement event carries a shell command.",
                            )
                        )
                        continue
                    cursor_event, mode = "beforeShellExecution", "shell-pretool"
                elif event in _EVENT:
                    cursor_event, mode = _EVENT[event]
                else:
                    raise ValueError(
                        f"{script} is registered under '{event}', which has no Cursor "
                        "lane and no entry in the skip map. Add a lane or an explicit "
                        "skip with a reason."
                    )
                args = _extra_args(command, script)
                cmd = f'"{adapter}" {mode} "{hooks_dir}/{script}"'
                if args:
                    cmd += f" {args}"
                out.setdefault(cursor_event, []).append({"command": cmd, "timeout": 90})
                wired.append((script, event, cursor_event, mode))
    return out, wired, skipped


def build(adapter: str, hooks_dir: str) -> tuple:
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    hooks, wired, skipped = project(manifest, adapter, hooks_dir)
    cfg = {
        "version": 1,
        "_generated_by": "scripts/generate-cursor-hooks.py — DO NOT HAND-EDIT; re-run the setup command.",
        "_source": "the canonical RavenClaude hook manifest",
        "_fail_open_warning": (
            "CURSOR FAILS OPEN: a malformed hook response silently ALLOWS the command "
            "(Cursor bug tracker, verified 2026-07-28). The adapter therefore emits its deny "
            "verdict as a fixed literal with no interpolation. Do not hand-edit these entries."
        ),
        "_not_wired": [f"{s} ({e}): {r}" for s, e, r in skipped],
        "hooks": hooks,
    }
    return cfg, wired, skipped


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Project hooks onto Cursor.")
    ap.add_argument("--adapter", default="<ADAPTER>")
    ap.add_argument("--hooks-dir", default="<HOOKS>")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv[1:])

    try:
        cfg, wired, skipped = build(args.adapter, args.hooks_dir)
    except ValueError as exc:
        print(f"cursor-hooks: {exc}", file=sys.stderr)
        return 1

    if args.check:
        manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
        canonical = {
            _script_of(e.get("command", ""))
            for groups in manifest.get("hooks", {}).values()
            for g in groups
            for e in g.get("hooks", [])
            if _script_of(e.get("command", ""))
        }
        accounted = {s for s, *_ in wired} | {s for s, *_ in skipped}
        missing = canonical - accounted
        if missing:
            print(
                f"cursor-hooks: NOT accounted for: {sorted(missing)}", file=sys.stderr
            )
            return 1
        if not any(ev == "beforeShellExecution" for _, _, ev, _ in wired):
            print(
                "cursor-hooks: nothing wired to beforeShellExecution — the lane would "
                "enforce NOTHING on this host.",
                file=sys.stderr,
            )
            return 1
        print(
            f"Cursor hooks OK — {len(wired)} wired, {len(skipped)} explicitly skipped, "
            f"{len(canonical)} canonical hooks all accounted for."
        )
        return 0

    text = json.dumps(cfg, indent=2) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
