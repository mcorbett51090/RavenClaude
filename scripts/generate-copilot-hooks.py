#!/usr/bin/env python3
"""Project the canonical hook manifest onto GitHub Copilot CLI's hooks config.

Projected hooks are CLI **and** Chat-Preview-when-enabled (VS Code Copilot Chat
Preview can parse Copilot CLI hook files). Chat is still not session-isolated
by CONTENTION alone — see knowledge/copilot-chat-customization.md. Do not add
worktree-guard.sh to _SKIP.

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
    PreCompact                                      =>  precompact
    PostCompact                                     =>  postcompact
    PostToolUseFailure                              =>  posttoolfailure
    SubagentStart                                   =>  subagentstart
    SubagentStop                                    =>  subagentstop
    SessionEnd                                      =>  sessionend
    PermissionRequest                               =>  permissionrequest

A hand-listed mode map would be a second thing to drift; deriving it means adding
a hook to the canonical manifest is the only edit needed.
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
_ADAPTER_NAME = "copilot-hook-adapter.sh"

_ARGV_TOKEN = '"$CLAUDE_TOOL_FILE_PATH"'

# PreToolUse timeout. Under THING_HOST=copilot thing-decision.py raises the
# tribunal panel deadline to 105 s so a slow panel can still ABSTAIN with a
# reason; a host timeout below that kills the panel first, and Copilot's
# fail-closed timeout then denies with no reason at all. --check asserts every
# PreToolUse entry stays above that deadline (read from thing-decision.py when
# it can be found, never below _COPILOT_PANEL_DEADLINE_FLOOR).
_PRETOOL_TIMEOUT_SEC = 120
_COPILOT_PANEL_DEADLINE_FLOOR = 105

# Claude event -> adapter mode. An event absent here has NO Copilot lane and every
# hook under it must appear in SKIP with a reason.
_EVENT_MODE = {
    "SessionStart": "sessionstart",
    "PostToolUse": "posttool",
    "Stop": "stop",
    "UserPromptSubmit": "userpromptsubmit",
    # PreCompact — CHAT-PREVIEW-ONLY (§D2). The Copilot CLI's own documented hook
    # event set has NO compaction-adjacent event at all [docs-verified 2026-09-02,
    # re-confirmed this revision, corroborated by github/copilot-cli#1138 — an
    # open, unclosed feature request for exactly this gap]. So on the CLI this
    # entry is INERT: Copilot CLI writes a log line about an unrecognised hook
    # entry on EVERY session that loads this file — a consumer may misread that
    # noise as a broken install. It is retained anyway, solely because ONE
    # generated .github/hooks/ravenclaude.json file serves BOTH the CLI and VS
    # Code Copilot Chat Preview, and PreCompact genuinely exists on Chat, where it
    # is Chat's only compaction archival path. Dropping this entry (the literal
    # `_SKIP`) would silently remove that archival from Chat too, since `_SKIP` is
    # keyed by script basename and strips the hook from the file entirely. The
    # adapter's `precompact)` case is fail-safe regardless (discards the wrapped
    # hook's stdout and exit code, always exits 0 — copilot-hook-adapter.sh:334+),
    # so a never-fired CLI lane costs nothing beyond that log noise. If a future
    # session finds the CLI actually REJECTS this entry (rather than just logging
    # about it), switch this to the literal `_SKIP` with that finding as the
    # reason, and file the resulting Chat-coverage loss as a follow-up.
    "PreCompact": "precompact",
    # PostCompact — Claude Code + Codex document it; Copilot Chat's eight-event
    # set omits PostCompact [docs-verified 2026-09-01]. Fail-safe inert projection
    # keeps multi-event spectate-emit accounted (same shape as PermissionRequest).
    "PostCompact": "postcompact",
    # PostToolUseFailure — Claude Code + Codex + Cursor + Copilot document it.
    # CORRECTED 2026-10-12: v0.15 recorded that Copilot's event set "omits a
    # separate failure lane [docs-verified 2026-09-01]". The reference page now
    # documents `postToolUseFailure` / `PostToolUseFailure` ("After a tool
    # completes with a failure"; VS Code-compatible input carries hook_event_name,
    # session_id, cwd, tool_name, tool_input, error)
    # `[docs-verified 2026-10-12 — docs.github.com/en/copilot/reference/hooks-reference]`.
    # The adapter's `posttoolfailure` mode already passes that payload through to
    # spectate-emit, so this lane is LIVE, not inert. Two limits stay open (see
    # BUILD-PLAN § Deferred): Copilot publishes no tool-call id, and the mode does
    # not normalise lowercase tool names the way bash-pretool does, so a failure
    # lands on its own `tool-<name>` node rather than joining tool.pre's.
    "PostToolUseFailure": "posttoolfailure",
    # SubagentStart — observe/audit only. Adapter mode is fail-safe (discards
    # stdout + exit code). Needed so multi-event observe hooks like
    # spectate-emit.sh can register under SubagentStart without a full skip.
    "SubagentStart": "subagentstart",
    # SubagentStop — Copilot Chat documents SubagentStop; CLI fixed
    # subagentStart/subagentStop firing in 1.0.52 [docs-verified 2026-09-01 /
    # copilot-cli-hook-incompatibility.md]. Spectate v0.12 wires observe emit;
    # adapter is fail-safe (discards stdout + exit).
    "SubagentStop": "subagentstop",
    # SessionEnd — Copilot CLI documents sessionEnd
    # [docs-verified — knowledge/copilot-cli-customization.md]. Chat's eight-event
    # set omits SessionEnd; PascalCase projection stays inert there (same shape as
    # PreCompact-on-CLI). Spectate v0.12 observe; adapter fail-safe.
    "SessionEnd": "sessionend",
    # PermissionRequest — Claude Code permission-prompt lane (Spectate v0.4).
    # Adapter mode is fail-safe (discards stdout + exit). Copilot has no verified
    # PermissionRequest event; projecting keeps multi-event spectate-* scripts
    # accounted without a basename skip that would drop PreToolUse/UserPromptSubmit.
    "PermissionRequest": "permissionrequest",
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
    "workaround-exhaustion.sh": (
        "Two lanes, neither reachable here. The PreToolUse lane matches "
        "AskUserQuestion — the same no-Copilot-equivalent + pre-1.0.62 "
        "unhonored-matcher liability as route-decision-review.sh above. The Stop "
        "lane reads last_assistant_message off the Stop payload; the adapter's stop "
        "mode forwards no such field (copilot-hook-adapter.sh names it nowhere, "
        "checked 2026-09-17), so the hook is silent by construction there. "
        "Projecting either lane would ship a no-op that reads as coverage."
    ),
    "caveman-route-hook.sh": (
        "routes a Claude-Code-only third-party plugin; the target mode store does "
        "not exist on this host."
    ),
    "explore-tier-pin.sh": (
        "PreToolUse on Agent|Task that REWRITES the tool input via Claude Code's "
        "hookSpecificOutput.updatedInput [docs-verified 2026-09-14, Claude Code hooks "
        "reference]. Copilot's hook output contract has no verified input-rewrite "
        "field, and the adapter does not translate one — wiring it would ship a "
        "rewrite that is silently ignored while the generated config says the pin "
        "is in force. Copilot custom agents DO honour a `model` frontmatter field, "
        "but it takes a plan-specific picker id, so generate-copilot-plugin.py states "
        "the canonical tier in each projected agent's header for the consumer to pin "
        "rather than inventing an alias→id map; until pinned, the agent inherits the "
        "session default."
    ),
    "routine-reserve-hook.sh": (
        "The routine token reserve protects claude.ai cloud Routines and reads the "
        "weekly-cap position from Claude Code's statusline `rate_limits` — neither exists "
        "on this host, so both lanes would be silent by construction. Projecting them "
        "would ship a no-op that reads as coverage."
    ),
    "emit-permission-denied.sh": (
        "PermissionDenied is Claude Code auto-mode only — Copilot/Gemini have no "
        "equivalent event. Projecting it would ship a silent no-op that reads as "
        "coverage. Claude Code lane remains wired via hooks.json."
    ),
    # AppSec hook-env hardening (Claude-Code-only surfaces).
    "env-integrity-guard.sh": (
        "Claude-Code-only (AppSec hook-env): reads the `env` block of .claude/settings.json, which only Claude Code exports into hook processes; another host never plants it, and this repo's own settings carry RAVENCLAUDE_* keys the guard would quarantine."
    ),
    "pretool-record-check.sh": (
        "Claude-Code-only (AppSec hook-env): pairs with thing-orchestrator.sh's record keyed by Claude Code's tool_use_id; other hosts' adapters do not carry that id."
    ),
}


# Per-event skip — (script, Claude event) -> reason. Used when a multi-event
# observe hook (spectate-emit.sh) wires on some Copilot lanes but not others.
# The script-keyed `_SKIP` above would drop EVERY lane of the script; this map
# drops one. Preferred over an inert adapter mode for an event Copilot does not
# document: an inert projection ships a config entry Copilot CLI logs as
# "unrecognised" on every session, for a lane that can never fire.
_SKIP_EVENT = {
    ("spectate-emit.sh", "PermissionDenied"): (
        "PermissionDenied is a Claude Code auto-mode event. The Copilot hooks "
        "reference documents fourteen events and none is a permission-denial "
        "lane (permissionRequest fires BEFORE the permission service, and its "
        "decision control is allow/deny, not a post-denial notification) "
        "`[docs-verified 2026-10-12 — docs.github.com/en/copilot/reference/hooks-reference]`. "
        "Spectate v0.16 wires permission.resolve(deny) on Claude Code only."
    ),
    ("spectate-emit.sh", "StopFailure"): (
        "StopFailure is a Claude Code API-error turn end. Copilot documents "
        "agentStop (stopReason always `end_turn`) and a separate errorOccurred "
        "event whose errorContext spans model_call / tool_execution / system / "
        "user_input — it is not a turn-failure signal, and mapping it to a failed "
        "turn would be a guess `[docs-verified 2026-10-12 — "
        "docs.github.com/en/copilot/reference/hooks-reference]`. Spectate v0.16 "
        "wires failed turn.end on Claude Code only."
    ),
}


def _script_of(command: str) -> str:
    m = re.search(r"/(?:hooks|scripts)/([A-Za-z0-9._-]+\.sh)", command)
    return m.group(1) if m else ""


def _extra_args(command: str, script: str) -> str:
    """Everything after the script path, minus Claude-only argv placeholders."""
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
    # The tool-file-path placeholder is supplied by the adapter in file/post modes.
    return tail.replace(_ARGV_TOKEN, "").strip()


def _script_path(command: str, script: str, hooks_dir: str) -> str:
    """Where the hook body lives, read off the manifest command.

    Most bodies are under hooks/, but some are under scripts/ (the tribunal's
    substrate guard forces that packaging for a few). Always using hooks_dir
    pointed those entries at a file that does not exist, and the adapter's
    `[ -f "$real" ] || exit 0` turned each into a silent no-op. The scripts/
    sibling is resolved relative to hooks_dir's parent; a bare placeholder
    (`<HOOKS>`) keeps a `<HOOKS>/../scripts` form that still resolves once the
    placeholder is substituted.
    """
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
    """`bash <adapter> <mode> <hook> [args]`, each path shell-quoted.

    Bare double quotes let `$`, a backtick or a `"` in the checkout path expand,
    substitute or break the command; shlex.quote leaves an ordinary path as is.
    """
    out = f"bash {shlex.quote(adapter)} {mode} {shlex.quote(script_path)}"
    return out + (f" {args}" if args else "")


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
                skip_ev = _SKIP_EVENT.get((script, event))
                if skip_ev:
                    skipped.append((script, event, skip_ev))
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
                bash = _command(adapter, mode, _script_path(command, script, hooks_dir), args)
                item = {"type": "command", "bash": bash, "timeoutSec": 90}
                if event == "PreToolUse":
                    item["timeoutSec"] = _PRETOOL_TIMEOUT_SEC
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


# ── --check floors added by the 2026-10-19 repo review (1005-P1-5, scripts-14,
# 1a-8). Each has an in-process must-fail mutant in _teeth(), run by --check
# itself, so Gate 158 cannot pass while a floor has gone vacuous.


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
        for t in toks:
            if t.startswith("/") and t.endswith((".sh", ".py")) and not os.path.isfile(t):
                bad.append((cmd, t))
    return bad


_HOSTILE_ROOT = '/tmp/rc we$ird `x` "q" \'a/ravenclaude-core'


def _quoting_failures() -> list:
    """Commands that do not split back to the exact adapter + hook path when the
    checkout path carries `$`, a backtick, `"` and `'`."""
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


def _panel_deadline() -> int:
    """The Copilot tribunal panel deadline, read from thing-decision.py when its
    THING_HOST=copilot block can be found; never below the documented floor."""
    floor = _COPILOT_PANEL_DEADLINE_FLOOR
    src_path = _REPO / "plugins" / "ravenclaude-core" / "scripts" / "thing-decision.py"
    try:
        src = src_path.read_text(encoding="utf-8")
    except OSError:
        return floor
    m = re.search(
        r'THING_HOST"\)\s*==\s*"copilot".{0,800}?panel_deadline_seconds"\]\s*=\s*(\d+)',
        src,
        re.S,
    )
    return max(floor, int(m.group(1))) if m else floor


def _timeout_failures(cfg: dict, deadline: int) -> list:
    out = []
    for it in cfg.get("hooks", {}).get("PreToolUse", []):
        t = it.get("timeoutSec")
        if not (isinstance(t, int) and not isinstance(t, bool) and t > deadline):
            out.append(f"timeoutSec={t!r}: {it.get('bash', '')[:80]}")
    return out


def _teeth(manifest: dict) -> list:
    """Must-fail mutants for the floors above, in process. Each mutant MUST be
    caught; an uncaught one means that floor no longer measures anything."""
    errs: list = []
    g = globals()
    if any(
        "${CLAUDE_PLUGIN_ROOT}/scripts/" in e.get("command", "")
        for groups in manifest.get("hooks", {}).values()
        for grp in groups
        for e in grp.get("hooks", [])
    ):
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
    cfg, _w, _s = build("<ADAPTER>", "<HOOKS>")
    pre = cfg.get("hooks", {}).get("PreToolUse", [])
    if pre:
        pre[0]["timeoutSec"] = 90
        if not _timeout_failures(cfg, _panel_deadline()):
            errs.append("teeth: a 90 s PreToolUse timeout was NOT caught")
    return errs


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
                "copilot-hooks: the per-event skip map names (script, event) pairs "
                f"that no longer exist: {sorted(stale_ev)}",
                file=sys.stderr,
            )
            return 1
        # Spectate floors: multi-event spectate-emit must stay on every mapped
        # lifecycle lane. A basename-only account via PreToolUse would otherwise
        # hide a drop of SessionEnd/SubagentStop (v0.12) or SubagentStart.
        floor_events = (
            "SubagentStart",
            "SessionEnd",
            "SubagentStop",
            "PermissionRequest",
            "PreCompact",
            "PostCompact",
            "PostToolUseFailure",
        )
        by_event: dict[str, set[str]] = {e: set() for e in floor_events}
        for script, event, *_rest in wired:
            if event in by_event:
                by_event[event].add(script)
        missing_emit = [ev for ev, scripts in by_event.items() if "spectate-emit.sh" not in scripts]
        if missing_emit:
            print(
                "copilot-hooks: spectate-emit.sh missing from mapped lanes: "
                f"{missing_emit} (Spectate v0.12/v0.15 Copilot observe)",
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
                "copilot-hooks: bash not found — emitted-command syntax check "
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
                    f"copilot-hooks: {len(_bad)} emitted command(s) are NOT valid "
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
                f"copilot-hooks: {len(missing_tok)} emitted command(s) name a hook "
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
                f"copilot-hooks: {len(quoting)} command(s) do not round-trip a checkout "
                "path containing $, a backtick or quotes; e.g.:",
                file=sys.stderr,
            )
            for _c in quoting[:3]:
                print(f"  {_c[:160]!r}", file=sys.stderr)
            return 1
        # PreToolUse timeout outlives the Copilot tribunal panel deadline (1a-8).
        deadline = _panel_deadline()
        slow = _timeout_failures(cfg, deadline)
        if slow:
            print(
                f"copilot-hooks: {len(slow)} PreToolUse entr(y/ies) time out at or below "
                f"the Copilot panel deadline ({deadline} s), so the host would kill a "
                "slow panel and deny with no reason; e.g.:",
                file=sys.stderr,
            )
            for _c in slow[:3]:
                print(f"  {_c}", file=sys.stderr)
            return 1
        teeth = _teeth(manifest)
        if teeth:
            for _e in teeth:
                print(f"copilot-hooks: {_e}", file=sys.stderr)
            return 1
        print(
            f"Copilot hooks OK — {len(wired)} wired, {len(skipped)} explicitly "
            f"skipped, {len(canonical)} canonical hooks all accounted for; every hook "
            f"path resolves, quoting round-trips, PreToolUse timeout > {deadline} s."
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
