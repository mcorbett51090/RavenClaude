#!/usr/bin/env python3
"""Project the canonical hook manifest onto Gemini CLI's settings hooks block.

Multi-host audit MH-30. Third sibling of the Copilot and Cursor projectors, and
written the same way for the same reason: MH-12 proved a hand-maintained host hook
list drifts silently and grows more wrong every release. Three hand-lists would
have been three of those.

--------------------------------------------------------------------------------
EVENT MAP (Claude -> Gemini) `[docs-verified 2026-07-29 — geminicli.com/docs/hooks/reference/]`
--------------------------------------------------------------------------------
    PreToolUse   ->  BeforeTool     [ENFORCING — exit 2 blocks, stderr is the reason]
    PostToolUse  ->  AfterTool      [side-effect]
    SessionStart ->  SessionStart    [context]

`Stop` and `UserPromptSubmit` are NOT mapped. Gemini has `AfterAgent`,
`BeforeAgent` and `SessionEnd`, which are plausible counterparts by name — but
their payload schemas were not published on the pages verified, and mapping a
lifecycle event by name-similarity is exactly how a lane comes to assert coverage
it does not have. Every such hook is skipped EXPLICITLY, with the reason, and
`--check` fails if anything is dropped silently.

Gemini supports `matcher` with regex, so the canonical matcher is projected —
translated into GEMINI's tool vocabulary, since a matcher written in Claude's
PascalCase would match nothing.
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
    "PreToolUse": ("BeforeTool", "pretool"),
    "PostToolUse": ("AfterTool", "posttool"),
    "SessionStart": ("SessionStart", "sessionstart"),
}

# Claude tool name -> Gemini tool name(s), for translating the MATCHER. The shim
# translates the reverse direction at runtime; these two must stay consistent or a
# hook is scoped to a tool that never fires.
_TOOL_TO_GEMINI = {
    "Bash": ["run_shell_command"],
    "Read": ["read_file", "read_many_files"],
    "Write": ["write_file"],
    "Edit": ["replace", "edit_file"],
    "MultiEdit": ["replace"],
    "WebFetch": ["web_fetch"],
    "WebSearch": ["google_web_search", "web_search"],
}

_SKIP = {
    "stream-prompt-attribute.sh": (
        "UserPromptSubmit. Gemini has BeforeAgent/BeforeModel, but their payload "
        "schemas were not published on the verified pages — mapping by name "
        "similarity would assert coverage that may not exist."
    ),
    "dod-gate.sh": (
        "Stop. Gemini's AfterAgent/SessionEnd are plausible counterparts but "
        "unverified; a definition-of-done gate that fires on the wrong lifecycle "
        "event either never runs or blocks the wrong thing."
    ),
    "remind-tests.sh": ("Stop — same unverified lifecycle mapping as dod-gate.sh."),
    "stream-session-close.sh": ("Stop — same unverified lifecycle mapping."),
    "thing-denial-kb-sync.sh": ("Stop — same unverified lifecycle mapping."),
    "handoff-nudge.sh": ("Stop — same unverified lifecycle mapping as dod-gate.sh."),
    "handoff-successor-ack.sh": (
        "SessionStart startup handshake (file write). Gemini SessionStart "
        "payload/matcher names are unverified; a wrong-event ack would lie."
    ),
    "route-decision-review.sh": (
        "matches AskUserQuestion, a Claude Code tool with no Gemini equivalent."
    ),
    "enforce-layout.sh": (
        "takes the file path as ARGV, and Gemini's tool_input path field name is NOT "
        "verified — the docs' rewrite example shows `filepath`, other tools may use "
        "`file_path` or `absolute_path`. Wiring it would register a guard that "
        "receives no path and silently no-ops, which is worse than not wiring it: it "
        "would LOOK enforced. CI remains the layout backstop on this host. One line "
        "to enable once the field name is read from the tools reference."
    ),
    "agent-dispatch-evaluator.sh": (
        "SubagentStart. Gemini exposes no verified subagent hook event; this hook is "
        "an audit-only shadow that never denies, so the cost is observability."
    ),
}


def _script_of(command: str) -> str:
    m = re.search(r"/hooks/([A-Za-z0-9._-]+\.sh)", command)
    return m.group(1) if m else ""


def _extra_args(command: str, script: str) -> str:
    marker = "/hooks/" + script
    tail = command.split(marker, 1)[1].strip() if marker in command else ""
    return tail.replace(_ARGV_TOKEN, "").strip()


def _gemini_matcher(claude_matcher: str) -> str:
    """Translate a Claude matcher into Gemini's tool vocabulary.

    An untranslated matcher would be written in PascalCase and match no Gemini tool
    at all — the hook would be registered and never fire, which is indistinguishable
    from not shipping it.
    """
    if not claude_matcher:
        return ""
    out: list = []
    for part in claude_matcher.split("|"):
        part = part.strip()
        if not part:
            continue
        if part.startswith("mcp__"):
            out.append("mcp_.*")
            continue
        out.extend(_TOOL_TO_GEMINI.get(part, []))
    # dedupe, preserve order
    seen: set = set()
    uniq = [x for x in out if not (x in seen or seen.add(x))]
    return "|".join(uniq)


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
                if event not in _EVENT:
                    raise ValueError(
                        f"{script} is registered under '{event}', which has no Gemini "
                        "lane and no entry in the skip map. Add a lane or an explicit "
                        "skip with a reason."
                    )
                gem_event, mode = _EVENT[event]
                gmatch = _gemini_matcher(matcher)
                if matcher and not gmatch:
                    skipped.append(
                        (
                            script,
                            event,
                            f"matcher {matcher!r} has no Gemini tool equivalent — wiring it "
                            "would register a hook that can never fire.",
                        )
                    )
                    continue
                args = _extra_args(command, script)
                cmd = f'bash "{adapter}" {mode} "{hooks_dir}/{script}"'
                if args:
                    cmd += f" {args}"
                item: dict = {
                    "name": f"ravenclaude-{script[:-3]}",
                    "type": "command",
                    "command": cmd,
                    "timeout": 90000,
                }
                block: dict = {"hooks": [item]}
                if gmatch:
                    block["matcher"] = gmatch
                out.setdefault(gem_event, []).append(block)
                wired.append((script, event, gem_event, gmatch or "*"))
    return out, wired, skipped


def build(adapter: str, hooks_dir: str) -> tuple:
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    hooks, wired, skipped = project(manifest, adapter, hooks_dir)
    cfg = {
        "_generated_by": "scripts/generate-gemini-hooks.py — DO NOT HAND-EDIT; re-run the setup command.",
        "_not_wired": [f"{s} ({e}): {r}" for s, e, r in skipped],
        "hooks": hooks,
    }
    return cfg, wired, skipped


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Project hooks onto Gemini CLI.")
    ap.add_argument("--adapter", default="<ADAPTER>")
    ap.add_argument("--hooks-dir", default="<HOOKS>")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv[1:])

    try:
        cfg, wired, skipped = build(args.adapter, args.hooks_dir)
    except ValueError as exc:
        print(f"gemini-hooks: {exc}", file=sys.stderr)
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
            print(f"gemini-hooks: NOT accounted for: {sorted(missing)}", file=sys.stderr)
            return 1
        if not any(ev == "BeforeTool" for _, _, ev, _ in wired):
            print(
                "gemini-hooks: nothing wired to BeforeTool — the lane would enforce NOTHING.",
                file=sys.stderr,
            )
            return 1
        # Every emitted matcher must be in Gemini's vocabulary. A PascalCase matcher
        # that slipped through would register a hook that can never fire.
        for _s, _e, _ev, m in wired:
            if m != "*" and any(c.isupper() for c in m):
                print(
                    f"gemini-hooks: matcher {m!r} contains PascalCase — it would match no "
                    "Gemini tool.",
                    file=sys.stderr,
                )
                return 1
        print(
            f"Gemini hooks OK — {len(wired)} wired, {len(skipped)} explicitly skipped, "
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
