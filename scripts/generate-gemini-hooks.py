#!/usr/bin/env python3
"""Project the canonical hook manifest onto Gemini CLI's settings hooks block.

Multi-host audit MH-30. Third sibling of the Copilot and Cursor projectors, and
written the same way for the same reason: MH-12 proved a hand-maintained host hook
list drifts silently and grows more wrong every release. Three hand-lists would
have been three of those.

--------------------------------------------------------------------------------
EVENT MAP (Claude -> Gemini) `[docs-verified 2026-10-11 — geminicli.com/docs/hooks/reference/]`
--------------------------------------------------------------------------------
    PreToolUse         ->  BeforeTool     [ENFORCING — exit 2 blocks, stderr is the reason]
    PostToolUse        ->  AfterTool      [side-effect]
    SessionStart       ->  SessionStart   [context]
    SessionEnd         ->  SessionEnd     [best-effort observe; reason published]
    PreCompact         ->  PreCompress    [advisory; trigger auto|manual]
    UserPromptSubmit   ->  BeforeAgent    [prompt published; observe-only consumers]
    Stop               ->  AfterAgent     [prompt_response published; observe discard stdout]

Enforcement Stop / UserPromptSubmit consumers (dod-gate, ask-on-ambiguity, …)
stay explicitly skipped — AfterAgent retry / BeforeAgent deny semantics are not
verified for those gates. Spectate observe emit is the sanctioned consumer on
the new lanes. SubagentStart/Stop, PostCompact, PermissionRequest remain
skipped (no verified Gemini counterpart). `--check` fails if anything is
dropped silently.

Gemini supports `matcher` with regex, so the canonical matcher is projected —
translated into GEMINI's tool vocabulary, since a matcher written in Claude's
PascalCase would match nothing.
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
_ADAPTER_NAME = "gemini-hook-adapter.sh"
_ARGV_TOKEN = '"$CLAUDE_TOOL_FILE_PATH"'


def _is_missing_script(tok: str) -> bool:
    return tok.startswith("/") and tok.endswith((".sh", ".py")) and not os.path.isfile(tok)


def _command(adapter: str, mode: str, script_path: str, args: str) -> str:
    """`bash <adapter> <mode> <hook> [args]`, each path shell-quoted (a `$`,
    backtick or quote in the checkout path must not expand or break it)."""
    out = f"bash {shlex.quote(adapter)} {mode} {shlex.quote(script_path)}"
    return out + (f" {args}" if args else "")


_EVENT = {
    "PreToolUse": ("BeforeTool", "pretool"),
    "PostToolUse": ("AfterTool", "posttool"),
    "SessionStart": ("SessionStart", "sessionstart"),
    "SessionEnd": ("SessionEnd", "sessionend"),
    "PreCompact": ("PreCompress", "precompact"),
    "UserPromptSubmit": ("BeforeAgent", "beforeagent"),
    "Stop": ("AfterAgent", "afteragent"),
}

# _gemini_matcher() translates a Claude TOOL-name matcher (Bash, Read, ...) into
# Gemini's tool vocabulary — it was only ever designed for that. PreToolUse and
# PostToolUse matchers are tool names, so they belong here. SessionStart's matcher
# is a SOURCE name (startup/resume/clear/compact/fork) — a different vocabulary
# entirely. Routing it through _gemini_matcher() finds no translation (these
# strings aren't in _TOOL_TO_GEMINI) and, once a hook actually carries a
# SessionStart matcher, silently drops the hook from Gemini instead of wiring it
# unconditionally as it always used to when the matcher was absent.
_TOOL_SHAPED_EVENTS = {"PreToolUse", "PostToolUse"}

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
        "UserPromptSubmit → BeforeAgent is docs-verified for observe emit, but "
        "this hook injects additionalContext that has not been round-tripped on "
        "Gemini BeforeAgent — skip until that path is measured."
    ),
    # ⛔ NEWLY VISIBLE, NOT NEWLY BROKEN. `ask-on-ambiguity.sh` has been registered
    # since v0.273.0 and was DROPPED SILENTLY by all three host projectors for its
    # whole service life, because `_script_of` matched only `/hooks/` and this hook
    # body lives under `/scripts/` (the packaging exception the tribunal's
    # substrate guard forces). The generator's own "explicit skip or raise"
    # contract never fired, because a hook it cannot see is a hook it cannot
    # refuse. Widening the resolver surfaced it and this entry is the decision the
    # contract was always supposed to demand.
    # control: with the widened resolver, 42 of 42 registered commands resolve to a
    # script name and 0 are dropped; before it, 4 were dropped and none of the
    # three generators said a word.
    "ask-on-ambiguity.sh": (
        "UserPromptSubmit → BeforeAgent is docs-verified for observe emit, but "
        "this advisory nudge's additionalContext path is not round-tripped on "
        "Gemini — skip; cost is one un-nudged prompt, not lost enforcement."
    ),
    "prompt-optimizer-gate.sh": (
        "UserPromptSubmit → BeforeAgent observe lane exists, but this gate's "
        "additionalContext injection is not round-tripped on Gemini. Ships "
        "prompt_optimizer.enabled: false by default and never blocks — cost is "
        "one un-augmented prompt, not lost enforcement."
    ),
    "plugin-lifecycle-telemetry.sh": (
        "UserPromptSubmit (slash bumps) stay unwired on Gemini (observe-only "
        "spectate uses BeforeAgent); PostToolUse matchers Skill and Agent|Task "
        "have no Gemini tool equivalents in _TOOL_TO_GEMINI — Claude Code "
        "telemetry only. SessionStart sweep remains wired via "
        "plugin-lifecycle-sweep.sh."
    ),
    "dod-gate.sh": (
        "Stop → AfterAgent is docs-verified for observe emit, but this gate's "
        "decision:block / retry semantics on AfterAgent are not verified — a "
        "wrong lifecycle block either never runs or blocks the wrong thing."
    ),
    "remind-tests.sh": (
        "Stop → AfterAgent — same unverified enforcement/advisory path as "
        "dod-gate.sh (observe emit only wires spectate-emit)."
    ),
    "stream-session-close.sh": (
        "Stop → AfterAgent — same unverified non-observe consumer path as dod-gate.sh."
    ),
    "thing-denial-kb-sync.sh": (
        "Stop → AfterAgent — same unverified non-observe consumer path as dod-gate.sh."
    ),
    "handoff-nudge.sh": (
        "Stop → AfterAgent — same unverified non-observe consumer path as dod-gate.sh."
    ),
    "spectate-steer.sh": (
        "Opt-in Spectate steer consumer (v0.5; spectate_steer: on). Uses Claude Code "
        "hookSpecificOutput.permissionDecision / additionalContext. Gemini PreToolUse "
        "deny envelope is not verified for this path; skip is script-keyed. Claude "
        "Code carries the steer path."
    ),
    "emit-permission-denied.sh": (
        "PermissionDenied is Claude Code auto-mode only — Copilot/Gemini have no "
        "equivalent event. Projecting it would ship a silent no-op that reads as "
        "coverage. Claude Code lane remains wired via hooks.json."
    ),
    "workaround-exhaustion.sh": (
        "Two lanes, neither reachable here: the PreToolUse lane matches "
        "AskUserQuestion, a Claude Code tool with no Gemini equivalent (same as "
        "route-decision-review.sh); the Stop→AfterAgent lane is observe-only for "
        "spectate and this hook reads last_assistant_message off Claude Code's "
        "Stop payload, without which it is silent by construction. Projecting it "
        "would register a no-op that reads as coverage."
    ),
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
    "precompact-digest.sh": (
        "PreCompact → PreCompress is docs-verified for observe emit, but this "
        "archival digest engine (transcript_path + detached worker + egress "
        "floor) is not round-tripped on Gemini PreCompress — skip; cost is one "
        "un-archived digest, not lost enforcement. Spectate compact.pre wires."
    ),
    # ⛔ R7 — THE THREE verify-before-assert CELLS SHIP **UNWIRED AND DECLARED**,
    # for the same reason as the Cursor lane: docs-verified only, never
    # round-tripped against the live product. A guardrail fully wired and
    # reviewing nothing is the exact MH-01 shape, and tool-name normalisation
    # (run_shell_command -> Bash) is not optional when these are eventually wired.
    # control (G7.2, 2026-08-25): host-support.json still reads updated
    # 2026-08-14 — no newer evidence than the plan had — so the downgrade stands.
    "preflight-command-review.sh": (
        "UNWIRED — declared (R7). Not round-tripped against the live product; "
        "ships skipped rather than wired-and-hopeful. Host degrades to the "
        "portable text floor."
    ),
    "guard-remediation-cause.sh": (
        "UNWIRED — declared (R7). Same basis; carries a deny path at "
        "cause_remediation: block, so a silent no-op would claim a fail-closed "
        "surface that does not exist."
    ),
    "guard-cause-closure.sh": (
        "UNWIRED — declared (R7). Write-shaped, and the tool_input FIELD NAME "
        "carrying a file path is unverified here — the same gap that keeps "
        "enforce-layout.sh skipped above."
    ),
    "caveman-route-hook.sh": (
        "routes a Claude-Code-only third-party plugin; the target mode store does "
        "not exist on this host."
    ),
    "routine-reserve-hook.sh": (
        "protects claude.ai cloud Routines using Claude Code's statusline rate_limits; "
        "neither exists on this host (BeforeAgent observe lane is spectate-only)."
    ),
    # AppSec hook-env hardening (Claude-Code-only surfaces).
    "env-integrity-guard.sh": (
        "Claude-Code-only (AppSec hook-env): reads the `env` block of .claude/settings.json, which only Claude Code exports into hook processes; another host never plants it, and this repo's own settings carry RAVENCLAUDE_* keys the guard would quarantine."
    ),
    "pretool-record-check.sh": (
        "Claude-Code-only (AppSec hook-env): pairs with thing-orchestrator.sh's record keyed by Claude Code's tool_use_id; other hosts' adapters do not carry that id."
    ),
}

# Per-event skip — (script, Claude event) → reason. Multi-event observe hooks
# (spectate-emit) wire on Gemini's mapped lanes; remaining lifecycle gaps stay
# explicitly skipped.
_SKIP_EVENT = {
    ("spectate-emit.sh", "SubagentStart"): (
        "SubagentStart. Gemini exposes no verified subagent hook event on the "
        "pages checked. Other emit lanes wire."
    ),
    ("spectate-emit.sh", "PostCompact"): (
        "PostCompact. Gemini exposes no verified post-compaction hook event on "
        "the pages checked (PreCompress maps to PreCompact only). Spectate "
        "v0.13 wires compact.post on Claude Code + Codex."
    ),
    ("spectate-emit.sh", "PostToolUseFailure"): (
        "PostToolUseFailure. Gemini AfterTool covers completed tools; docs "
        "publish no separate failure event "
        "`[docs-verified 2026-10-11 — geminicli.com/docs/hooks/reference/]`. "
        "Spectate v0.15 wires tool.fail on Claude Code + Cursor + Codex."
    ),
    ("spectate-emit.sh", "PermissionDenied"): (
        "PermissionDenied. Claude Code auto-mode event; the Gemini hooks reference "
        "documents no denial-notification lane (Notification is ToolPermission "
        "observability only) "
        "`[docs-verified 2026-10-12 — geminicli.com/docs/hooks/reference/]`. "
        "Spectate v0.16 wires permission.resolve(deny) on Claude Code only."
    ),
    ("spectate-emit.sh", "StopFailure"): (
        "StopFailure. Gemini AfterAgent fires on a completed response; the docs "
        "publish no turn-failure event "
        "`[docs-verified 2026-10-12 — geminicli.com/docs/hooks/reference/]`. "
        "Spectate v0.16 wires failed turn.end on Claude Code only."
    ),
    ("spectate-emit.sh", "PermissionRequest"): (
        "PermissionRequest. Gemini Notification(ToolPermission) is observability "
        "only and cannot grant/deny — not a permission-prompt lane. Claude Code "
        "+ Copilot carry permission.request emit."
    ),
    ("spectate-emit.sh", "SubagentStop"): (
        "SubagentStop. Gemini exposes no verified subagent-stop hook event on the "
        "pages checked. Other emit lanes wire."
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
                skip_ev = _SKIP_EVENT.get((script, event))
                if skip_ev:
                    skipped.append((script, event, skip_ev))
                    continue
                if event not in _EVENT:
                    raise ValueError(
                        f"{script} is registered under '{event}', which has no Gemini "
                        "lane and no entry in the skip map. Add a lane or an explicit "
                        "skip with a reason."
                    )
                gem_event, mode = _EVENT[event]
                if event in _TOOL_SHAPED_EVENTS:
                    gmatch = _gemini_matcher(matcher)
                    if matcher and not gmatch:
                        skipped.append(
                            (
                                script,
                                event,
                                f"matcher {matcher!r} has no Gemini tool equivalent — wiring "
                                "it would register a hook that can never fire.",
                            )
                        )
                        continue
                else:
                    # Non-tool-shaped lifecycle events (SessionStart / SessionEnd /
                    # PreCompact / UserPromptSubmit / Stop). Manifest matchers are
                    # source/trigger names, not Claude tool names — wire
                    # unconditionally rather than guess a translation that could
                    # silently drop the hook.
                    gmatch = ""
                args = _extra_args(command, script)
                cmd = _command(adapter, mode, _script_path(command, script, hooks_dir), args)
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


# ── --check floors added by the 2026-10-19 repo review (1005-P1-5, scripts-14).
# Each has an in-process must-fail mutant in _teeth(), run by --check itself, so
# Gate 165 cannot pass while a floor has gone vacuous.


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


def _teeth(manifest: dict) -> list:
    """Must-fail mutants for the floors above, in process. Each MUST be caught."""
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
    return errs


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
        stale = set(_SKIP) - canonical
        if stale:
            print(
                f"gemini-hooks: the skip map names hooks that no longer exist: {sorted(stale)}",
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
                "gemini-hooks: the per-event skip map names (script, event) pairs "
                f"that no longer exist: {sorted(stale_ev)}",
                file=sys.stderr,
            )
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
                "gemini-hooks: bash not found — emitted-command syntax check "
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
                    f"gemini-hooks: {len(_bad)} emitted command(s) are NOT valid "
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
                f"gemini-hooks: {len(missing_tok)} emitted command(s) name a hook "
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
                f"gemini-hooks: {len(quoting)} command(s) do not round-trip a checkout "
                "path containing $, a backtick or quotes; e.g.:",
                file=sys.stderr,
            )
            for _c in quoting[:3]:
                print(f"  {_c[:160]!r}", file=sys.stderr)
            return 1
        teeth = _teeth(manifest)
        if teeth:
            for _e in teeth:
                print(f"gemini-hooks: {_e}", file=sys.stderr)
            return 1
        print(
            f"Gemini hooks OK — {len(wired)} wired, {len(skipped)} explicitly skipped, "
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
