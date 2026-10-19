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
    PreCompact                         ->  preCompact             [observe; v0.9]
    SubagentStart                      ->  subagentStart          [permission; v0.9]

`preToolUse` / `postToolUse` remain unwired for *enforcement* until a live
payload probe; v0.9 only opens the docs-verified PreCompact / SubagentStart
observe lanes for spectate-emit. Anything else is explicitly skipped WITH A
REASON, never silently dropped — `--check` fails the build otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MANIFEST = _REPO.joinpath("plugins", "ravenclaude-core", "hooks", "hooks.json")
_ADAPTER_NAME = "cursor-hook-adapter.sh"
_ARGV_TOKEN = '"$CLAUDE_TOOL_FILE_PATH"'

# Claude file-edit tool names. Cursor's PostToolUse lane here is afterFileEdit,
# which fires only on a file edit, so a PostToolUse hook whose matcher names
# none of these (a WebFetch / MCP / Bash / Agent output hook) can never fire on
# it and is skipped WITH A REASON rather than counted as coverage.
_FILE_EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
_AFTERFILEEDIT_SKIP_REASON = (
    "afterFileEdit never fires for tool output: this PostToolUse hook matches {m!r}, "
    "not a file-edit tool, so registering it on Cursor's only PostToolUse lane here "
    "would read as coverage it cannot give."
)


def _covers_file_edit(matcher: str) -> bool:
    if not matcher or matcher.strip() in ("*", ".*"):
        return True
    return any(p.strip() in _FILE_EDIT_TOOLS for p in matcher.split("|"))


def _is_missing_script(tok: str) -> bool:
    return tok.startswith("/") and tok.endswith((".sh", ".py")) and not os.path.isfile(tok)


