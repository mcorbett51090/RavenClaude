#!/usr/bin/env python3
"""Project the canonical hook manifest's SessionStart lane onto OpenAI Codex CLI's
native hooks.json.

Fourth sibling of `generate-copilot-hooks.py` / `generate-cursor-hooks.py` /
`generate-gemini-hooks.py` -- same `_EVENT` / `_SKIP` / `_script_of` / `project()`
(here: `build()`) / `--check` / `--out` contract -- but Codex needs NO adapter and
NO envelope translation. Codex speaks the Claude Code hook contract natively:
identical PascalCase event names, identical stdin field names (tool_name /
tool_input / cwd / session_id), identical `exit 2` + stderr blocking, identical
`hookSpecificOutput` envelope, and identical PascalCase tool-name VALUES ("Bash",
not Copilot's "bash") `[docs-verified 2026-07-28 -- learn.chatgpt.com/docs/hooks]`.
So every emitted command is a plain `bash "<shim>" "<hooks-dir>/<script>" [args]`
-- exactly the wrapping style `wire_codex_hooks()` (scripts/ravenclaude) used
before this file existed. The ONLY per-hook difference from the canonical
`${CLAUDE_PLUGIN_ROOT}/hooks/<script>` command is two environment variables
(`CLAUDE_PROJECT_DIR` / `CLAUDE_SESSION_ID`) that `hooks/codex-hook-env.sh` lifts
out of the stdin payload -- see that file's header for why an adapter is the
wrong shape here.

--------------------------------------------------------------------------------
SCOPE OF THIS GENERATOR (Phase 4, sessionstart-safeguards-multihost)
--------------------------------------------------------------------------------
* **SessionStart is DERIVED from hooks.json** -- the actual fix. Before this
  file existed, Codex wired only 2 of the canonical 9 SessionStart hooks
  (`capability-orientation.sh`, `thing-denial-kb-recall.sh`), with NO matcher on
  either -- so those two re-fired on every mid-conversation compaction on Codex,
  the exact PR #1084 defect finally reaching this host. `build()` now emits all
  9 hooks across the manifest's 3 real matcher groups (`startup|resume|clear|
  fork`, `startup`, `compact`), matcher included, matching `hooks.json` exactly.
* **PreToolUse / PostToolUse / Stop are reproduced BYTE-IDENTICALLY** to the
  pre-Phase-4 hand-list (`wire_codex_hooks()`'s prior Python heredoc) as
  LITERAL, HARDCODED blocks -- NOT derived from the canonical manifest. Widening
  those lanes to the full manifest is a separate, later decision (plan.md
  Phase 4: "out of this run's SessionStart-only scope... Do not widen scope to
  those lanes"). `_FIXED_PRETOOLUSE` / `_FIXED_POSTTOOLUSE` / `_FIXED_STOP`
  below are that literal transcription, unconditional -- they do not vary with
  `--legacy-sessionstart` or the manifest's current contents.
* Every canonical hook this generator does NOT wire (all of PreToolUse /
  PostToolUse / Stop beyond the fixed subset above, plus every hook under
  UserPromptSubmit / SubagentStart / PreCompact, which have no Codex lane at
  all yet) is accounted for in `_SKIP`, loudly, with a reason `--check` can
  print -- never silently dropped.

--------------------------------------------------------------------------------
KILL SWITCH -- RC_CODEX_SESSIONSTART_LEGACY=1
--------------------------------------------------------------------------------
Set (env var, or `--legacy-sessionstart` for direct invocation/testing) to emit
the pre-Phase-4 2-hook, matcher-less SessionStart block VERBATIM instead of the
9-hook derivation -- an instant, code-level rollback with no git revert needed.
PreToolUse/PostToolUse/Stop are unaffected either way (they are never derived).
Codex's hash-keyed hook trust (MH-17) still requires a `/hooks` re-trust after
flipping this, exactly as after any other change to `.codex/hooks.json` -- the
kill switch removes the uncertainty about WHAT gets re-trusted, not the
re-trust step itself.

`wire_codex_hooks()` (scripts/ravenclaude) is the ONLY call site that ships this
generator's output to a consumer, and it routes through `_rc_rearm_notice` +
prints the before/after hook count -- see that function, not this file, for the
re-trust flow.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MANIFEST = _REPO.joinpath("plugins", "ravenclaude-core", "hooks", "hooks.json")
_ARGV_TOKEN = '"$CLAUDE_TOOL_FILE_PATH"'

# Codex speaks the native Claude Code hook contract, so every event name is
# IDENTICAL on both sides -- there is nothing to translate. Kept as an explicit
# identity map (rather than omitted) for shape-parity with the other three
# projectors, and so a reader can see at a glance which events this generator
# actually emits a lane for.
_EVENT = {
    "SessionStart": "SessionStart",
    "PreToolUse": "PreToolUse",
    "PostToolUse": "PostToolUse",
    "Stop": "Stop",
}

_LANE_SCOPE_REASON = (
    "Phase 4 (sessionstart-safeguards-multihost) is SessionStart-ONLY in scope. "
    "PreToolUse/PostToolUse/Stop are reproduced byte-identically to the "
    "pre-Phase-4 hand-list (wire_codex_hooks()'s prior heredoc) rather than "
    "derived from the canonical manifest -- widening those lanes to full "
    "coverage is a separate, later decision (plan.md Phase 4: 'Do not widen "
    "scope to those lanes')."
)
_EVENT_UNWIRED_REASON = (
    "no Codex lane is wired for this event at all yet (Phase 4 is "
    "SessionStart-only in scope); wiring it is a separate, later decision."
)

# EXPLICIT skips -- every canonical hook this generator does not put in
# PreToolUse/PostToolUse/Stop's fixed subset, with a reason `--check` prints.
# `worktree-guard.sh` is deliberately NOT here even though its PreToolUse
# instance is unwired: the SAME basename is wired via the SessionStart
# derivation below (its SessionStart instance, arg "register"), so by-basename
# accounting (matching the sibling generators' contract) already covers it --
# listing it again here would just be confusing, not more correct.
_SKIP = {
    # PreToolUse -- out of this generator's fixed subset.
    "guard-probe-validity.sh": _LANE_SCOPE_REASON,
    "enforce-git-protocol.sh": _LANE_SCOPE_REASON,
    "preflight-command-review.sh": _LANE_SCOPE_REASON,
    "guard-remediation-cause.sh": _LANE_SCOPE_REASON,
    "guard-foreground-suite.sh": _LANE_SCOPE_REASON,
    "guard-memory-compaction.sh": _LANE_SCOPE_REASON,
    "route-decision-review.sh": _LANE_SCOPE_REASON,
    "guard-premise.sh": _LANE_SCOPE_REASON,
    "enforce-portability.sh": _LANE_SCOPE_REASON,
    "guard-cause-closure.sh": _LANE_SCOPE_REASON,
    # PostToolUse -- out of this generator's fixed subset.
    "guard-recursive-spawn.sh": _LANE_SCOPE_REASON,
    "delegation-nudge.sh": _LANE_SCOPE_REASON,
    "regen-on-manifest-change.sh": _LANE_SCOPE_REASON,
    "storage-placement-nudge.sh": _LANE_SCOPE_REASON,
    "mark-web-domain-seen.sh": _LANE_SCOPE_REASON,
    "sanitize-webfetch-output.sh": _LANE_SCOPE_REASON,
    "sanitize-mcp-output.sh": _LANE_SCOPE_REASON,
    "log-probe.sh": _LANE_SCOPE_REASON,
    "triage-outcome.sh": _LANE_SCOPE_REASON,
    # Stop -- out of this generator's fixed subset.
    "thing-denial-kb-sync.sh": _LANE_SCOPE_REASON,
    "handoff-nudge.sh": _LANE_SCOPE_REASON,
    # Events with no Codex lane wired at all yet.
    "ask-on-ambiguity.sh": _EVENT_UNWIRED_REASON,
    "stream-prompt-attribute.sh": _EVENT_UNWIRED_REASON,
    "agent-dispatch-evaluator.sh": _EVENT_UNWIRED_REASON,
    # PreCompact -- see D2 in the sessionstart-safeguards-multihost plan for
    # why Copilot's sibling generator keeps a (CLI-inert) projection here
    # instead of a literal _SKIP: that reasoning does not apply to Codex,
    # which has no PreCompact-adjacent event documented at all, so an honest
    # skip is correct, not a downgrade.
    "precompact-digest.sh": _EVENT_UNWIRED_REASON,
}

# The pre-Phase-4 SessionStart hand-list, transcribed verbatim as literal data
# -- A4.1's control. `--legacy-sessionstart` / RC_CODEX_SESSIONSTART_LEGACY=1
# reproduces exactly this: 2 hooks, no matcher.
_LEGACY_SESSIONSTART_HOOKS = ("capability-orientation.sh", "thing-denial-kb-recall.sh")

# The pre-Phase-4 PreToolUse/PostToolUse/Stop hand-list, transcribed verbatim.
# UNCONDITIONAL -- these never vary with --legacy-sessionstart; only
# SessionStart has a legacy/canonical split (see the module docstring).
_FIXED_PRETOOLUSE = (
    ("Bash", (("guard-destructive.sh", ""), ("thing-orchestrator.sh", ""), ("runaway-brake.sh", ""))),
    ("Edit|Write|MultiEdit", (("enforce-layout.sh", ""),)),
    ("WebFetch", (("guard-web-access.sh", ""),)),
)
_FIXED_POSTTOOLUSE = (
    (
        "Edit|Write|MultiEdit",
        (("format-on-write.sh", _ARGV_TOKEN), ("claim-grounding-lint.sh", _ARGV_TOKEN)),
    ),
)
_FIXED_STOP = (
    (None, (("dod-gate.sh", ""), ("remind-tests.sh", ""), ("stream-session-close.sh", ""))),
)


def _script_of(command: str) -> str:
    m = re.search(r"/(?:hooks|scripts)/([A-Za-z0-9._-]+\.sh)", command)
    return m.group(1) if m else ""


def _extra_args(command: str, script: str) -> str:
    """Everything after the script path, minus Claude-only argv placeholders."""
    marker = "/hooks/" + script
    if marker not in command:
        marker = "/scripts/" + script
    tail = command.split(marker, 1)[1].strip() if marker in command else ""
    return tail.replace(_ARGV_TOKEN, "").strip()


def _cmd(shim: str, hooks_dir: str, script: str, arg: str = "") -> dict:
    """`bash "<shim>" "<hooks-dir>/<script>" [arg]` -- exactly the wrapping
    style `wire_codex_hooks()`'s prior heredoc used. No adapter mode token
    (unlike Copilot/Cursor): the shim only lifts two env vars out of stdin and
    re-emits the payload unchanged; it takes no positional mode argument.
    """
    tail = f" {arg}" if arg else ""
    return {"type": "command", "command": f'bash "{shim}" "{hooks_dir}/{script}"{tail}'}


def _fixed_block(shim: str, hooks_dir: str, groups: tuple) -> tuple[list, list]:
    """Build a literal (matcher, [(script, arg), ...]) tuple-of-tuples into the
    Claude-shaped group list `_FIXED_PRETOOLUSE`/`_FIXED_POSTTOOLUSE`/
    `_FIXED_STOP` describe. Returns (json_groups, wired_scripts)."""
    out = []
    wired = []
    for matcher, hooks in groups:
        block = {}
        if matcher:
            block["matcher"] = matcher
        block["hooks"] = []
        for script, arg in hooks:
            block["hooks"].append(_cmd(shim, hooks_dir, script, arg))
            wired.append(script)
        out.append(block)
    return out, wired


def _derive_sessionstart(manifest: dict, shim: str, hooks_dir: str) -> tuple[list, list]:
    """The Phase 4 fix: every SessionStart hook + its real matcher, read
    directly off hooks.json's own SessionStart block -- the 3 matcher groups
    (`startup|resume|clear|fork`, `startup`, `compact`), in manifest order."""
    out = []
    wired = []
    for group in manifest.get("hooks", {}).get("SessionStart", []):
        matcher = group.get("matcher")
        block: dict = {}
        if matcher:
            block["matcher"] = matcher
        items = []
        for entry in group.get("hooks", []):
            command = entry.get("command", "")
            script = _script_of(command)
            if not script:
                continue
            args = _extra_args(command, script)
            items.append(_cmd(shim, hooks_dir, script, args))
            wired.append(script)
        block["hooks"] = items
        out.append(block)
    return out, wired


def _legacy_sessionstart(shim: str, hooks_dir: str) -> tuple[list, list]:
    wired = list(_LEGACY_SESSIONSTART_HOOKS)
    return [{"hooks": [_cmd(shim, hooks_dir, s) for s in wired]}], wired


def _all_canonical_scripts(manifest: dict) -> set:
    return {
        _script_of(e.get("command", ""))
        for groups in manifest.get("hooks", {}).values()
        for g in groups
        for e in g.get("hooks", [])
        if _script_of(e.get("command", ""))
    }


def _sessionstart_scripts(manifest: dict) -> set:
    return {
        _script_of(e.get("command", ""))
        for g in manifest.get("hooks", {}).get("SessionStart", [])
        for e in g.get("hooks", [])
        if _script_of(e.get("command", ""))
    }


def _event_of(manifest: dict, script: str) -> str:
    """First event this script appears under in the canonical manifest --
    used only to label a _SKIP entry in --check output."""
    for event, groups in manifest.get("hooks", {}).items():
        for g in groups:
            for e in g.get("hooks", []):
                if _script_of(e.get("command", "")) == script:
                    return event
    return "unknown"


def build(shim: str, hooks_dir: str, manifest: dict | None = None, legacy_sessionstart: bool = False) -> tuple:
    """Return (config, wired, skipped). Pure -- no I/O beyond the manifest read
    already done by the caller, so `--check` and the install path cannot
    diverge. `wired`/`skipped` entries are (script, event, ...) tuples,
    matching the sibling generators' shape."""
    manifest = manifest if manifest is not None else json.loads(_MANIFEST.read_text(encoding="utf-8"))

    if legacy_sessionstart:
        ss_groups, ss_wired = _legacy_sessionstart(shim, hooks_dir)
    else:
        ss_groups, ss_wired = _derive_sessionstart(manifest, shim, hooks_dir)
    pt_groups, pt_wired = _fixed_block(shim, hooks_dir, _FIXED_PRETOOLUSE)
    po_groups, po_wired = _fixed_block(shim, hooks_dir, _FIXED_POSTTOOLUSE)
    st_groups, st_wired = _fixed_block(shim, hooks_dir, _FIXED_STOP)

    wired: list = (
        [(s, "SessionStart") for s in ss_wired]
        + [(s, "PreToolUse") for s in pt_wired]
        + [(s, "PostToolUse") for s in po_wired]
        + [(s, "Stop") for s in st_wired]
    )
    wired_names = {s for s, _ in wired}

    skipped: list = []
    if legacy_sessionstart:
        # Every canonical SessionStart hook the legacy fallback does NOT wire
        # -- accounted for loudly, so --check never fails just because the
        # kill switch is engaged; it fails only if something is genuinely
        # unaccounted for.
        for script in sorted(_sessionstart_scripts(manifest) - set(ss_wired)):
            skipped.append(
                (
                    script,
                    "SessionStart",
                    "RC_CODEX_SESSIONSTART_LEGACY=1 is active -- this hook is not "
                    "wired under the SessionStart legacy fallback. Unset the env "
                    "var (or drop --legacy-sessionstart) to restore the full "
                    "9-hook derivation.",
                )
            )
    for script, reason in _SKIP.items():
        if script in wired_names:
            continue
        skipped.append((script, _event_of(manifest, script), reason))

    cfg = {
        "$schema": "https://json.schemastore.org/claude-code-hooks.json",
        "description": (
            "RavenClaude guardrails for OpenAI Codex CLI. GENERATED by "
            "`ravenclaude install --host codex` — do not hand-edit; re-run the installer. "
            "Paths are absolute into the marketplace checkout so `git pull` updates "
            "behaviour live. NOTE: Codex tracks hook trust BY HASH, so any change to a "
            "hook script marks it for review and SKIPS it until you re-trust via /hooks."
        ),
        "hooks": {
            "SessionStart": ss_groups,
            "PreToolUse": pt_groups,
            "PostToolUse": po_groups,
            "Stop": st_groups,
        },
    }
    return cfg, wired, skipped


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Project the SessionStart lane onto Codex CLI's native hooks.json.")
    ap.add_argument("--shim", default="<SHIM>", help="absolute path to hooks/codex-hook-env.sh")
    ap.add_argument("--hooks-dir", default="<HOOKS>", help="absolute path to the plugin's hooks/ directory")
    ap.add_argument("--out")
    ap.add_argument(
        "--legacy-sessionstart",
        action="store_true",
        help="emit the pre-Phase-4 2-hook, matcher-less SessionStart block (also RC_CODEX_SESSIONSTART_LEGACY=1)",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="assert every canonical hook is wired or explicitly skipped",
    )
    args = ap.parse_args(argv[1:])

    legacy = args.legacy_sessionstart or bool(os.environ.get("RC_CODEX_SESSIONSTART_LEGACY"))

    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    cfg, wired, skipped = build(args.shim, args.hooks_dir, manifest=manifest, legacy_sessionstart=legacy)

    if args.check:
        canonical = _all_canonical_scripts(manifest)
        accounted = {s for s, _ in wired} | {s for s, _, _ in skipped}
        missing = canonical - accounted
        if missing:
            print(
                f"codex-hooks: NOT accounted for (neither wired nor explicitly "
                f"skipped): {sorted(missing)}",
                file=sys.stderr,
            )
            return 1
        stale = set(_SKIP) - canonical
        if stale:
            print(
                f"codex-hooks: the skip map names hooks that no longer exist: {sorted(stale)}",
                file=sys.stderr,
            )
            return 1
        print(
            f"Codex hooks OK — {len(wired)} wired, {len(skipped)} explicitly "
            f"skipped, {len(canonical)} canonical hooks all accounted for."
            + (" (RC_CODEX_SESSIONSTART_LEGACY active)" if legacy else "")
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
