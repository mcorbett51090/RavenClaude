#!/usr/bin/env python3
"""Project the canonical hook manifest onto GitHub Copilot CLI's hooks config.

Multi-host audit **MH-12**. The Copilot wiring used to be a Python heredoc inside
`scripts/ravenclaude` that listed hooks by hand. It had drifted badly: the
canonical manifest registers 25 hook entries and the heredoc wired 11, so **14
shipped guardrails never fired under Copilot at all** — among them the web-access
guard, the worktree guard, both Muninn hooks, and the delegation nudge. Nothing
enforced that the two lists agreed, so the drift was invisible and grew with every
release.

This derives the Copilot config from the canonical manifest instead, and
`--check` fails if any canonical hook is neither projected nor explicitly skipped.

--------------------------------------------------------------------------------
MATCHERS ARE PROJECTED — and the claim that they could not be was WRONG
--------------------------------------------------------------------------------
The Copilot knowledge file stated flatly *"Copilot CLI has no per-tool matcher"*.
That is false, and it was the repo's own MH-24 "guardrail against the next MH-01".

Copilot supports **two payload formats, selected by the event name's casing**
`[docs-verified 2026-07-28 — docs.github.com/en/copilot/reference/hooks-configuration]`:

  * **camelCase** (`preToolUse`, `sessionStart`, `agentStop`) — native format,
    no per-tool matcher; scoping is a native regex rule.
  * **PascalCase** (`PreToolUse`, `SessionStart`, `Stop`) — Claude-compatible
    format. *"Hooks configured with the PascalCase event name `PreToolUse` apply
    Claude's matcher semantics"*, and field names switch to snake_case.

The generated file has **always** used PascalCase keys, so Claude matcher
semantics were available the whole time and simply were not used. Corroborated
independently by the changelog: **1.0.62** — *"PostToolUse hook matchers (e.g.
Edit-or-Write) are now honored instead of silently dropped"*.

**Degradation below 1.0.62 is SAFE, which is why this is unconditional:** an
unhonored matcher means the hook fires for *every* tool — exactly the behaviour of
the hand-maintained file it replaces. The hooks self-filter and the adapter
normalises tool names, so old Copilot is no worse than today and new Copilot is
correctly scoped. Emitting matchers conditionally on the installer machine's
Copilot version was considered and rejected: it would make the generated
guardrails depend on who ran the setup.

--------------------------------------------------------------------------------
ADAPTER MODE IS DERIVED, NOT LISTED
--------------------------------------------------------------------------------
Each hook runs through the Copilot hook adapter as `<mode> <script> [args...]`.
The mode follows from the event plus *how the hook consumes its input*, which is
readable off the canonical command:

    PreToolUse  + takes the tool file path as argv  =>  file-pretool
    PreToolUse  + reads stdin                       =>  bash-pretool
    PostToolUse                                     =>  posttool
    SessionStart                                    =>  sessionstart
    Stop                                            =>  stop
    UserPromptSubmit                                =>  userpromptsubmit

A hand-listed mode map would be a second thing to drift; deriving it means adding
a hook to the canonical manifest is the only edit needed.
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

# Claude event -> adapter mode. An event absent here has NO Copilot lane and every
# hook under it must appear in SKIP with a reason.
_EVENT_MODE = {
    "SessionStart": "sessionstart",
    "PostToolUse": "posttool",
    "Stop": "stop",
    "UserPromptSubmit": "userpromptsubmit",
    # PreToolUse resolves to bash-pretool / file-pretool per-hook (see above).
}

# EXPLICIT skips. The remedy requires that a hook without a Copilot lane be
# skipped *loudly*, never silently — silent omission is the defect being fixed.
# Keyed by script basename; the reason is printed by --check and lands in the
# generated config so a consumer can see what is NOT protecting them.
_SKIP = {
    "agent-dispatch-evaluator.sh": (
        "SubagentStart has no adapter mode. Copilot does expose a `subagentStart` "
        "event, but nothing translates its envelope yet — and this hook is an "
        "audit-only shadow that never denies, so the cost of omitting it is "
        "observability, not enforcement. Wire it when the adapter grows the mode."
    ),
    "route-decision-review.sh": (
        "matches AskUserQuestion, a Claude Code tool with no Copilot equivalent, so "
        "it could never usefully fire. Deliberately NOT wired: below Copilot 1.0.62 "
        "an unhonored matcher makes a hook fire for EVERY tool, and this one expects "
        "an AskUserQuestion payload — wiring it would be a liability on exactly the "
        "versions where the matcher cannot protect it."
    ),
}


def _script_of(command: str) -> str:
    m = re.search(r"/hooks/([A-Za-z0-9._-]+\.sh)", command)
    return m.group(1) if m else ""


def _extra_args(command: str, script: str) -> str:
    """Everything after the script path, minus Claude-only argv placeholders."""
    marker = "/hooks/" + script
    tail = command.split(marker, 1)[1].strip() if marker in command else ""
    # The tool-file-path placeholder is supplied by the adapter in file/post modes.
    return tail.replace(_ARGV_TOKEN, "").strip()


def project(manifest: dict, adapter: str, hooks_dir: str) -> tuple:
    """Return (config, wired, skipped). Pure — no I/O, so `--check` and the
    setup path cannot diverge."""
    out: dict = {}
    wired: list = []
    skipped: list = []
    for event, groups in manifest.get("hooks", {}).items():
        for group in groups:
            matcher = group.get("matcher")
            for entry in group.get("hooks", []):
                command = entry.get("command", "")
                script = _script_of(command)
                if not script:
                    continue
                if script in _SKIP:
                    skipped.append((script, event, _SKIP[script]))
                    continue
                if event == "PreToolUse":
                    mode = "file-pretool" if _ARGV_TOKEN in command else "bash-pretool"
                elif event in _EVENT_MODE:
                    mode = _EVENT_MODE[event]
                else:
                    # An event with no lane AND no explicit skip. Fail loudly
                    # rather than drop it — that silence is the whole bug.
                    raise ValueError(
                        f"{script} is registered under '{event}', which has no "
                        "adapter mode and no entry in the skip map. Add a lane or "
                        "an explicit skip with a reason."
                    )
                args = _extra_args(command, script)
                # `bash "<adapter>"` rather than executing it directly, matching the
                # Codex and Cursor lanes: the wiring then survives a checkout that
                # lost its exec bits (Windows, zip exports, the installer's own cp -r
                # fallback).
                #
                # The failure this prevents is LOUD on Copilot and SILENT on Cursor,
                # and the difference is worth knowing: Copilot's preToolUse "fails
                # closed — an error/crash/timeout denies the tool", so a
                # non-executable adapter there would deny everything and be noticed in
                # seconds. Cursor fails OPEN, so the same breakage there is invisible.
                # Same fix, very different blast radius.
                bash = f'bash "{adapter}" {mode} "{hooks_dir}/{script}"'
                if args:
                    bash += f" {args}"
                item = {"type": "command", "bash": bash, "timeoutSec": 90}
                # Claude matcher semantics apply under the PascalCase event name.
                if matcher:
                    item["matcher"] = matcher
                out.setdefault(event, []).append(item)
                wired.append((script, event, mode, matcher or "*"))
    return out, wired, skipped


def build(adapter: str, hooks_dir: str) -> tuple:
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    hooks, wired, skipped = project(manifest, adapter, hooks_dir)
    cfg = {
        "version": 1,
        "_generated_by": "scripts/generate-copilot-hooks.py — DO NOT HAND-EDIT; re-run the setup command.",
        "_source": "the canonical RavenClaude hook manifest",
        "_matchers": (
            "PascalCase event names select Copilot's Claude-compatible format, under which "
            "Claude matcher semantics apply (docs.github.com/en/copilot/reference/hooks-configuration). "
            "Matchers are honored from Copilot CLI 1.0.62; below that they are ignored and each hook "
            "fires for every tool, which is safe here because the hooks self-filter."
        ),
        "_not_wired": [f"{s} ({e}): {r}" for s, e, r in skipped],
        "hooks": hooks,
    }
    return cfg, wired, skipped


def _canonical_scripts(manifest: dict) -> set:
    return {
        _script_of(e.get("command", ""))
        for groups in manifest.get("hooks", {}).values()
        for g in groups
        for e in g.get("hooks", [])
        if _script_of(e.get("command", ""))
    }


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Project hooks onto Copilot CLI.")
    ap.add_argument("--adapter", default="<ADAPTER>")
    ap.add_argument("--hooks-dir", default="<HOOKS>")
    ap.add_argument("--out")
    ap.add_argument(
        "--check",
        action="store_true",
        help="assert every canonical hook is wired or explicitly skipped",
    )
    args = ap.parse_args(argv[1:])

    try:
        cfg, wired, skipped = build(args.adapter, args.hooks_dir)
    except ValueError as exc:
        print(f"copilot-hooks: {exc}", file=sys.stderr)
        return 1

    if args.check:
        manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
        canonical = _canonical_scripts(manifest)
        accounted = {s for s, *_ in wired} | {s for s, *_ in skipped}
        missing = canonical - accounted
        if missing:
            print(
                "copilot-hooks: NOT accounted for (neither wired nor explicitly "
                f"skipped): {sorted(missing)}",
                file=sys.stderr,
            )
            return 1
        stale = set(_SKIP) - canonical
        if stale:
            print(
                f"copilot-hooks: the skip map names hooks that no longer exist: {sorted(stale)}",
                file=sys.stderr,
            )
            return 1
        print(
            f"Copilot hooks OK — {len(wired)} wired, {len(skipped)} explicitly "
            f"skipped, {len(canonical)} canonical hooks all accounted for."
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