# `SessionStart`'s matcher is never emitted for Cursor, and that is CORRECT, not a
# gap: `[docs-verified 2026-09-02 — cursor.com/docs/agent/hooks]` Cursor's matcher
# config section enumerates matcher support per event, and `sessionStart` is not
# among them — its documented input payload (session_id, is_background_agent,
# composer_mode + the common base fields) carries no `source`/`matcher`-able field
# either. So there is no Claude-Code-style startup/resume/clear/compact/fork
# discrimination to wire on this host; every SessionStart hook fires on every
# Cursor session start unconditionally, by platform design. (The payload DOES
# carry `transcript_path`, same field name as Claude Code's — see
# knowledge/cursor-customization.md for why that matters for the lease-identity
# work this comment sits next to in history.)
_EVENT = {
    "SessionStart": ("sessionStart", "sessionstart"),
    "PostToolUse": ("afterFileEdit", "file-posttool"),
    "Stop": ("stop", "stop"),
    "UserPromptSubmit": ("beforeSubmitPrompt", "promptsubmit"),
    # Spectate v0.9 — schemas docs-verified 2026-10-10 (cursor.com/docs/agent/hooks).
    # subagentStart is a permission hook (empty/invalid stdout BLOCKS); adapter
    # mode always emits {"permission":"allow"} after the observe hook.
    "PreCompact": ("preCompact", "precompact"),
    "SubagentStart": ("subagentStart", "subagentstart"),
    # Spectate v0.12 — schemas docs-verified 2026-10-10 (cursor.com/docs/agent/hooks).
    # sessionEnd is fire-and-forget (no output fields). subagentStop is observational
    # (optional followup_message — observe emits empty stdout, never forwards task/
    # summary/modified_files).
    "SessionEnd": ("sessionEnd", "sessionend"),
    "SubagentStop": ("subagentStop", "subagentstop"),
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
    "workaround-exhaustion.sh": (
        "Two lanes, neither reachable here: the PreToolUse lane matches "
        "AskUserQuestion (no Cursor equivalent, as route-decision-review.sh above); "
        "the Stop lane reads last_assistant_message off Claude Code's Stop payload, "
        "and no verified Cursor event carries that field — without it the hook is "
        "silent by construction, so a projection would read as coverage it cannot give."
    ),
    "agent-dispatch-evaluator.sh": (
        "SubagentStart audit-only shadow (never denies). Cursor subagentStart is "
        "now docs-verified and reserved for spectate-emit observe + allow "
        "(Spectate v0.9); the Haiku evaluator stays Claude-Code-only until a "
        "Cursor adapter path is designed for its audit ledger."
    ),
    "mark-web-domain-seen.sh": (
        "PostToolUse on WebFetch; pairs with guard-web-access.sh, which is skipped."
    ),
    "handoff-tax-meter.sh": (
        "PostToolUse on Agent|Task (a subagent-dispatch RESULT). Cursor's only "
        "PostToolUse lane here is afterFileEdit, which carries a file edit, not a "
        "dispatch — wiring it there would register a meter that can only ever "
        "no-op on its tool_name guard, and the generated config would claim "
        "coverage the host does not give. Cursor has no verified after-subagent "
        "event with the dispatch payload; the dispatch ledger is Claude-Code-only "
        "on this host."
    ),
    "explore-tier-pin.sh": (
        "PreToolUse on Agent|Task that REWRITES the tool input via Claude Code's "
        "hookSpecificOutput.updatedInput. Cursor's verified pre-tool lane carries a "
        "shell command and has no input-rewrite field, so the pin cannot bind here. "
        "On Cursor, pick the model tier in the dispatch call itself."
    ),
    "spectate-steer.sh": (
        "Opt-in Spectate steer consumer (v0.5; spectate_steer: on). Pause-as-deny + PermissionRequest approve/deny + "
        "additionalContext note injection. Cursor's verified PreToolUse deny shape "
        "differs from Claude Code's hookSpecificOutput.permissionDecision envelope; "
        "skip is script-keyed until a Cursor adapter path is probed. Claude Code "
        "carries the steer path."
    ),
    "emit-permission-denied.sh": (
        "PermissionDenied. Cursor has no verified lane for Claude Code PermissionDenied hooks."
    ),
    "precompact-digest.sh": (
        "PreCompact is docs-verified on Cursor (Spectate v0.9 wires spectate-emit "
        "there). precompact-digest stays skipped: its cheap_lane/egress floor is "
        "Claude-Code-shaped; Cursor PreCompact is observational and cannot host "
        "that archival engine without a separate adapter design."
    ),
    # ⛔ R7 — THE THREE verify-before-assert CELLS SHIP **UNWIRED AND DECLARED**.
    # This is a deliberate DOWNGRADE from what the lane would otherwise do: both
    # Bash-shaped hooks below would map cleanly onto beforeShellExecution, and the
    # generator would wire them without complaint. They are skipped anyway.
    #
    # The governing rule: a lane whose event is not LIVE-verified ships as
    # explicitly skipped with a stated reason, never as wired-and-hopeful. A
    # silent no-op guardrail is strictly worse than a documented gap, because it
    # produces a false sense of coverage that survives into the next session's
    # priors. The in-repo existence proof is Copilot: plugin-level hooks were
    # DOCUMENTED to fire, were shipped that way, and only github/copilot-cli#2540
    # -- a live product bug report, not a docs re-read -- revealed they never do.
    # A synthetic-fixture canary would have stayed green throughout.
    #
    # ⛔ Cursor additionally FAILS OPEN on a malformed hook response, so a cell
    # that is wrong here is wrong SILENTLY.
    #
    # control (G7.2, 2026-08-25): re-read knowledge/host-support.json rather than
    # trusting its standing "unverified" note. `updated` still reads 2026-08-14 --
    # no newer evidence than the plan had -- so the downgrade stands unmodified.
    # These move to wired only when G7.1 is satisfied in full: a cited dated URL
    # for the event's input schema, the field name carrying a file path for the
    # write-path gate, AND a live round-trip against the real product.
    "preflight-command-review.sh": (
        "UNWIRED — declared (R7). Bash-shaped and would map to "
        "beforeShellExecution, but that round-trip has never been run against the "
        "live product, and Cursor fails OPEN on a malformed response. Ships "
        "skipped until G7.1 passes; the host degrades to the portable text floor."
    ),
    "guard-remediation-cause.sh": (
        "UNWIRED — declared (R7). Same basis as preflight-command-review.sh. This "
        "one carries a deny path at cause_remediation: block, so a silently "
        "fail-open cell would claim a fail-closed surface that does not exist."
    ),
    "guard-cause-closure.sh": (
        "UNWIRED — declared (R7). Write/Edit/MultiEdit-shaped: Cursor's verified "
        "enforcement event carries a shell command, not file content, and the "
        "file-write events reachable here fire AFTER the edit. Same skip basis as "
        "enforce-layout.sh above, plus the R7 live-round-trip requirement."
    ),
    "caveman-route-hook.sh": (
        "routes a Claude-Code-only third-party plugin; the target mode store does "
        "not exist on this host."
    ),
    "routine-reserve-hook.sh": (
        "protects claude.ai cloud Routines using Claude Code's statusline rate_limits; "
        "neither exists on this host, so both lanes would be silent by construction."
    ),
    # AppSec hook-env hardening (Claude-Code-only surfaces).
    "env-integrity-guard.sh": (
        "Claude-Code-only (AppSec hook-env): reads the `env` block of .claude/settings.json, which only Claude Code exports into hook processes; another host never plants it, and this repo's own settings carry RAVENCLAUDE_* keys the guard would quarantine."
    ),
    "pretool-record-check.sh": (
        "Claude-Code-only (AppSec hook-env): pairs with thing-orchestrator.sh's record keyed by Claude Code's tool_use_id; other hosts' adapters do not carry that id."
    ),
}

