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
  D. Ledger COMPLETENESS (Phase 5, sessionstart-safeguards-multihost): makes
     the ledger self-extending. Enumerates every host lane actually present
     on the filesystem (an adapter, a generator, or a host-support.json row)
     and asserts each is classified -- present in _WIRED_SET_LEDGER OR
     _UNSUPPORTED_HOSTS -- with silence itself a finding. A converse pass
     then re-checks every _UNSUPPORTED_HOSTS entry's OWN recorded promotion
     criteria against disk, so a classified-but-now-stale exclusion (e.g.
     grok gaining a real adapter after this phase ships) is caught on every
     run rather than becoming a permanent, never-revisited fixture.

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
_HOST_SUPPORT_JSON = _REPO / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"

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

# The full canonical SessionStart hook set, across ALL matcher lanes (the
# `startup|resume|clear|fork` group, the `startup`-only group, and the
# `compact` group) -- 9 hooks as of this writing, read directly off
# hooks.json's own SessionStart block (see check_a_canonical_matcher's
# _SOURCE_HOOKS/_COMPACT_HOOK, which only cover two of the three groups).
_HANDOFF_HOOK = "handoff-successor-ack.sh"
_ALL_SESSIONSTART_HOOKS = _SOURCE_HOOKS | {_COMPACT_HOOK, _HANDOFF_HOOK}

# The declared per-host WIRED-SET ledger. Each entry:
#   "required"          -- must be wired, regardless of matcher precision
#                           (that's check A/generator-specific); this is
#                           `_ALL_SESSIONSTART_HOOKS` MINUS whatever that
#                           host's own generator's `_SKIP` dict legitimately
#                           excludes -- computed once, by hand, against each
#                           generator's actual `_SKIP` keys at the time this
#                           row was written (Gemini skips
#                           handoff-successor-ack.sh; Copilot-CLI and Cursor
#                           skip neither of the two SessionStart-lane hooks
#                           in their `_SKIP` dicts, so their required sets
#                           are the full 9). This is DELIBERATELY NOT
#                           recomputed live against a generator's CURRENT
#                           `_SKIP` set at check time -- check C exists
#                           specifically to catch a hook silently added to
#                           `_SKIP` with a plausible-sounding reason (CE-1,
#                           see the module docstring); a live "hooks.json
#                           minus _SKIP" derivation would make that class of
#                           regression invisible again, one level up (F-2's
#                           own failure shape, reproduced by the fix meant to
#                           prevent it).
#   "source"             -- where this host's wiring truth comes from.
#   "matcher_fidelity"   -- "exact" | "none-by-platform" | "none-unverified"
#                           (plan.md Sec 1.2); asserted bidirectionally by
#                           check_c_matcher_fidelity() below.
#
# A host not listed here is not asserted on (Claude Code/Codex are Phases
# 3/4's job; a host not ledgered at all is Phase 5's completeness scan).
_WIRED_SET_LEDGER = {
    "gemini": {
        "source": "generator",
        # handoff-successor-ack.sh is explicitly _SKIP'd by
        # generate-gemini-hooks.py ("SessionStart startup handshake (file
        # write). Gemini SessionStart ...") -- excluded from `required`
        # accordingly, matching Phase 1's original hand-typed row exactly.
        "required": _SOURCE_HOOKS | {_COMPACT_HOOK},
        "matcher_fidelity": "none-unverified",
        # Phase 8: declared, never measured. Gemini has no Tier D mechanism
        # (plan.md Sec 1.3 -- "Gemini CLI presence on the host is not
        # established") and no live Tier A probe was run against it either;
        # this is `_rc_canary_declared_tier`'s own value for gemini, ported
        # here so `rc hooks selftest` has ONE source of truth for the
        # settled/reportable tier per host (see the copilot-cli entry below
        # for the case where the two sources diverge and why).
        "runtime_tier": "A",
    },
    "copilot-cli": {
        "source": "generator",
        # generate-copilot-hooks.py's _SKIP has no entry for any of the 9
        # SessionStart-lane hooks (its two skips are agent-dispatch-
        # evaluator.sh/SubagentStart and route-decision-review.sh/
        # AskUserQuestion) -- required is the full canonical set.
        "required": _ALL_SESSIONSTART_HOOKS,
        "matcher_fidelity": "exact",
        # Phase 8 (sessionstart-safeguards-multihost) -- the settled, MEASURED
        # value, deliberately NOT the same as `_rc_canary_declared_tier`'s
        # generic aspirational classification in
        # plugins/ravenclaude-core/hooks/_host-canary.sh, which still returns
        # "D" for copilot ("D-if-present, else A", plan.md Sec 1.3). Phase 7
        # measured it TWICE, independently, against a live `copilot -p` spawn
        # with a positive control on the spawn mechanism itself
        # (hooks/tests/test-tier-d-canary.sh A7.5): the spawn genuinely runs
        # and returns real output, but SessionStart does NOT fire from
        # `.github/hooks/*.json` under `copilot -p` -- so "if present" is
        # false in practice, not merely unverified. Phase 5 explicitly
        # deferred recording this here; `rc hooks selftest` (Phase 8) reads
        # THIS field as the declared/reportable tier for its "tier" column
        # and its anti-degradation check, and separately compares it against
        # `_rc_canary_declared_tier`'s aspirational "D" to print the
        # "D unverified" caveat on an otherwise-plain PASS -- so a reader
        # never mistakes a settled A for "D was never even attempted."
        "runtime_tier": "A",
    },
    "cursor": {
        "source": "generator",
        # generate-cursor-hooks.py's _SKIP likewise has no entry for any of
        # the 9 SessionStart-lane hooks -- required is the full set.
        "required": _ALL_SESSIONSTART_HOOKS,
        "matcher_fidelity": "none-by-platform",
        # Phase 8: declared, never measured (plan.md Sec 1.3 -- no verified
        # non-interactive one-shot invocation, and Cursor fails OPEN on a
        # malformed hook response, so an inconclusive Tier D result there
        # would be actively misleading). Matches `_rc_canary_declared_tier`.
        "runtime_tier": "A",
    },
    "claude-code": {
        "source": "manifest",
        # Claude Code has no generator and no _SKIP mechanism to exclude
        # through -- its wiring IS hooks/hooks.json plus the dev-mirror
        # .claude/settings.json, directly (checks A and B already assert
        # both files). required is the full canonical set; nothing is
        # legitimately excludable the way a generator's _SKIP can be.
        "required": _ALL_SESSIONSTART_HOOKS,
        "matcher_fidelity": "exact",
        # Phase 3 only: claude-code's extractor (_extract_manifest) exposes
        # the REAL per-hook matcher STRING (not just presence/absence, the
        # way copilot-cli's fidelity check treats it) -- so its wiring can
        # additionally be checked for LANE PARTITION (which basenames sit
        # under which matcher group), via check_c_lane_partition below. Not
        # set on the copilot-cli/cursor rows above -- out of Phase 3's
        # scope; adding it there is a later phase's call, not this one's.
        "lane_partitioned": True,
        # Phase 8: MEASURED, not merely declared. A7.1
        # (hooks/tests/test-tier-d-canary.sh) drove a real `claude -p`
        # against a scratch project's planted SessionStart hook and observed
        # the marker fire -- the positive control this plan requires before
        # trusting a "D" claim at all (plan.md Sec 1.3's own worked example).
        "runtime_tier": "D",
    },
    "codex": {
        "source": "generator",
        # generate-codex-hooks.py's SessionStart lane is a full derivation off
        # hooks.json's own SessionStart block (Phase 4, sessionstart-safeguards-
        # multihost) -- unlike copilot-cli/cursor/gemini, it has NO _SKIP entry
        # for any of the 9 SessionStart-lane hooks (its ~25 _SKIP entries are all
        # PreToolUse/PostToolUse/Stop/other-event hooks, deliberately out of this
        # generator's SessionStart-only scope) -- required is the full canonical
        # set, same as claude-code/copilot-cli/cursor.
        "required": _ALL_SESSIONSTART_HOOKS,
        # Codex speaks the native Claude Code hook contract, so its generator can
        # (and does) carry a per-entry matcher on every wired SessionStart hook,
        # exactly like claude-code and copilot-cli -- "exact" was simply absent
        # until Phase 4 wired it, not a platform limitation the way cursor's
        # "none-by-platform" or gemini's "none-unverified" are.
        "matcher_fidelity": "exact",
        # Phase 8: declared, never measured -- Tier D is blocked by a real
        # platform gate (Codex tracks hook trust by hash and skips untrusted
        # hooks, MH-17; a freshly-written scratch config is untrusted by
        # construction, so a spawned Codex session would report "did not
        # fire" for a CORRECT wiring). Matches `_rc_canary_declared_tier`.
        "runtime_tier": "A",
    },
}

