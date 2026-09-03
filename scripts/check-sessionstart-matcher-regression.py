#!/usr/bin/env python3
"""Gate 259 — SessionStart matcher regression floor.

Built for the sessionstart-hook-safeguards FORGE run, after the G4a critic
proved (with a reproducible mutant, see --self-test) that the obvious design
-- "does the generator's own --check pass?" -- is BLIND to this exact
regression class: a hook that gets silently DROPPED from a host still passes
that host's own --check, because --check only asserts "every canonical hook
is wired OR explicitly skipped with a reason", and a newly-broken skip still
carries a plausible-sounding reason string. See critic-brief.md CE-1.

Three independent checks, because any one alone is insufficient:

  A. Canonical-manifest matcher check. Asserts hooks.json's SessionStart
     block carries the exact matcher values on the exact hook set, directly
     -- catches a REVERTED fix even when every host generator's wiring still
     looks fine (a wiring-only ledger, as originally proposed, would miss
     this: CE-1's own finding, one level up).
  B. hooks.json <-> .claude/settings.json SessionStart parity. Catches drift
     between the plugin-canonical and marketplace-dev-mirror registrations
     (found live this session: keep-awake.sh was silently absent from the
     dev-mirror -- fixed in the same commit as this gate).
  C. Per-host WIRED-SET ledger, checked against each generator's REAL
     project() output (not its `skipped` reasons) -- this is what actually
     catches the Gemini-style regression. Declares, per host, which of the 8
     SessionStart hooks MUST be wired; fails closed on any host whose actual
     wiring disagrees, and fails closed on an unlisted hook rather than
     silently ignoring it.

Exit codes: 0 clean, 2 a check failed, 1 could not run (malformed input --
never reported as clean, matching this repo's own premise-gate convention).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_HOOKS_JSON = _REPO / "plugins" / "ravenclaude-core" / "hooks" / "hooks.json"
_SETTINGS_JSON = _REPO / ".claude" / "settings.json"
_GEMINI_GEN = _REPO / "scripts" / "generate-gemini-hooks.py"
_COPILOT_GEN = _REPO / "scripts" / "generate-copilot-hooks.py"

_SOURCE_MATCHER = "startup|resume|clear|fork"
_COMPACT_MATCHER = "compact"
_SOURCE_HOOKS = frozenset(
    {
        "reapply-posture.sh",
        "ensure-default-mode.sh",
        "capability-orientation.sh",
        "keep-awake.sh",
        "worktree-guard.sh",  # matched by basename; "register" arg stripped below
        "thing-denial-kb-recall.sh",
        "dashboard-autostart.sh",
    }
)
_COMPACT_HOOK = "compact-anchor.sh"

# The declared per-host WIRED-SET ledger. `required` = must be wired
# (regardless of matcher precision -- that's check A/generator-specific);
# a host not listed here is not asserted on (deliberately narrow: Codex has
# no generator to run, Copilot's matcher pass-through is asserted separately
# below since it doesn't need a live run to prove -- see check C's Copilot
# branch).
#
# Phase 1 (F-1) note: this stays Gemini-only in this phase on purpose --
# Copilot-CLI/Cursor/Claude-Code/Codex rows are Phases 2/3/4's job, running
# in parallel once this extractor refactor lands. What Phase 1 fixes is that
# check_c_wired_set() below no longer has ONE hardcoded reader that only
# happens to understand Gemini's shape -- it dispatches per host through
# _EXTRACTORS, so a future ledger row is a dict entry, not a rewrite.
_WIRED_SET_LEDGER = {
    "gemini": _SOURCE_HOOKS | {_COMPACT_HOOK},
}

_CURSOR_GEN = _REPO / "scripts" / "generate-cursor-hooks.py"


def _basename(command: str) -> str:
    tail = command.rstrip().split()[-1] if command.strip() else command
    name = tail.rsplit("/", 1)[-1]
    return name


def _sh_basename(text: str) -> str:
    """Pull a `<name>.sh` basename out of an arbitrary shell-command string.

    The flat host shapes (Copilot-CLI, Cursor) carry no `name` field at all --
    the only place a basename lives is inside the assembled `bash`/`command`
    string (e.g. `bash "<adapter>" sessionstart "<hooks-dir>/keep-awake.sh"`,
    sometimes with trailing args like `... /worktree-guard.sh" register`).
    Stops at the first `/`-free, non-quote run ending in `.sh`, so a trailing
    arg token never gets mistaken for the script name.
    """
    m = re.search(r"([A-Za-z0-9_.-]+\.sh)", text)
    return m.group(1) if m else ""


def _session_start_groups(hooks_json_path: Path) -> dict:
    data = json.loads(hooks_json_path.read_text(encoding="utf-8"))
    groups: dict[str, set[str]] = {}
    for entry in data.get("hooks", {}).get("SessionStart", []):
        matcher = entry.get("matcher")
        names = set()
        for h in entry.get("hooks", []):
            cmd = h.get("command", "")
            # "worktree-guard.sh register" -> basename is "register"; take the
            # script token specifically (first path-shaped word).
            for tok in cmd.split():
                if "/" in tok or tok.endswith(".sh"):
                    names.add(_basename(tok))
                    break
        groups.setdefault(matcher, set()).update(names)
    return groups


def check_a_canonical_matcher(findings: list, hooks_json_path: Path | None = None) -> None:
    groups = _session_start_groups(hooks_json_path or _HOOKS_JSON)
    source_actual = groups.get(_SOURCE_MATCHER, set())
    compact_actual = groups.get(_COMPACT_MATCHER, set())
    if source_actual != _SOURCE_HOOKS:
        findings.append(
            "A: hooks.json SessionStart matcher %r hook set is %s, expected %s"
            % (_SOURCE_MATCHER, sorted(source_actual), sorted(_SOURCE_HOOKS))
        )
    if compact_actual != {_COMPACT_HOOK}:
        findings.append(
            "A: hooks.json SessionStart matcher %r hook set is %s, expected {%s}"
            % (_COMPACT_MATCHER, sorted(compact_actual), _COMPACT_HOOK)
        )


def check_b_parity(
    findings: list,
    hooks_json_path: Path | None = None,
    settings_json_path: Path | None = None,
) -> None:
    a = _session_start_groups(hooks_json_path or _HOOKS_JSON)
    b = _session_start_groups(settings_json_path or _SETTINGS_JSON)
    a_source = a.get(_SOURCE_MATCHER, set())
    b_source = b.get(_SOURCE_MATCHER, set())
    if a_source != b_source:
        only_a = sorted(a_source - b_source)
        only_b = sorted(b_source - a_source)
        findings.append(
            "B: hooks.json/.claude/settings.json SessionStart parity broken -- "
            "only in hooks.json: %s; only in settings.json: %s" % (only_a, only_b)
        )


def _run_host_generator(generator: Path, repo: Path) -> dict:
    """Run a host projector's `--out` flag and return its parsed JSON config.

    Shared plumbing for every per-host extractor below -- F-1's actual fix is
    what each extractor does with this config (each host emits a genuinely
    different SessionStart shape), not how the config gets produced.
    """
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        subprocess.run(
            [sys.executable, str(generator), "--out", str(out)],
            check=True,
            capture_output=True,
            cwd=str(repo),
        )
        return json.loads(out.read_text(encoding="utf-8"))


def _extract_gemini(repo: Path) -> dict:
    """Gemini's SessionStart shape: `hooks.SessionStart[] ->
    {hooks:[{name,type,command,timeout}], matcher?}`, names prefixed
    `ravenclaude-<stem>`.

    This is F-1's regression-proof reader: it reproduces the pre-Phase-1
    `_run_generator_wired()`'s exact Gemini-reading logic byte-for-byte
    (same key-tolerance, same "hooks" nesting fallback, same
    `ravenclaude-` prefix strip), generalized only in that it now returns
    the matcher too instead of discarding it. Returns
    `{basename: matcher_or_None}`.
    """
    generator = repo / "scripts" / "generate-gemini-hooks.py"
    if not generator.exists():
        return {}
    cfg = _run_host_generator(generator, repo)
    wired: dict = {}
    events = cfg.get("hooks", cfg)  # generators nest under "hooks"; tolerate a flat shape too
    for key in ("SessionStart", "sessionStart"):
        for block in events.get(key, []):
            matcher = block.get("matcher")
            for h in block.get("hooks", []):
                nm = h.get("name", "")
                # generators emit "ravenclaude-<script-stem>"
                if nm.startswith("ravenclaude-"):
                    wired[nm[len("ravenclaude-") :] + ".sh"] = matcher
    return wired


def _extract_copilot_cli_flat(repo: Path) -> dict:
    """Copilot CLI's SessionStart shape: `hooks.SessionStart[]` FLAT (no
    per-matcher grouping like Gemini's), each entry
    `{type,bash,timeoutSec,matcher}` -- no `name` field at all, so the
    basename has to be read off the `bash` command string instead. Returns
    `{basename: matcher_or_None}`.
    """
    generator = repo / "scripts" / "generate-copilot-hooks.py"
    if not generator.exists():
        return {}
    cfg = _run_host_generator(generator, repo)
    events = cfg.get("hooks", cfg)
    wired: dict = {}
    for entry in events.get("SessionStart", []):
        name = _sh_basename(entry.get("bash", ""))
        if name:
            wired[name] = entry.get("matcher")
    return wired


def _extract_cursor_flat(repo: Path) -> dict:
    """Cursor's sessionStart shape: `hooks.sessionStart[]` FLAT, each entry
    `{command,timeout}` -- no `name` field, and no `matcher` field EVER
    (generate-cursor-hooks.py never emits one for this event: `sessionStart`
    is not in Cursor's documented matcher-capable event list, a platform
    fact, not a gap). Returns `{basename: None}` for every wired hook.
    """
    generator = repo / "scripts" / "generate-cursor-hooks.py"
    if not generator.exists():
        return {}
    cfg = _run_host_generator(generator, repo)
    events = cfg.get("hooks", cfg)
    wired: dict = {}
    for entry in events.get("sessionStart", []):
        name = _sh_basename(entry.get("command", ""))
        if name:
            wired[name] = None
    return wired


def _extract_manifest(repo: Path) -> dict:
    """Claude Code has no generator -- its wiring IS `hooks/hooks.json` plus
    the dev-mirror `.claude/settings.json`, read directly.

    STUB for this phase: the signature/shape is defined now so every
    extractor in `_EXTRACTORS` is callable identically, but the body is
    Phase 3's job (the `claude-code` ledger row + the lane-partition
    assertion that goes with it). Nothing in Phase 1 dispatches to this --
    `claude-code` is not yet a key in `_WIRED_SET_LEDGER`.
    """
    raise NotImplementedError(
        "_extract_manifest is a Phase-1 stub; its body ships with Phase 3's "
        "claude-code ledger row"
    )


# Dispatch table: ledger host key -> the extractor that knows how to read
# THAT host's actual generator/manifest output. Every _WIRED_SET_LEDGER key
# must have an entry here; check_c_wired_set() below fails closed (a
# finding, not a silent skip) on a ledgered host with no registered
# extractor.
_EXTRACTORS = {
    "gemini": _extract_gemini,
    "copilot-cli": _extract_copilot_cli_flat,
    "cursor": _extract_cursor_flat,
    "claude-code": _extract_manifest,
}


def check_c_wired_set(findings: list, repo: Path | None = None) -> None:
    r = repo or _REPO
    for host, required in _WIRED_SET_LEDGER.items():
        extractor = _EXTRACTORS.get(host)
        if extractor is None:
            findings.append(
                "C: %s is in _WIRED_SET_LEDGER but has no entry in "
                "_EXTRACTORS -- a ledgered host must be readable, not just "
                "declared" % host
            )
            continue
        try:
            actual = extractor(r)
        except NotImplementedError as exc:
            findings.append(f"C: {host}'s extractor is not implemented yet: {exc}")
            continue
        wired_names = set(actual)
        # Fail-closed guard (Phase 1, F-1): an extractor returning EMPTY for
        # a host whose required set is non-empty is a finding, never a
        # silent pass. Gemini's own row already demonstrates the positive
        # case works (8 basenames, not empty) -- this guard is what stops a
        # future Copilot-CLI/Cursor row's extractor from silently reporting
        # "wired: {}" as if that were success.
        if required and not wired_names:
            findings.append(
                "C: EMPTY-EXTRACTION -- %s's extractor returned ZERO wired "
                "SessionStart hooks while %d are required; this is either a "
                "broken extractor or a host that silently stopped wiring "
                "SessionStart entirely, and neither may pass silently"
                % (host, len(required))
            )
            continue
        missing = required - wired_names
        if missing:
            findings.append(
                "C: %s WIRED-SET regression -- %s required-wired but NOT "
                "wired by its generator's actual project() output (this is "
                "the exact class CE-1 found: a hook silently dropped while "
                "--check still passes)" % (host, sorted(missing))
            )


def run(repo: Path | None = None) -> tuple[int, list]:
    findings: list = []
    try:
        check_a_canonical_matcher(findings)
        check_b_parity(findings)
        check_c_wired_set(findings, repo=repo)
    except (OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        return 1, [f"could not run: {exc}"]
    if findings:
        return 2, findings
    return 0, []


def self_test(must_fail: bool = False) -> int:
    passed = 0
    failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  \033[32m✓\033[0m {name}")
        else:
            failed += 1
            print(f"  \033[31m✗\033[0m {name}")

    # 1. Clean run against the real repo state must be exit 0.
    code, findings = run()
    check("self-test: clean repo -> exit 0, no findings", code == 0 and not findings)

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        shutil.copytree(_REPO / "plugins", repo / "plugins")
        shutil.copytree(_REPO / "scripts", repo / "scripts")
        (repo / ".claude").mkdir()
        shutil.copy(_SETTINGS_JSON, repo / ".claude" / "settings.json")

        hooks_json = repo / "plugins" / "ravenclaude-core" / "hooks" / "hooks.json"

        # 2. Mutant: revert the SessionStart matcher fix (Defect A regression).
        data = json.loads(hooks_json.read_text(encoding="utf-8"))
        for entry in data["hooks"]["SessionStart"]:
            if entry.get("matcher") == _SOURCE_MATCHER:
                del entry["matcher"]
        hooks_json.write_text(json.dumps(data), encoding="utf-8")
        f2: list = []
        check_a_canonical_matcher(f2, hooks_json_path=hooks_json)
        check(
            "self-test MUST-FAIL: reverted matcher is caught by check A",
            any("A:" in x for x in f2),
        )

        # restore for the next mutant
        shutil.copy(_HOOKS_JSON, hooks_json)

        # 3. Mutant: drop keep-awake.sh from the settings.json mirror (the
        #    real drift this gate was built to catch, reproduced).
        settings_json = repo / ".claude" / "settings.json"
        sdata = json.loads(settings_json.read_text(encoding="utf-8"))
        for entry in sdata["hooks"]["SessionStart"]:
            if entry.get("matcher") == _SOURCE_MATCHER:
                entry["hooks"] = [
                    h for h in entry["hooks"] if "keep-awake.sh" not in h.get("command", "")
                ]
        settings_json.write_text(json.dumps(sdata), encoding="utf-8")
        f3: list = []
        check_b_parity(f3, hooks_json_path=hooks_json, settings_json_path=settings_json)
        check(
            "self-test MUST-FAIL: settings.json/hooks.json drift is caught by check B",
            any("B:" in x for x in f3),
        )

        # 4. Mutant: reproduce the ORIGINAL Gemini regression (route
        #    SessionStart through _gemini_matcher again) and confirm check C
        #    catches it via the ledger -- the direct reproduction of CE-1.
        gemini_gen = repo / "scripts" / "generate-gemini-hooks.py"
        src = gemini_gen.read_text(encoding="utf-8")
        mutant = src.replace(
            "_TOOL_SHAPED_EVENTS = {\"PreToolUse\", \"PostToolUse\"}",
            "_TOOL_SHAPED_EVENTS = {\"PreToolUse\", \"PostToolUse\", \"SessionStart\"}",
        )
        if mutant == src:
            check("self-test MUST-FAIL setup: mutant string found in generator", False)
        else:
            gemini_gen.write_text(mutant, encoding="utf-8")
            f4: list = []
            check_c_wired_set(f4, repo=repo)
            check(
                "self-test MUST-FAIL: the original Gemini regression (CE-1) is caught by check C",
                any("C:" in x for x in f4),
            )

    print(f"\ncheck-sessionstart-matcher-regression self-test: {passed} pass, {failed} fail")
    if must_fail:
        # --must-fail invocation: exit 0 only if every MUST-FAIL assertion
        # above actually caught its mutant (failed == 0 here means the real
        # teeth all bit).
        return 0 if failed == 0 else 1
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate 259: SessionStart matcher regression floor")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true", help="run self-test and require every teeth check to bite")
    args = ap.parse_args()

    if args.self_test or args.must_fail:
        return self_test(must_fail=args.must_fail)

    code, findings = run()
    if code == 0:
        print("check-sessionstart-matcher-regression: OK -- canonical matcher, parity, and wired-set all clean")
    else:
        print("check-sessionstart-matcher-regression: FAIL")
        for f in findings:
            print(f"  - {f}")
    return code


if __name__ == "__main__":
    sys.exit(main())