# Per-event skip — (script, Claude event) → reason. Used when a multi-event
# observe hook can wire on some Cursor lanes but not others. Script-keyed
# `_SKIP` would drop every event; this map lets SessionStart / UserPromptSubmit /
# Stop / Bash-PreToolUse / afterFileEdit / PreCompact / SubagentStart project
# while PermissionRequest stays explicitly skipped (Spectate v0.9).
_SKIP_EVENT = {
    ("spectate-emit.sh", "PermissionRequest"): (
        "PermissionRequest. Cursor third-party hooks table marks PermissionRequest "
        "unsupported `[docs-verified 2026-10-11 — cursor.com/docs/reference/third-party-hooks]` "
        "(no Cursor mapping). Claude Code + Copilot carry permission.request emit."
    ),
    ("spectate-emit.sh", "PermissionDenied"): (
        "PermissionDenied. Claude Code auto-mode event; Cursor's hooks reference "
        "documents no permission-denial lane (and marks PermissionRequest "
        "unsupported) `[docs-verified 2026-10-12 — cursor.com/docs/agent/hooks]`. "
        "Spectate v0.16 wires permission.resolve(deny) on Claude Code only."
    ),
    ("spectate-emit.sh", "StopFailure"): (
        "StopFailure. Claude Code API-error turn end. Cursor's `stop` carries a "
        "status field but its payload shape is not probed here; wiring it as a "
        "failed turn would be a guess `[docs-verified 2026-10-12 — "
        "cursor.com/docs/agent/hooks]`. Spectate v0.16 wires failed turn.end on "
        "Claude Code only."
    ),
    ("spectate-emit.sh", "PostCompact"): (
        "PostCompact. Cursor docs publish preCompact but no verified postCompact "
        "lane [docs-verified 2026-10-10 — cursor.com/docs/agent/hooks]. Spectate "
        "v0.13 wires compact.post on Claude Code + Codex only."
    ),
}


def _script_of(command: str) -> str:
    m = re.search(r"/(?:hooks|scripts)/([A-Za-z0-9._-]+\.sh)", command)
    return m.group(1) if m else ""


def _extra_args(command: str, script: str) -> str:
    marker = "/hooks/" + script
    if marker not in command:
        marker = "/scripts/" + script
    if marker in command:
        tail = command.split(marker, 1)[1]
        # PR #1316 double-quoted the script path in the manifest, so the path's
        # own CLOSING quote is the first char of the split tail (`" check`, or a
        # lone `"`). Strip it BEFORE .strip() — a legacy unquoted path's tail
        # starts with whitespace, not a quote, so it is left untouched. Without
        # this every emitted command ends in a stray unterminated quote and
        # fails `bash -n` (the whole projection was broken; see the round-trip
        # validation gate).
        if tail.startswith('"'):
            tail = tail[1:]
        tail = tail.strip()
    else:
        tail = ""
    return tail.replace(_ARGV_TOKEN, "").strip()


def _script_path(command: str, script: str, hooks_dir: str) -> str:
    """Where the hook body lives (hooks/ or scripts/), read off the manifest
    command; scripts/ resolves relative to hooks_dir's parent. Mirrors
    generate-copilot-hooks.py — see the rationale there."""
    m = re.search(
        r"\$\{CLAUDE_PLUGIN_ROOT\}/(hooks|scripts)/" + re.escape(script) + r"(?![A-Za-z0-9._-])",
        command,
    )
    sub = m.group(1) if m else "hooks"
    if sub == "hooks":
        return f"{hooks_dir}/{script}"
    p = Path(hooks_dir)
    if p.parent == Path(".") and not hooks_dir.startswith("."):
        return f"{hooks_dir}/../{sub}/{script}"
    return str(p.parent / sub / script)


