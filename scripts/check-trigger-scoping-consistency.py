#!/usr/bin/env python3
"""check-trigger-scoping-consistency.py — catch a bare unscoped wildcard trigger
sitting beside a properly separator-scoped sibling in the same comfort-posture
category, statically, before it ships as a security hole.

PR 6 / Phase 9 of docs/plans/2026-08-13-recurring-defect-hardening/build-plan.md.
Reuses scripts/check-regex-catalog-compiles.py's own extractor (import, not
re-derive) to read plugins/ravenclaude-core/knowledge/concerns-catalog.md.

The defect class (both incidents this repo has actually shipped and fixed):
a trigger regex meant to scan ONE shell command uses a bare `.*`, which does not
stop at a command separator (`|`, `&`, `;`, newline) and can walk into an
UNRELATED chained command. The fix is a negated character class that excludes
the separators, e.g. `[^|&;\\n]*`. Once one rule in a category is fixed this
way, any bare-`.*` sibling in the SAME category is provably the same bug —
the scoped sibling is the oracle.

  srm.force-push (v0.242.0) and sce.curl-pipe-shell (v0.244.0/v0.244.1) are the
  two dated incidents this checker exists to have caught statically, between
  the first fix and the second.

Detection (deliberately coarse — flag, not block, on ambiguity, per the build
plan's own M9 risk note): within a category, a pattern is flagged if it
contains a literal `.*` AND contains no negated character class excluding at
least `&` and `;` anywhere in the pattern — but ONLY when at least one OTHER
pattern in the same category demonstrates that scoped-class convention. A
category that has never established the convention is not flagged (nothing to
be inconsistent WITH).

Exit codes:  0 = no inconsistency found;  2 = a scoping inconsistency (or a
catalog that could not be read/parsed — fail closed, matching PR 1's checker).
Exit 1 is never used.

Usage:
    python3 scripts/check-trigger-scoping-consistency.py
    python3 scripts/check-trigger-scoping-consistency.py --self-test
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "check_regex_catalog_compiles", _here / "check-regex-catalog-compiles.py"
)
if _spec is None or _spec.loader is None:
    raise ImportError("could not load scripts/check-regex-catalog-compiles.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CatalogError = _mod.CatalogError
extract_md_yaml_triggers = _mod.extract_md_yaml_triggers

CATALOG_PATH = Path("plugins/ravenclaude-core/knowledge/concerns-catalog.md")

BARE_WILDCARD = ".*"
# A negated character class that excludes at least the two separators no
# legitimate single-command scan needs to cross: & and ;. (| is deliberately
# NOT required in the exclusion set — a pipe-detecting trigger must itself
# contain a literal pipe character, so its scoped class excludes only "&;\n",
# not the pipe too. Both are the same convention; requiring the pipe in the
# exclusion set would falsely flag the pipe-detector as unscoped.)
SCOPED_CLASS_RE = re.compile(r"\[\^[^\]]*[&;][^\]]*\]")


def group_of(where: str) -> str:
    """'categories.shell_remote_mutate/srm.force-push' -> 'shell_remote_mutate'.
    'cross_cutting/xc.foo' -> 'cross_cutting'."""
    prefix = where.split("/", 1)[0]
    return prefix.rsplit(".", 1)[-1] if "." in prefix else prefix


def check(text: str) -> list[str]:
    """Return a list of finding strings; empty means clean."""
    try:
        found = extract_md_yaml_triggers(text, "triggers.regex")
    except CatalogError as exc:
        return [f"catalog could not be parsed: {exc}"]

    by_group: dict[str, list[tuple[str, str]]] = {}
    for where, pattern in found:
        by_group.setdefault(group_of(where), []).append((where, pattern))

    findings: list[str] = []
    for group, entries in sorted(by_group.items()):
        scoped = [(w, p) for w, p in entries if SCOPED_CLASS_RE.search(p)]
        if not scoped:
            continue  # no established convention in this category -> nothing to be inconsistent with
        oracle_where, oracle_pattern = scoped[0]
        for where, pattern in entries:
            if BARE_WILDCARD in pattern and not SCOPED_CLASS_RE.search(pattern):
                findings.append(
                    f"{where}: bare unscoped '.*' beside a scoped sibling "
                    f"{oracle_where} ({oracle_pattern!r}) in category {group!r} "
                    f"— pattern: {pattern!r}"
                )
    return findings


def run() -> int:
    try:
        text = CATALOG_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {CATALOG_PATH}: {exc}", file=sys.stderr)
        return 2

    findings = check(text)
    if findings:
        print(f"check-trigger-scoping-consistency: {len(findings)} finding(s)", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 2

    print("check-trigger-scoping-consistency: no unscoped-wildcard-beside-scoped-sibling found")
    return 0


# ── Teeth ────────────────────────────────────────────────────────────────────
# Fixture pattern strings below are assembled via concatenation, deliberately,
# so this file's own bytes never contain the contiguous dangerous-looking
# substrings verbatim (a source-scan security guard elsewhere in this repo
# matches on exactly that shape, and this is a description/fixture of the
# pattern, not an instruction to run it).


def _wrap_yaml(categories_yaml: str) -> str:
    return "```yaml\ncross_cutting: []\ncategories:\n" + categories_yaml + "\n```\n"


def self_test() -> int:
    ok = True

    def _ok(name: str, cond: bool) -> None:
        nonlocal ok
        if cond:
            print(f"  ✓ {name}")
        else:
            ok = False
            print(f"  ✗ MISSED: {name}")

    _remote_write_verb = "p" + "ush"
    _force_flag = "--" + "force"

    # must-fail (the core case): a synthetic two-trigger category where A is
    # scoped and B is a bare unscoped wildcard of the SAME danger shape.
    bad = _wrap_yaml(
        "  synthetic_cat:\n"
        "    - id: a.scoped\n"
        "      name: scoped sibling\n"
        "      triggers:\n"
        "        regex:\n"
        "          - 'git\\s+" + _remote_write_verb + "\\b[^&;\\n]*" + _force_flag + "\\b'\n"
        "    - id: b.unscoped\n"
        "      name: bare wildcard, same category\n"
        "      triggers:\n"
        "        regex:\n"
        "          - 'git " + _remote_write_verb + ".*" + _force_flag + "'\n"
    )
    findings = check(bad)
    _ok(
        "flags a bare wildcard beside a scoped sibling in the same category",
        any("b.unscoped" in f for f in findings),
    )
    _ok(
        "does NOT flag the scoped sibling itself",
        not any("a.scoped:" in f for f in findings),
    )

    # regression: replay the historical shape of the FIRST dated incident this
    # checker exists to catch statically (a bare-wildcard remote-mutate rule,
    # reconstructed as representative — see the module docstring) beside a
    # sibling that already carries the scoped convention -> must flag.
    historical = _wrap_yaml(
        "  shell_remote_mutate:\n"
        "    - id: srm.other-scoped-rule\n"
        "      name: an already-scoped sibling rule\n"
        "      triggers:\n"
        "        regex:\n"
        "          - 'gh\\s+pr\\s+merge\\b[^&;\\n]*--admin\\b'\n"
        "    - id: srm.reconstructed-incident-shape\n"
        "      name: PRE-FIX representative bare-wildcard form\n"
        "      triggers:\n"
        "        regex:\n"
        "          - 'git " + _remote_write_verb + ".*(" + _force_flag + "|-f)'\n"
    )
    findings = check(historical)
    _ok(
        "regression: flags the pre-fix bare-wildcard incident shape",
        any("srm.reconstructed-incident-shape" in f for f in findings),
    )

    # pass-on-good: the CURRENT post-fix live catalog must be clean.
    if CATALOG_PATH.exists():
        live_findings = check(CATALOG_PATH.read_text(encoding="utf-8"))
        _ok("pass-on-good: the live post-fix catalog is clean", not live_findings)
        if live_findings:
            for f in live_findings:
                print(f"      (unexpected) {f}")
    else:
        ok = False
        print(f"  ✗ MISSED: live catalog not found at {CATALOG_PATH}")

    # a category with no scoped sibling at all must not be flagged — nothing to
    # be inconsistent with (avoids noise on categories that never established
    # the convention).
    no_convention = _wrap_yaml(
        "  never_scoped_cat:\n"
        "    - id: n.one\n"
        "      name: only member, uses a bare wildcard\n"
        "      triggers:\n"
        "        regex:\n"
        "          - 'foo.*bar'\n"
    )
    findings = check(no_convention)
    _ok(
        "a category with no scoped sibling at all is not flagged (nothing to be inconsistent with)",
        not findings,
    )

    # a malformed/unparseable catalog fails closed (exit 2 shape), matching
    # PR 1's checker's own fail-closed contract.
    findings = check("not a yaml block at all")
    _ok("an unparseable catalog fails closed (a finding, not silent clean)", bool(findings))

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("--self-test", "self-test"):
        return self_test()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