# Phase 5 (sessionstart-safeguards-multihost) -- the ledger completeness
# scan's join point. This section makes the ledger self-extending: every
# host lane actually wired on disk (an adapter, a generator, or a
# host-support.json row) must appear in _WIRED_SET_LEDGER above OR here in
# _UNSUPPORTED_HOSTS -- silence (present on disk, absent from both) is a
# finding (check_d_ledger_completeness below), never a silent pass.
#
# A raw filesystem/host-support.json host token does not always match the
# ledger's own key spelling (the ledger key is "copilot-cli"; the adapter is
# "copilot-hook-adapter.sh", the generator is "generate-copilot-hooks.py",
# and host-support.json's own row key is "copilot") -- _HOST_ALIASES is the
# one place that reconciliation lives, so a raw "copilot" resolves to the
# same identity the ledger and _UNSUPPORTED_HOSTS both use.
_HOST_ALIASES = {
    "copilot": "copilot-cli",
}


def _canonical_host(raw: str) -> str:
    return _HOST_ALIASES.get(raw, raw)


# Grok -- decided here, loudly (plan.md Sec 4, the "Grok -- the explicit
# ruling" section, claims-table row 8). EXCLUDED from _WIRED_SET_LEDGER;
# INCLUDED, by name and with a reason, here. Basis (re-confirmed live this
# session against the ACTUAL 7-row host-support.json components.hooks dict --
# claude-code, copilot, codex, cursor, gemini, aider, windsurf -- grok is
# genuinely absent, not merely `supported: false`): no
# grok-hook-adapter.sh, no generate-grok-hooks.py, no `grok` row in
# host-support.json's components.hooks, and scripts/ravenclaude's --host arm
# enumerates `copilot | codex | cursor | aider | gemini` and does not know
# the word. Grok appears only as a MODEL-ROUTING key
# (substrate-tier-map.json, agent-routing-matrix.json) -- a distinct concern
# that must not be conflated (scope.md's own instruction, restated in
# plan.md Sec 4).
#
# `promotion_criteria` is deliberately a list of exactly the four criteria
# plan.md Sec 4 names, in that fixed order -- check_d_converse_promotion_
# criteria below is positionally keyed to this order via
# _promotion_criterion_met(index, ...), so reordering this list without
# updating that function's four branches would silently mis-check a
# criterion. When ANY of these four exist, the converse check below fires a
# PROMOTION-CRITERIA-MET finding automatically -- nobody has to remember to
# revisit this exclusion, and it cannot silently go stale once it ships.
_UNSUPPORTED_HOSTS = {
    "grok": {
        "reason": (
            "no grok-hook-adapter.sh, no generate-grok-hooks.py, and no "
            "`grok` row in host-support.json's components.hooks (verified "
            "this session against the live 7-row dict: claude-code, "
            "copilot, codex, cursor, gemini, aider, windsurf -- grok is "
            "absent, not merely supported:false). Grok appears only as a "
            "model-routing key (substrate-tier-map.json, "
            "agent-routing-matrix.json), a distinct concern that must not "
            "be conflated with host support (plan.md Sec 4)."
        ),
        "promotion_criteria": [
            "a grok row in host-support.json with supported: true and a dated basis",
            "a grok-hook-adapter.sh with a sessionstart mode",
            "a generate-grok-hooks.py sibling with the _SKIP/--check contract",
            "an --host grok installer lane",
        ],
        "recorded": "2026-09-03",
    },
}