def _command(adapter: str, mode: str, script_path: str, args: str) -> str:
    """`bash <adapter> <mode> <hook> [args]`, each path shell-quoted (a `$`,
    backtick or quote in the checkout path must not expand or break it)."""
    out = f"bash {shlex.quote(adapter)} {mode} {shlex.quote(script_path)}"
    return out + (f" {args}" if args else "")


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
                skip_ev = _SKIP_EVENT.get((script, event))
                if skip_ev:
                    skipped.append((script, event, skip_ev))
                    continue
                if event == "PreToolUse" and script == "spectate-emit.sh":
                    # Spectate v0.10 — docs-verified Cursor preToolUse (all tools +
                    # tool_use_id). Observe-only; enforcement stays on
                    # beforeShellExecution for Bash guards.
                    # `[docs-verified 2026-10-10 — cursor.com/docs/agent/hooks]`
                    cursor_event, mode = "preToolUse", "tool-pre"
                elif event == "PostToolUse" and script == "spectate-emit.sh":
                    # Spectate v0.10 — docs-verified Cursor postToolUse (all tools +
                    # tool_use_id). File formatters stay on afterFileEdit via _EVENT.
                    cursor_event, mode = "postToolUse", "tool-post"
                elif event == "PostToolUseFailure" and script == "spectate-emit.sh":
                    # Spectate v0.15 — docs-verified Cursor postToolUseFailure
                    # `[docs-verified 2026-10-11 — cursor.com/docs/agent/hooks]`.
                    # Never forwards error_message.
                    cursor_event, mode = "postToolUseFailure", "tool-fail"
                elif event == "PreToolUse":
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
                elif event == "PostToolUse":
                    if not _covers_file_edit(matcher):
                        skipped.append(
                            (script, event, _AFTERFILEEDIT_SKIP_REASON.format(m=matcher))
                        )
                        continue
                    cursor_event, mode = _EVENT[event]
                elif event in _EVENT:
                    cursor_event, mode = _EVENT[event]
                else:
                    raise ValueError(
                        f"{script} is registered under '{event}', which has no Cursor "
                        "lane and no entry in the skip map. Add a lane or an explicit "
                        "skip with a reason."
                    )
                args = _extra_args(command, script)
                # Invoked as `bash "<adapter>"` rather than executing it directly,
                # matching the Codex lane. The wiring then survives a checkout that
                # lost its exec bits — Windows, some zip exports, the installer's own
                # `cp -r` fallback where symlinks are unavailable. On a host that
                # FAILS OPEN, a hook that cannot execute is a guardrail that silently
                # is not there, so this is worth the four extra characters.
                cmd = _command(adapter, mode, _script_path(command, script, hooks_dir), args)
                entry: dict = {"command": cmd, "timeout": 90}
                if cursor_event == "beforeShellExecution":
                    entry["failClosed"] = True
                out.setdefault(cursor_event, []).append(entry)
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


# ── --check floors added by the 2026-10-19 repo review (1005-P1-5, scripts-14,
# 1a-11). Each has an in-process must-fail mutant in _teeth(), run by --check
# itself, so Gate 160 cannot pass while a floor has gone vacuous.


def _emitted_commands(obj) -> list:
    acc: list = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("bash", "command") and isinstance(v, str):
                acc.append(v)
            else:
                acc.extend(_emitted_commands(v))
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            acc.extend(_emitted_commands(v))
    return acc


def _real_paths() -> tuple:
    hooks = _REPO / "plugins" / "ravenclaude-core" / "hooks"
    return str(hooks / _ADAPTER_NAME), str(hooks)


def _missing_script_tokens(cfg: dict) -> list:
    """(command, problem) for a command that does not shlex-split, or whose
    absolute .sh/.py token names no file. Run on a REAL-path projection."""
    bad = []
    for cmd in _emitted_commands(cfg.get("hooks", {})):
        try:
            toks = shlex.split(cmd)
        except ValueError:
            bad.append((cmd, "does not shlex-split"))
            continue
        bad.extend((cmd, t) for t in toks if _is_missing_script(t))
    return bad


_HOSTILE_ROOT = '/tmp/rc we$ird `x` "q" \'a/ravenclaude-core'


def _quoting_failures() -> list:
    adapter = f"{_HOSTILE_ROOT}/hooks/{_ADAPTER_NAME}"
    cfg, _w, _s = build(adapter, f"{_HOSTILE_ROOT}/hooks")
    bad = []
    for cmd in _emitted_commands(cfg.get("hooks", {})):
        try:
            toks = shlex.split(cmd)
        except ValueError:
            bad.append(cmd)
            continue
        if len(toks) < 4 or toks[0] != "bash" or toks[1] != adapter:
            bad.append(cmd)
        elif not toks[3].startswith(_HOSTILE_ROOT + "/"):
            bad.append(cmd)
    return bad