def _discover_host_lanes(repo: Path) -> dict:
    """Enumerate every host lane actually present on the filesystem, per
    Phase 5's four discovery sources: `hooks/*-hook-adapter.sh`,
    `hooks/codex-hook-env.sh` (codex's env-shim, NOT an envelope adapter --
    see the CLAUDE.md milestone explaining why no codex-hook-adapter.sh
    exists), `scripts/generate-*-hooks.py`, and host-support.json's
    `components.hooks` rows with `supported: true`. Returns
    {canonical_host: {evidence source labels}} -- the evidence set is for
    finding-message diagnostics only; membership is what
    check_d_ledger_completeness asserts on.
    """
    discovered: dict = {}

    def _add(raw: str, source: str) -> None:
        discovered.setdefault(_canonical_host(raw), set()).add(source)

    hooks_dir = repo / "plugins" / "ravenclaude-core" / "hooks"
    if hooks_dir.is_dir():
        for f in sorted(hooks_dir.glob("*-hook-adapter.sh")):
            _add(f.name[: -len("-hook-adapter.sh")], "hooks/%s" % f.name)
        if (hooks_dir / "codex-hook-env.sh").exists():
            _add("codex", "hooks/codex-hook-env.sh")

    scripts_dir = repo / "scripts"
    if scripts_dir.is_dir():
        for f in sorted(scripts_dir.glob("generate-*-hooks.py")):
            m = re.match(r"generate-(.+)-hooks\.py$", f.name)
            if m:
                _add(m.group(1), "scripts/%s" % f.name)

    hs_path = repo / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"
    if hs_path.exists():
        try:
            data = json.loads(hs_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        for host, row in data.get("components", {}).get("hooks", {}).items():
            if isinstance(row, dict) and row.get("supported") is True:
                _add(host, "host-support.json:components.hooks.%s" % host)

    return discovered


def check_d_ledger_completeness(findings: list, repo: Path | None = None) -> None:
    """Phase 5's join point: every host lane discovered on disk must be
    classified -- present in _WIRED_SET_LEDGER (required-and-wired) OR
    _UNSUPPORTED_HOSTS (deliberately excluded, with a reason). A host on
    disk that is in NEITHER is a finding -- silence is never a pass. This is
    what makes the ledger self-extending: a future host lane (a new
    *-hook-adapter.sh, a new generate-<host>-hooks.py, or a host-support.json
    row flipping to supported:true) is caught the moment it lands, rather
    than waiting for someone to remember to add a ledger row by hand.
    """
    r = repo or _REPO
    for host, sources in sorted(_discover_host_lanes(r).items()):
        if host in _WIRED_SET_LEDGER or host in _UNSUPPORTED_HOSTS:
            continue
        findings.append(
            "D: COMPLETENESS -- %r is wired on disk (%s) but is in NEITHER "
            "_WIRED_SET_LEDGER nor _UNSUPPORTED_HOSTS -- silence is a "
            "finding (Phase 5): classify it as one or the other"
            % (host, ", ".join(sorted(sources)))
        )


def check_d_unsupported_entries_valid(findings: list) -> None:
    """A5.4: every _UNSUPPORTED_HOSTS entry must carry a non-empty `reason`
    and a non-empty `promotion_criteria` list -- either being empty is a
    finding (an exclusion with no stated reason, or no way to ever revisit
    it, is exactly the silent-permanent-exclusion failure mode this whole
    mechanism exists to prevent)."""
    for host, entry in sorted(_UNSUPPORTED_HOSTS.items()):
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            findings.append(
                "D: %s's _UNSUPPORTED_HOSTS entry has an empty or missing "
                "'reason'" % host
            )
        criteria = entry.get("promotion_criteria")
        if (
            not isinstance(criteria, list)
            or not criteria
            or not all(isinstance(c, str) and c.strip() for c in criteria)
        ):
            findings.append(
                "D: %s's _UNSUPPORTED_HOSTS entry has an empty, missing, or "
                "malformed 'promotion_criteria' list" % host
            )


def _promotion_criterion_met(index: int, host: str, repo: Path) -> tuple:
    """Returns (met: bool, description: str) for one of the four canonical
    promotion criteria (plan.md Sec 4), by FIXED positional index --
    deliberately independent of the prose stored in an entry's own
    `promotion_criteria[]` (that prose is for a human reader; this is the
    machine-checkable primitive A5.5 asserts against disk for each of the
    four standard criteria, in the order plan.md Sec 4 states them).
    Raises ValueError on an index outside 0..3 (a host that ships MORE than
    the four standard criteria has the extras skipped by the converse check,
    not mis-evaluated against the wrong primitive).
    """
    if index == 0:
        desc = (
            "a %s row in host-support.json with supported:true and a dated "
            "basis" % host
        )
        hs_path = repo / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"
        if not hs_path.exists():
            return False, desc
        try:
            data = json.loads(hs_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False, desc
        row = data.get("components", {}).get("hooks", {}).get(host)
        if not isinstance(row, dict) or row.get("supported") is not True:
            return False, desc
        basis = row.get("basis", "")
        met = bool(isinstance(basis, str) and re.search(r"\d{4}-\d{2}-\d{2}", basis))
        return met, desc
    if index == 1:
        desc = "a %s-hook-adapter.sh with a sessionstart mode" % host
        adapter = repo / "plugins" / "ravenclaude-core" / "hooks" / ("%s-hook-adapter.sh" % host)
        if not adapter.exists():
            return False, desc
        text = adapter.read_text(encoding="utf-8", errors="ignore")
        return bool(re.search(r"^\s*sessionstart\)", text, re.MULTILINE)), desc
    if index == 2:
        desc = "a generate-%s-hooks.py sibling with the _SKIP/--check contract" % host
        gen = repo / "scripts" / ("generate-%s-hooks.py" % host)
        if not gen.exists():
            return False, desc
        text = gen.read_text(encoding="utf-8", errors="ignore")
        return ("_SKIP" in text and "--check" in text), desc
    if index == 3:
        desc = "an --host %s installer lane" % host
        installer = repo / "scripts" / "ravenclaude"
        if not installer.exists():
            return False, desc
        text = installer.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'case\s+"\$host"\s+in\s*\n\s*([a-z0-9_|]+)\)', text)
        return bool(m and host in m.group(1).split("|")), desc
    raise ValueError("unknown promotion criterion index %d" % index)


def check_d_converse_promotion_criteria(findings: list, repo: Path | None = None) -> None:
    """A5.5, MANDATORY (closes G5 red-team Finding F1, HIGH) -- the converse
    assertion. A naive membership-only completeness scan
    (check_d_ledger_completeness above) is a placebo for the exact scenario
    it is named after: once _UNSUPPORTED_HOSTS["grok"] ships as part of this
    phase, it is a PERMANENT FIXTURE in the tree. A future
    grok-hook-adapter.sh landing would be discovered by the completeness
    scan, looked up, found ALREADY CLASSIFIED, and pass -- never
    re-examining whether the classification's own justification still
    holds. This is the second, converse pass: for every _UNSUPPORTED_HOSTS
    entry, verify its OWN recorded promotion_criteria do NOT currently hold
    on disk. If ANY criterion is met, that is itself a finding --
    PROMOTION-CRITERIA-MET, naming the host and the specific criterion
    satisfied -- never a silent pass.
    """
    r = repo or _REPO
    for host, entry in sorted(_UNSUPPORTED_HOSTS.items()):
        criteria = entry.get("promotion_criteria") or []
        for idx, criterion_text in enumerate(criteria):
            try:
                met, desc = _promotion_criterion_met(idx, host, r)
            except ValueError:
                continue  # beyond the 4 standard criteria -- not machine-checked here
            if met:
                findings.append(
                    "D: PROMOTION-CRITERIA-MET -- %s's exclusion from "
                    "_WIRED_SET_LEDGER needs review -- criterion %d (%s) "
                    "now holds on disk (stated as: %r)"
                    % (host, idx + 1, desc, criterion_text)
                )


# Canonical lane -> expected-hook-set partition, read directly off the same
# constants check A itself asserts against (_SOURCE_HOOKS/_COMPACT_HOOK via
# _SOURCE_MATCHER/_COMPACT_MATCHER, plus the startup-only _HANDOFF_HOOK lane
# that check A's own two assertions don't cover). Used only by
# check_c_lane_partition -- check A still owns the direct hooks.json read;
# this is the ledger/extractor-side view of the same partition, framed
# per-hook rather than per-matcher-group so its findings read distinctly
# from check A's.
_LANE_GROUPS = {
    _SOURCE_MATCHER: _SOURCE_HOOKS,
    "startup": {_HANDOFF_HOOK},
    _COMPACT_MATCHER: {_COMPACT_HOOK},
}
_LANE_LABELS = {
    _SOURCE_MATCHER: "source (startup|resume|clear|fork)",
    "startup": "startup-only",
    _COMPACT_MATCHER: "compact",
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
    `{command,timeout}` -- no `name` field, and, TODAY, no `matcher` field
    EVER (generate-cursor-hooks.py never emits one for this event:
    `sessionStart` is not in Cursor's documented matcher-capable event list,
    a platform fact, not a gap). Returns `{basename: matcher_or_None}`,
    reading whatever `matcher` key is actually present rather than
    hardcoding `None` -- Phase 2's matcher-fidelity assertion (Sec 1.2) needs
    to be able to SEE a future regression where the generator starts
    emitting one; a hardcoded `None` here would make that direction
    permanently unfalsifiable (see A2.4).
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
            wired[name] = entry.get("matcher")
    return wired


def _extract_manifest(repo: Path) -> dict:
    """Claude Code has no generator -- its wiring IS `hooks/hooks.json` plus
    the dev-mirror `.claude/settings.json`, read directly (no subprocess, no
    projector to run -- unlike every other extractor in this dispatch
    table). Returns `{basename: matcher}`, exactly like every other
    extractor, so check_c_wired_set/check_c_matcher_fidelity/
    check_c_lane_partition can read it identically.

    Reads BOTH files (Phase 3's explicit ask): `hooks/hooks.json` is treated
    as canonical (it is the plugin-shipped source of truth a consumer
    actually installs), and `.claude/settings.json` is folded in as a
    fallback ONLY for a basename hooks.json itself doesn't carry --
    `setdefault`, never an override. In a healthy tree the two are already
    byte-identical on this axis (check B enforces that), so the fallback
    step is normally a no-op; it exists so a hook present ONLY in the
    dev-mirror still surfaces to check C's ledger checks rather than this
    extractor silently under-reporting relative to what Phase 3's own goal
    calls "the wiring" (hooks.json *plus* the dev-mirror, not hooks.json
    alone).

    Deliberately does NOT re-assert hooks.json<->settings.json parity itself
    -- that is check B's job (see module docstring); re-deriving it here
    would be exactly the kind of duplication Phase 3's task scope forbids.
    """
    hooks_json = repo / "plugins" / "ravenclaude-core" / "hooks" / "hooks.json"
    settings_json = repo / ".claude" / "settings.json"
    wired: dict = {}
    if hooks_json.exists():
        for matcher, names in _session_start_groups(hooks_json).items():
            for name in names:
                wired[name] = matcher
    if settings_json.exists():
        for matcher, names in _session_start_groups(settings_json).items():
            for name in names:
                wired.setdefault(name, matcher)
    return wired


def _codex_target_basename(command: str) -> str:
    """Codex's SessionStart shape wraps every hook as `bash "<shim>"
    "<hooks-dir>/<script>" [args]` -- TWO quoted `.sh`-ending paths per
    command (the shim itself, then the real hook), unlike Copilot/Cursor's
    single-path shape that `_sh_basename` was built for. Naively reusing
    `_sh_basename` here would match the SHIM's own basename
    (`codex-hook-env.sh`), not the target hook, because its regex finds the
    FIRST `.sh` token and the shim path is always quoted first. This instead
    collects every quoted `<...>/<name>.sh` path and takes the LAST one --
    the shim is always first, the real hook (or a trailing bare-word arg
    like `register`, which never ends in `.sh"`) is always last.
    """
    matches = re.findall(r'"[^"]*/([A-Za-z0-9_.-]+\.sh)"', command)
    return matches[-1] if matches else ""


def _extract_codex(repo: Path) -> dict:
    """Codex's SessionStart shape: `hooks.SessionStart[] ->
    {matcher?, hooks:[{type,command}]}` -- grouped by matcher like Gemini's,
    but with NO `name` field at all (like Copilot-CLI/Cursor's flat shapes),
    so the basename has to be read off the assembled `command` string via
    `_codex_target_basename` above. Returns `{basename: matcher_or_None}`.
    """
    generator = repo / "scripts" / "generate-codex-hooks.py"
    if not generator.exists():
        return {}
    cfg = _run_host_generator(generator, repo)
    events = cfg.get("hooks", cfg)
    wired: dict = {}
    for block in events.get("SessionStart", []):
        matcher = block.get("matcher")
        for h in block.get("hooks", []):
            name = _codex_target_basename(h.get("command", ""))
            if name:
                wired[name] = matcher
    return wired


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
    "codex": _extract_codex,
}


def check_c_wired_set(findings: list, repo: Path | None = None) -> None:
    r = repo or _REPO
    for host, entry in _WIRED_SET_LEDGER.items():
        required = entry["required"]
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


_VALID_MATCHER_FIDELITIES = frozenset({"exact", "none-by-platform", "none-unverified"})


def check_c_matcher_fidelity(findings: list, repo: Path | None = None) -> None:
    """plan.md Sec 1.2's bidirectional assertion: a ledgered host's DECLARED
    `matcher_fidelity` must match what its extractor's ACTUAL SessionStart
    output emits, in BOTH directions.

    This is a different axis from check A (which asserts hooks.json's own
    canonical matcher STRING) and from check C's wired-set (which asserts
    WHICH hooks are wired, not what matcher a per-host generator attaches to
    them). A host declared "exact" (a per-entry matcher on every wired hook)
    that starts emitting none is a silent fidelity regression; a host
    declared "none-by-platform"/"none-unverified" that starts emitting one
    is a silent, unreviewed platform-assumption change -- G5 named this
    second direction the one most likely to ship unmutant-tested (A2.4).
    """
    r = repo or _REPO
    for host, entry in _WIRED_SET_LEDGER.items():
        declared = entry.get("matcher_fidelity")
        if declared not in _VALID_MATCHER_FIDELITIES:
            findings.append(
                "C: %s declares matcher_fidelity=%r, not one of %s"
                % (host, declared, sorted(_VALID_MATCHER_FIDELITIES))
            )
            continue
        extractor = _EXTRACTORS.get(host)
        if extractor is None:
            continue  # already reported by check_c_wired_set
        try:
            actual = extractor(r)
        except NotImplementedError:
            continue  # Phase-3-stub host; already reported by check_c_wired_set
        if not actual:
            continue  # EMPTY-EXTRACTION already reported by check_c_wired_set
        matcher_flags = [bool(m) for m in actual.values()]
        all_matchered = all(matcher_flags)
        any_matchered = any(matcher_flags)
        if declared == "exact" and not all_matchered:
            findings.append(
                "C: MATCHER-FIDELITY -- %s declares matcher_fidelity='exact' "
                "but its generator's actual SessionStart output does NOT "
                "carry a per-entry matcher on every wired hook (declared "
                "exact, emitted none)" % host
            )
        elif declared in ("none-by-platform", "none-unverified") and any_matchered:
            findings.append(
                "C: MATCHER-FIDELITY -- %s declares matcher_fidelity=%r (no "
                "matcher expected) but its generator's actual SessionStart "
                "output NOW carries a matcher on at least one wired hook "
                "(declared %s, emitted one)" % (host, declared, declared)
            )


def check_c_lane_partition(findings: list, repo: Path | None = None) -> None:
    """Phase 3: asserts the LANE PARTITION -- which basenames sit under
    which SessionStart matcher group (`startup|resume|clear|fork` vs
    `startup` vs `compact`) -- for any ledgered host that opts in via
    `lane_partitioned: True` (currently `claude-code` only; Phase 2's
    copilot-cli/cursor rows do not set it and are unaffected by this
    check).

    This is a different axis from every other check in this module:

      - check A reads hooks.json DIRECTLY and asserts its own literal
        matcher STRING values, per matcher-group (module docstring, "A.").
        This check goes through the host's EXTRACTOR instead -- the same
        abstraction check_c_wired_set/check_c_matcher_fidelity use -- and
        asserts, per REQUIRED HOOK, that its extracted matcher places it in
        the lane hooks.json's own canonical partition says it belongs to.
        Findings are phrased per-hook ("X is wired under lane Y, belongs in
        lane Z"), never restating check A's per-matcher-group "hook set is
        A, expected B" wording -- so the two remain distinguishable in
        output even though both can (correctly) fire on the same mutant
        (A3.2/A3.3: two independent checks catching one underlying problem
        from different angles is fine; a check silently subsuming the
        other's job is not).
      - check_c_wired_set asserts MEMBERSHIP only (is the hook wired at
        all) -- a hook moved to the wrong matcher group is still "wired",
        so that check cannot see this regression class.
      - check_c_matcher_fidelity asserts PRESENCE/ABSENCE of a matcher only
        (declared "exact" vs emitted none) -- a hook with the wrong matcher
        STILL has *a* matcher, so that check cannot see this class either.

    A hook silently reassigned to a different SessionStart matcher group --
    present, correctly matcher-having, just wired into the wrong lane -- is
    invisible to both of the above and is exactly what this check exists to
    catch.
    """
    r = repo or _REPO
    for host, entry in _WIRED_SET_LEDGER.items():
        if not entry.get("lane_partitioned"):
            continue
        extractor = _EXTRACTORS.get(host)
        if extractor is None:
            continue  # already reported by check_c_wired_set
        try:
            actual = extractor(r)
        except NotImplementedError:
            continue  # stub host; already reported by check_c_wired_set
        if not actual:
            continue  # EMPTY-EXTRACTION already reported by check_c_wired_set
        for lane, expected_hooks in _LANE_GROUPS.items():
            for hook in expected_hooks:
                if hook not in actual:
                    continue  # missing entirely -- already a wired-set finding
                actual_matcher = actual[hook]
                if actual_matcher != lane:
                    findings.append(
                        "C: LANE-PARTITION -- %s's %s is wired under the %s lane "
                        "but belongs in the %s lane per hooks.json's own canonical "
                        "partition -- a hook moved between SessionStart matcher "
                        "groups, not a hook-count or matcher-presence problem"
                        % (
                            host,
                            hook,
                            _LANE_LABELS.get(actual_matcher, repr(actual_matcher)),
                            _LANE_LABELS.get(lane, lane),
                        )
                    )


def run(repo: Path | None = None) -> tuple[int, list]:
    findings: list = []
    try:
        check_a_canonical_matcher(findings)
        check_b_parity(findings)
        check_c_wired_set(findings, repo=repo)
        check_c_matcher_fidelity(findings, repo=repo)
        check_c_lane_partition(findings, repo=repo)
        check_d_ledger_completeness(findings, repo=repo)
        check_d_unsupported_entries_valid(findings)
        check_d_converse_promotion_criteria(findings, repo=repo)
    except (OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        return 1, [f"could not run: {exc}"]
    if findings:
        return 2, findings
    return 0, []


def _copilot_cli_chat_annotation(host_support_path: Path | None = None) -> str:
    """G5 Finding F2 (HIGH, mandatory): force-printed on every invocation
    that reports on `copilot-cli`, so a green run can never be silently
    misread as covering GitHub Copilot CHAT. Sourced verbatim from
    host-support.json's own `components.hooks.copilot.surfaces.chat` note --
    not a comment, a runtime string, so `--must-fail`/CI output and a test
    can both grep for it directly (plan.md Sec 1.4 / A2.7).

    Fails loudly (never silently prints a stale claim) if host-support.json
    itself ever flips `surfaces.chat.supported` to true -- that flip is the
    plan's own stated exit condition ("do not flip ... without a Phase 0
    payload dump"), and this annotation's whole point is to never lag behind
    the fact it quotes.
    """
    data = json.loads((host_support_path or _HOST_SUPPORT_JSON).read_text(encoding="utf-8"))
    chat = data["components"]["hooks"]["copilot"]["surfaces"]["chat"]
    if chat["supported"]:
        raise RuntimeError(
            "host-support.json now declares "
            "components.hooks.copilot.surfaces.chat.supported=true -- the "
            "hardcoded 'chat: unverified' annotation is stale and this "
            "checker (and the Copilot-CLI-only scope boundary it enforces) "
            "needs a Phase-0-payload-dump-informed revisit before it can be "
            "trusted again."
        )
    return "chat: unverified (surfaces.chat.supported=false) -- host-support.json note: %r" % (
        chat["note"],
    )


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

        # 5. Mutant (A2.2, drop, copilot-cli): make generate-copilot-hooks.py
        #    _SKIP keep-awake.sh with a plausible-sounding reason -- the exact
        #    CE-1 shape, on the newly-ledgered host.
        copilot_gen = repo / "scripts" / "generate-copilot-hooks.py"
        src5 = copilot_gen.read_text(encoding="utf-8")
        mutant5 = src5.replace(
            '_SKIP = {\n    "agent-dispatch-evaluator.sh": (',
            '_SKIP = {\n    "keep-awake.sh": ("mutant test -- A2.2",),\n'
            '    "agent-dispatch-evaluator.sh": (',
            1,
        )
        if mutant5 == src5:
            check("self-test MUST-FAIL setup: A2.2 copilot-cli drop mutant string found", False)
        else:
            copilot_gen.write_text(mutant5, encoding="utf-8")
            f5: list = []
            check_c_wired_set(f5, repo=repo)
            check(
                "self-test MUST-FAIL (A2.2, copilot-cli drop): check C names copilot-cli and keep-awake.sh",
                any("copilot-cli" in x and "keep-awake.sh" in x for x in f5),
            )
            copilot_gen.write_text(src5, encoding="utf-8")  # restore -- mutant 7 reuses this file

        # 6. Mutant (A2.2, drop, cursor): same CE-1 shape, the other newly-
        #    ledgered host.
        cursor_gen = repo / "scripts" / "generate-cursor-hooks.py"
        src6 = cursor_gen.read_text(encoding="utf-8")
        mutant6 = src6.replace(
            '_SKIP = {\n    "enforce-layout.sh": (',
            '_SKIP = {\n    "keep-awake.sh": ("mutant test -- A2.2",),\n    "enforce-layout.sh": (',
            1,
        )
        if mutant6 == src6:
            check("self-test MUST-FAIL setup: A2.2 cursor drop mutant string found", False)
        else:
            cursor_gen.write_text(mutant6, encoding="utf-8")
            f6: list = []
            check_c_wired_set(f6, repo=repo)
            check(
                "self-test MUST-FAIL (A2.2, cursor drop): check C names cursor and keep-awake.sh",
                any("cursor" in x and "keep-awake.sh" in x for x in f6),
            )
            cursor_gen.write_text(src6, encoding="utf-8")  # restore -- mutant 8 reuses this file

        # 7. Mutant (A2.3, matcher-strip, copilot-cli): stop emitting the
        #    per-entry matcher entirely. declared 'exact', emitted none.
        src7 = copilot_gen.read_text(encoding="utf-8")
        mutant7 = src7.replace(
            '                if matcher:\n                    item["matcher"] = matcher\n',
            "",
            1,
        )
        if mutant7 == src7:
            check("self-test MUST-FAIL setup: A2.3 matcher-strip mutant string found", False)
        else:
            copilot_gen.write_text(mutant7, encoding="utf-8")
            f7: list = []
            check_c_matcher_fidelity(f7, repo=repo)
            check(
                "self-test MUST-FAIL (A2.3, matcher strip): check C reports MATCHER-FIDELITY for copilot-cli",
                any("MATCHER-FIDELITY" in x and "copilot-cli" in x for x in f7),
            )

        # 8. Mutant (A2.4, the INVERSE direction, cursor): make the generator
        #    start emitting a matcher where none is declared. This is the
        #    direction G4b/G5 flagged as most likely to be skipped -- do not
        #    skip it.
        src8 = cursor_gen.read_text(encoding="utf-8")
        mutant8 = src8.replace(
            'out.setdefault(cursor_event, []).append({"command": cmd, "timeout": 90})',
            'out.setdefault(cursor_event, []).append('
            '{"command": cmd, "timeout": 90, "matcher": "mutant-a2-4"})',
            1,
        )
        if mutant8 == src8:
            check("self-test MUST-FAIL setup: A2.4 matcher-add (inverse) mutant string found", False)
        else:
            cursor_gen.write_text(mutant8, encoding="utf-8")
            f8: list = []
            check_c_matcher_fidelity(f8, repo=repo)
            check(
                "self-test MUST-FAIL (A2.4, matcher add, INVERSE): check C reports MATCHER-FIDELITY for cursor",
                any("MATCHER-FIDELITY" in x and "cursor" in x for x in f8),
            )

        # 9. Mutant (A3.2, claude-code): move dashboard-autostart.sh from the
        #    `startup|resume|clear|fork` group into the `compact` group in a
        #    fixture manifest. Both check A (the existing, unchanged
        #    matcher-value assertion) and the new check_c_lane_partition
        #    must fire -- and A3.3 requires BOTH to fire together, with
        #    check C's finding naming the LANE, not restating check A's own
        #    "hook set is X, expected Y" wording.
        data9 = json.loads(hooks_json.read_text(encoding="utf-8"))
        source_entry9 = next(
            e for e in data9["hooks"]["SessionStart"] if e.get("matcher") == _SOURCE_MATCHER
        )
        compact_entry9 = next(
            e for e in data9["hooks"]["SessionStart"] if e.get("matcher") == _COMPACT_MATCHER
        )
        moved9 = None
        kept9 = []
        for h in source_entry9["hooks"]:
            if "dashboard-autostart.sh" in h.get("command", ""):
                moved9 = h
            else:
                kept9.append(h)
        source_entry9["hooks"] = kept9
        if moved9 is None:
            check(
                "self-test MUST-FAIL setup: A3.2 dashboard-autostart.sh found in the source group",
                False,
            )
        else:
            compact_entry9["hooks"].append(moved9)
            hooks_json.write_text(json.dumps(data9), encoding="utf-8")

            f9a: list = []
            check_a_canonical_matcher(f9a, hooks_json_path=hooks_json)
            f9c: list = []
            check_c_lane_partition(f9c, repo=repo)

            check(
                "self-test MUST-FAIL (A3.2, claude-code lane move): check A fires on the moved hook",
                any("A:" in x for x in f9a),
            )
            check(
                "self-test MUST-FAIL (A3.2, claude-code lane move): check C fires a "
                "LANE-PARTITION finding naming dashboard-autostart.sh and claude-code",
                any(
                    "LANE-PARTITION" in x and "dashboard-autostart.sh" in x and "claude-code" in x
                    for x in f9c
                ),
            )
            check(
                "self-test A3.3 (no overlap-suppression): check A still fired "
                "(not silently subsumed by check C firing)",
                len(f9a) > 0,
            )
            check(
                "self-test A3.3 (no overlap-suppression): check C still fired "
                "(not silently subsumed by check A firing)",
                len(f9c) > 0,
            )
            check(
                "self-test (findings distinguishable): check A's finding text does "
                "NOT contain check C's LANE-PARTITION marker",
                not any("LANE-PARTITION" in x for x in f9a),
            )
            check(
                "self-test (findings distinguishable): check C's finding text does "
                "NOT restate check A's 'hook set is' wording",
                not any("hook set is" in x for x in f9c),
            )

            # restore before the next block reads a clean hooks_json again
            hooks_json.write_text(_HOOKS_JSON.read_text(encoding="utf-8"), encoding="utf-8")

        # 10. Mutant (A4.4, codex): drop keep-awake.sh from the generator's
        #     SessionStart derivation -- the CE-1 shape, on the newly-ledgered
        #     codex host (Phase 4).
        codex_gen = repo / "scripts" / "generate-codex-hooks.py"
        src10 = codex_gen.read_text(encoding="utf-8")
        mutant10 = src10.replace(
            "            args = _extra_args(command, script)\n"
            '            items.append(_cmd(shim, hooks_dir, script, args))\n'
            "            wired.append(script)\n",
            '            if script == "keep-awake.sh":\n'
            "                continue\n"
            "            args = _extra_args(command, script)\n"
            '            items.append(_cmd(shim, hooks_dir, script, args))\n'
            "            wired.append(script)\n",
            1,
        )
        if mutant10 == src10:
            check("self-test MUST-FAIL setup: A4.4 codex keep-awake.sh drop mutant string found", False)
        else:
            codex_gen.write_text(mutant10, encoding="utf-8")
            f10: list = []
            check_c_wired_set(f10, repo=repo)
            check(
                "self-test MUST-FAIL (A4.4, codex drop): check C names codex and keep-awake.sh",
                any("codex" in x and "keep-awake.sh" in x for x in f10),
            )
            codex_gen.write_text(src10, encoding="utf-8")  # restore -- mutant 11 reuses this file

        # 11. Mutant (A4.5, THE F-2 REGRESSION, codex -- the one this whole
        #     phase exists for): revert generate-codex-hooks.py's SessionStart
        #     lane back to the ORIGINAL pre-Phase-4 2-hook, matcher-less
        #     hand-list -- a FIXTURE mutation of the generator itself (not the
        #     supported/tested RC_CODEX_SESSIONSTART_LEGACY escape hatch),
        #     simulating a reverted fix. Must fire BOTH a missing-hooks
        #     (WIRED-SET) finding AND a MATCHER-FIDELITY finding -- proving the
        #     gate would have caught the live defect that shipped for real
        #     (Codex wired only 2 of 9 SessionStart hooks, no matcher, so
        #     capability-orientation.sh and thing-denial-kb-recall.sh re-fired
        #     on every mid-conversation compaction, the PR #1084 defect).
        src11 = codex_gen.read_text(encoding="utf-8")
        mutant11 = src11.replace(
            '    for group in manifest.get("hooks", {}).get("SessionStart", []):\n'
            '        matcher = group.get("matcher")\n',
            "    return _legacy_sessionstart(shim, hooks_dir)  # A4.5 must-fail mutant\n"
            '    for group in manifest.get("hooks", {}).get("SessionStart", []):\n'
            '        matcher = group.get("matcher")\n',
            1,
        )
        if mutant11 == src11:
            check("self-test MUST-FAIL setup: A4.5 codex SessionStart-revert mutant string found", False)
        else:
            codex_gen.write_text(mutant11, encoding="utf-8")
            f11: list = []
            check_c_wired_set(f11, repo=repo)
            check_c_matcher_fidelity(f11, repo=repo)
            check(
                "self-test MUST-FAIL (A4.5, THE F-2 REGRESSION, codex): check C fires a "
                "WIRED-SET (missing-hooks) finding naming codex",
                any("WIRED-SET" in x and "codex" in x for x in f11),
            )
            check(
                "self-test MUST-FAIL (A4.5, THE F-2 REGRESSION, codex): check C ALSO fires a "
                "MATCHER-FIDELITY finding naming codex -- both findings, not just one",
                any("MATCHER-FIDELITY" in x and "codex" in x for x in f11),
            )
            codex_gen.write_text(src11, encoding="utf-8")  # restore

        # 12. Phase 5 / A5.1 (positive controls): the real, shipped state --
        #     all 5 hosts wired-and-ledgered, grok excluded-and-classified,
        #     both entry-validity and the converse pass clean.
        check(
            "self-test (A5.1): all 5 real hosts are in _WIRED_SET_LEDGER",
            {"gemini", "copilot-cli", "cursor", "claude-code", "codex"} <= set(_WIRED_SET_LEDGER),
        )
        check(
            "self-test (A5.1): grok is in _UNSUPPORTED_HOSTS, not _WIRED_SET_LEDGER",
            "grok" in _UNSUPPORTED_HOSTS and "grok" not in _WIRED_SET_LEDGER,
        )
        f12clean: list = []
        check_d_ledger_completeness(f12clean, repo=repo)
        check(
            "self-test (A5.1): completeness scan against the real fixture tree is clean",
            not f12clean,
        )

        # 13. Mutant (A5.2, MUST-FAIL, no-entry case): plant a
        #     grok-hook-adapter.sh stub in the fixture tree with NO ledger
        #     entry ANYWHERE (temporarily pop _UNSUPPORTED_HOSTS's real grok
        #     row, simulating a host that was never classified at all) ->
        #     the completeness scan must name grok.
        grok_adapter_a52 = repo / "plugins" / "ravenclaude-core" / "hooks" / "grok-hook-adapter.sh"
        grok_adapter_a52.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\ncase \"$1\" in\n  sessionstart) ;;\nesac\n",
            encoding="utf-8",
        )
        saved_grok_entry_a52 = _UNSUPPORTED_HOSTS.pop("grok", None)
        try:
            f13: list = []
            check_d_ledger_completeness(f13, repo=repo)
            check(
                "self-test MUST-FAIL (A5.2, no-entry case): completeness scan "
                "names grok when it is in NEITHER _WIRED_SET_LEDGER nor "
                "_UNSUPPORTED_HOSTS",
                any("grok" in x and "COMPLETENESS" in x for x in f13),
            )
        finally:
            if saved_grok_entry_a52 is not None:
                _UNSUPPORTED_HOSTS["grok"] = saved_grok_entry_a52
            grok_adapter_a52.unlink(missing_ok=True)  # revert -- confirm the fixture tree is clean
        f13_clean: list = []
        check_d_ledger_completeness(f13_clean, repo=repo)
        check(
            "self-test (A5.2 cleanup verified): after reverting the stub + "
            "restoring the ledger entry, the completeness scan is clean again",
            not f13_clean,
        )

        # 14. Mutant (A5.3, MUST-FAIL, inverse): delete the `cursor` ledger
        #     row (in the FIXTURE ledger dict, not the real file on disk)
        #     while cursor-hook-adapter.sh still exists on disk -> the
        #     completeness scan must name cursor.
        saved_cursor_entry_a53 = _WIRED_SET_LEDGER.pop("cursor", None)
        try:
            f14: list = []
            check_d_ledger_completeness(f14, repo=repo)
            check(
                "self-test MUST-FAIL (A5.3, ledger-row-deleted inverse): "
                "completeness scan names cursor when its row is removed from "
                "_WIRED_SET_LEDGER while cursor-hook-adapter.sh still exists "
                "on disk",
                any("cursor" in x and "COMPLETENESS" in x for x in f14),
            )
        finally:
            if saved_cursor_entry_a53 is not None:
                _WIRED_SET_LEDGER["cursor"] = saved_cursor_entry_a53
        f14_clean: list = []
        check_d_ledger_completeness(f14_clean, repo=repo)
        check(
            "self-test (A5.3 cleanup verified): after restoring the cursor "
            "ledger row, the completeness scan is clean again",
            not f14_clean,
        )

        # 15. Mutant (A5.4): an _UNSUPPORTED_HOSTS entry with an empty
        #     `reason` or empty `promotion_criteria` must be a finding;
        #     the REAL grok entry (non-empty both) must NOT be.
        saved_grok_entry_a54 = _UNSUPPORTED_HOSTS["grok"]
        _UNSUPPORTED_HOSTS["grok"] = {**saved_grok_entry_a54, "reason": ""}
        try:
            f15a: list = []
            check_d_unsupported_entries_valid(f15a)
            check(
                "self-test MUST-FAIL (A5.4, empty reason): flagged",
                any("grok" in x and "reason" in x for x in f15a),
            )
        finally:
            _UNSUPPORTED_HOSTS["grok"] = saved_grok_entry_a54
        _UNSUPPORTED_HOSTS["grok"] = {**saved_grok_entry_a54, "promotion_criteria": []}
        try:
            f15b: list = []
            check_d_unsupported_entries_valid(f15b)
            check(
                "self-test MUST-FAIL (A5.4, empty promotion_criteria): flagged",
                any("grok" in x and "promotion_criteria" in x for x in f15b),
            )
        finally:
            _UNSUPPORTED_HOSTS["grok"] = saved_grok_entry_a54
        f15c: list = []
        check_d_unsupported_entries_valid(f15c)
        check(
            "self-test (A5.4 positive control): the REAL grok entry has "
            "non-empty reason + promotion_criteria and produces no finding",
            not f15c,
        )

        # 16. Mutant (A5.5, THE CONVERSE MUTANT -- G5 red-team Finding F1,
        #     HIGH -- do not approximate this): plant a grok-hook-adapter.sh
        #     stub carrying a `sessionstart)` mode ALONGSIDE the existing,
        #     REAL, shipped _UNSUPPORTED_HOSTS["grok"] entry (i.e. simulate
        #     the actual future state this phase ships: the entry is present
        #     and classified, exactly as shipped, AND a real adapter file now
        #     ALSO exists) -> the converse check must STILL fire, with a
        #     PROMOTION-CRITERIA-MET finding naming grok and criterion 2 (a
        #     grok-hook-adapter.sh with a sessionstart mode) -- proving the
        #     self-auditing property actually holds, not just is claimed.
        grok_adapter_a55 = repo / "plugins" / "ravenclaude-core" / "hooks" / "grok-hook-adapter.sh"
        grok_adapter_a55.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'mode="$1"\n'
            'case "$mode" in\n'
            "  sessionstart)\n"
            "    echo '{}'\n"
            "    ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        try:
            f16: list = []
            check_d_converse_promotion_criteria(f16, repo=repo)
            check(
                "self-test MUST-FAIL (A5.5, THE CONVERSE MUTANT): converse "
                "check fires PROMOTION-CRITERIA-MET naming grok + criterion 2 "
                "when its own criterion 2 now holds on disk, even though the "
                "entry is already present and classified",
                any(
                    "PROMOTION-CRITERIA-MET" in x
                    and "grok" in x
                    and "criterion 2" in x
                    for x in f16
                ),
            )
            check(
                "self-test (A5.5): criteria 1/3/4 do NOT fire (only the "
                "planted criterion 2 is actually met) -- the check "
                "discriminates per-criterion, it does not blanket-flag the host",
                not any(
                    ("criterion 1" in x or "criterion 3" in x or "criterion 4" in x)
                    for x in f16
                ),
            )
        finally:
            grok_adapter_a55.unlink(missing_ok=True)  # revert -- confirm the fixture tree is clean
        f16_clean: list = []
        check_d_converse_promotion_criteria(f16_clean, repo=repo)
        check(
            "self-test (A5.5 cleanup verified): after reverting the "
            "grok-hook-adapter.sh stub, the converse check reports clean "
            "again -- the real tree is clean",
            not f16_clean,
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
    # Force-printed on EVERY invocation that reports on copilot-cli,
    # independent of pass/fail (A2.7, G5 Finding F2) -- never conditional on
    # a clean run, since the scope limit it states is true regardless.
    if "copilot-cli" in _WIRED_SET_LEDGER:
        print(_copilot_cli_chat_annotation())
    return code


if __name__ == "__main__":
    sys.exit(main())