def _afterfileedit_failures(cfg: dict, manifest: dict) -> list:
    """Scripts registered on afterFileEdit with no file-edit PostToolUse matcher."""
    file_matched: set = set()
    for grp in manifest.get("hooks", {}).get("PostToolUse", []):
        if _covers_file_edit(grp.get("matcher") or ""):
            for e in grp.get("hooks", []):
                file_matched.add(_script_of(e.get("command", "")))
    bad = []
    for cmd in _emitted_commands(cfg.get("hooks", {}).get("afterFileEdit", [])):
        try:
            toks = shlex.split(cmd)
        except ValueError:
            bad.append(cmd)
            continue
        name = os.path.basename(toks[3]) if len(toks) > 3 else ""
        if name not in file_matched:
            bad.append(name or cmd)
    return bad


def _teeth(manifest: dict) -> list:
    """Must-fail mutants for the floors above, in process. Each MUST be caught."""
    errs: list = []
    g = globals()
    entries = [
        (ev, grp, e)
        for ev, groups in manifest.get("hooks", {}).items()
        for grp in groups
        for e in grp.get("hooks", [])
    ]
    if any("${CLAUDE_PLUGIN_ROOT}/scripts/" in e.get("command", "") for _ev, _g, e in entries):
        orig = g["_script_path"]
        g["_script_path"] = lambda command, script, hooks_dir: f"{hooks_dir}/{script}"
        try:
            mcfg, _w, _s = build(*_real_paths())
        finally:
            g["_script_path"] = orig
        if not _missing_script_tokens(mcfg):
            errs.append("teeth: a scripts/ hook pointed at hooks/ was NOT caught")
    orig_cmd = g["_command"]
    g["_command"] = lambda a, m, s, x: f'bash "{a}" {m} "{s}"' + (f" {x}" if x else "")
    try:
        if not _quoting_failures():
            errs.append("teeth: double-quoted paths under a hostile checkout were NOT caught")
    finally:
        g["_command"] = orig_cmd
    non_file_post = [
        e
        for ev, grp, e in entries
        if ev == "PostToolUse"
        and not _covers_file_edit(grp.get("matcher") or "")
        and _script_of(e.get("command", "")) not in _SKIP
        and _script_of(e.get("command", "")) != "spectate-emit.sh"
    ]
    if non_file_post:
        orig_cov = g["_covers_file_edit"]
        g["_covers_file_edit"] = lambda matcher: True
        try:
            mcfg, _w, _s = build("<ADAPTER>", "<HOOKS>")
        finally:
            g["_covers_file_edit"] = orig_cov
        if not _afterfileedit_failures(mcfg, manifest):
            errs.append("teeth: a tool-output PostToolUse hook on afterFileEdit was NOT caught")
    return errs


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
            print(f"cursor-hooks: NOT accounted for: {sorted(missing)}", file=sys.stderr)
            return 1
        stale = set(_SKIP) - canonical
        if stale:
            print(
                f"cursor-hooks: the skip map names hooks that no longer exist: {sorted(stale)}",
                file=sys.stderr,
            )
            return 1
        manifest_pairs = {
            (_script_of(e.get("command", "")), ev)
            for ev, groups in manifest.get("hooks", {}).items()
            for g in groups
            for e in g.get("hooks", [])
            if _script_of(e.get("command", ""))
        }
        stale_ev = set(_SKIP_EVENT) - manifest_pairs
        if stale_ev:
            print(
                "cursor-hooks: the per-event skip map names (script, event) pairs "
                f"that no longer exist: {sorted(stale_ev)}",
                file=sys.stderr,
            )
            return 1
        if not any(ev == "beforeShellExecution" for _, _, ev, _ in wired):
            print(
                "cursor-hooks: nothing wired to beforeShellExecution — the lane would "
                "enforce NOTHING on this host.",
                file=sys.stderr,
            )
            return 1
        # Spectate floors: v0.9 preCompact/subagentStart; v0.10 preToolUse/postToolUse;
        # v0.12 sessionEnd/subagentStop; v0.15 postToolUseFailure.
        wired_pairs = {(s, e) for s, e, _, _ in wired}
        wired_cursor = {(s, ce) for s, _, ce, _ in wired}
        for need_ev, cursor_ev in (
            ("PreCompact", "preCompact"),
            ("SubagentStart", "subagentStart"),
            ("SessionEnd", "sessionEnd"),
            ("SubagentStop", "subagentStop"),
            ("PostToolUseFailure", "postToolUseFailure"),
        ):
            if ("spectate-emit.sh", need_ev) not in wired_pairs:
                print(
                    f"cursor-hooks: spectate-emit.sh not wired on {need_ev}→{cursor_ev} "
                    f"(Spectate v0.9/v0.12/v0.15)",
                    file=sys.stderr,
                )
                return 1
        for cursor_ev in ("preToolUse", "postToolUse", "postToolUseFailure"):
            if ("spectate-emit.sh", cursor_ev) not in wired_cursor:
                print(
                    f"cursor-hooks: spectate-emit.sh not wired on Cursor {cursor_ev} "
                    f"(Spectate v0.10/v0.15)",
                    file=sys.stderr,
                )
                return 1
        # Command-syntax floor (added after the PR #1316 regression): the emitted
        # command STRING must be valid shell. This --check accounted only for
        # basenames, so it stayed GREEN while _extra_args left a stray closing
        # quote on every command and `bash -n` rejected all of them. Validate the
        # real strings so a manifest-quoting change can never silently break the
        # projection again.
        import shutil as _sh
        import subprocess as _sp

        def _emitted(obj):
            acc = []
            if isinstance(obj, dict):
                for _k, _v in obj.items():
                    if _k in ("bash", "command") and isinstance(_v, str):
                        acc.append(_v)
                    else:
                        acc.extend(_emitted(_v))
            elif isinstance(obj, (list, tuple)):
                for _v in obj:
                    acc.extend(_emitted(_v))
            return acc

        _bash = _sh.which("bash")
        if _bash is None:
            print(
                "cursor-hooks: bash not found — emitted-command syntax check "
                "SKIPPED (a SKIP, not a pass).",
                file=sys.stderr,
            )
        else:
            _bad = [
                _cmd
                for _cmd in _emitted(cfg)
                if _cmd.strip()
                and _sp.run([_bash, "-n", "-c", _cmd], capture_output=True).returncode != 0
            ]
            if _bad:
                print(
                    f"cursor-hooks: {len(_bad)} emitted command(s) are NOT valid "
                    "shell (a stray quote / bad _extra_args?); e.g.:",
                    file=sys.stderr,
                )
                for _c in _bad[:5]:
                    print(f"  {_c!r}", file=sys.stderr)
                return 1
        # Every hook path must name a real file once real paths are substituted
        # (1005-P1-5): a scripts/ hook projected under hooks/ is a silent no-op.
        real_cfg, _rw, _rs = build(*_real_paths())
        missing_tok = _missing_script_tokens(real_cfg)
        if missing_tok:
            print(
                f"cursor-hooks: {len(missing_tok)} emitted command(s) name a hook "
                "file that does not exist (or do not shlex-split); e.g.:",
                file=sys.stderr,
            )
            for _c, _t in missing_tok[:5]:
                print(f"  {_t}  <-  {_c[:120]!r}", file=sys.stderr)
            return 1
        # Paths survive a hostile checkout path (scripts-14).
        quoting = _quoting_failures()
        if quoting:
            print(
                f"cursor-hooks: {len(quoting)} command(s) do not round-trip a checkout "
                "path containing $, a backtick or quotes; e.g.:",
                file=sys.stderr,
            )
            for _c in quoting[:3]:
                print(f"  {_c[:160]!r}", file=sys.stderr)
            return 1
        # afterFileEdit carries only hooks that can fire on a file edit (1a-11).
        afe = _afterfileedit_failures(cfg, manifest)
        if afe:
            print(
                "cursor-hooks: tool-output PostToolUse hooks registered on afterFileEdit, "
                f"which never fires for tool output: {sorted(set(afe))}",
                file=sys.stderr,
            )
            return 1
        teeth = _teeth(manifest)
        if teeth:
            for _e in teeth:
                print(f"cursor-hooks: {_e}", file=sys.stderr)
            return 1
        n_afe = sum(1 for _s, _e, r in skipped if r.startswith("afterFileEdit never fires"))
        print(
            f"Cursor hooks OK — {len(wired)} wired, {len(skipped)} explicitly skipped "
            f"({n_afe} tool-output PostToolUse kept off afterFileEdit), "
            f"{len(canonical)} canonical hooks all accounted for; every hook path "
            "resolves, quoting round-trips."
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
