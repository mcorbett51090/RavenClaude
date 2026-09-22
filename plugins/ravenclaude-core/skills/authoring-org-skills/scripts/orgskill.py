#!/usr/bin/env python3
"""orgskill — author, validate and package a claude.ai Organization Skill.

Phase 0 scope (this file, today): the rules loader and its invariant checker.
`lint` / `pack` / `verify` / `report` land in later phases and are declared here
only as stubs so the CLI surface is stable.

⛔ NO NUMERIC LIMIT MAY APPEAR IN THIS FILE. Every threshold (name length,
description length, body lines) lives in schemas/org-skill-rules.json and is read
from there. Phase 0 acceptance test 1 greps this file for bare limit literals; a
constant stated twice is a constant that will drift. The only integers below are
exit codes, list indices and the self-test's own fixture counts.

Stdlib only. Python 3.9-safe (stock macOS ships 3.9.6).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

# ⛔ EXIT CONTRACT — 0 = clean, 2 = finding or parse ambiguity. EXIT 1 IS NEVER USED.
# Claude Code treats a hook exit of 1 as a NON-BLOCKING error, so a checker that
# reports findings with 1 silently allows the thing it just objected to. That is the
# defect class this repo has shipped twice (the macOS `globstar` fail-open, and Gate
# 184 landing inside its own dispatcher). Fail closed or do not fail at all.
EXIT_OK = 0
EXIT_FINDINGS = 2
EXIT_USAGE = 2

_HARD_REFUSALS = ("R1", "R2", "R3", "R4")
_VALID_TIERS = ("fail", "warn")
_VALID_CLASSES = ("ground-truth", "advisory")
_CLAIM_RE = re.compile(r"^S(\d+)$")
_FIRE_RATE_KEYS = ("value", "n", "total", "population", "measured_on")

_DEFAULT_RULES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "schemas",
    "org-skill-rules.json",
)


# ── loading ──────────────────────────────────────────────────────────────────

def load_rules(path: str | None = None) -> dict[str, Any]:
    """Read the rule table. Raises on anything it cannot confidently parse.

    Refusing beats guessing: this table is the single source of every threshold
    the studio enforces, so a silently-half-parsed table would enforce a subset
    while reporting success.
    """
    p = path or _DEFAULT_RULES
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise ValueError("rule table has no top-level 'rules' array")
    return data


# ── the invariant checker (Phase 0 acceptance test 5) ────────────────────────

def check_invariants(data: dict[str, Any], max_claim: int) -> list[str]:
    """Return a list of invariant violations. Empty list == the table is sound.

    The load-bearing pair is advisory ⟹ warn and advisory ⟹ fire_rate present.
    Together they make an unmeasured heuristic *unserializable*: you cannot write
    down a judgement-call rule without also writing down what it fired on and the
    population you measured. That is the whole tier discipline, mechanised.
    """
    problems: list[str] = []
    seen: dict[str, int] = {}

    for idx, rule in enumerate(data.get("rules", [])):
        rid = rule.get("id") or "<rule #%d with no id>" % idx
        if rid in seen:
            problems.append("%s: duplicate rule id" % rid)
        seen[rid] = idx

        tier = rule.get("tier")
        klass = rule.get("class")
        if tier not in _VALID_TIERS:
            problems.append("%s: tier %r is not one of %s" % (rid, tier, list(_VALID_TIERS)))
        if klass not in _VALID_CLASSES:
            problems.append("%s: class %r is not one of %s" % (rid, klass, list(_VALID_CLASSES)))

        # The two invariants that carry the tier discipline.
        if klass == "advisory" and tier != "warn":
            problems.append(
                "%s: class 'advisory' requires tier 'warn' (got %r) — a heuristic may not block"
                % (rid, tier)
            )
        if klass == "advisory" and rule.get("fire_rate") is None:
            problems.append(
                "%s: class 'advisory' requires a measured fire_rate — an unmeasured "
                "heuristic cannot ship" % rid
            )

        if not str(rule.get("remediation", "")).strip():
            problems.append("%s: empty remediation — a rule that cannot say how to fix "
                            "the defect is not ready to warn" % rid)
        if not str(rule.get("rule", "")).strip():
            problems.append("%s: empty rule text" % rid)

        claim = str(rule.get("claim", ""))
        m = _CLAIM_RE.match(claim)
        if not m or not (1 <= int(m.group(1)) <= max_claim):
            problems.append("%s: claim %r is not a real S-id in S1..S%d" % (rid, claim, max_claim))

        fr = rule.get("fire_rate")
        if fr is not None:
            if not isinstance(fr, dict):
                problems.append("%s: fire_rate must be an object" % rid)
            else:
                for key in _FIRE_RATE_KEYS:
                    if key not in fr:
                        problems.append("%s: fire_rate missing %r" % (rid, key))
                # A rate that does not equal its own numerator over its own
                # denominator is a number somebody typed, not one they measured.
                try:
                    if fr.get("total"):
                        calc = round(float(fr["n"]) / float(fr["total"]), 4)
                        if abs(calc - float(fr["value"])) > 0.0002:
                            problems.append(
                                "%s: fire_rate value %s does not equal n/total (%s) — "
                                "the rate was asserted, not computed"
                                % (rid, fr.get("value"), calc)
                            )
                except (TypeError, ValueError, ZeroDivisionError):
                    problems.append("%s: fire_rate n/total/value are not numeric" % rid)

        # ⛔ A hard refusal that lost its no_override flag is a refusal with a --force.
        # The invariant is listed in the table's own invariants[]; a listed invariant
        # nothing checks is this repo's gate-that-asserts-nothing class, so it is
        # enforced here rather than described there.
        if rid in _HARD_REFUSALS:
            if tier != "fail":
                problems.append("%s: a hard refusal must be tier 'fail' (got %r)" % (rid, tier))
            if klass != "ground-truth":
                problems.append("%s: a hard refusal must be class 'ground-truth' (got %r)"
                                % (rid, klass))
            if rule.get("no_override") is not True:
                problems.append("%s: a hard refusal must carry no_override: true — a "
                                "supply-chain refusal with an override is a refusal that "
                                "will be overridden" % rid)

    if not data.get("stale_after"):
        problems.append("<table>: missing stale_after stamp — an unswept snapshot "
                        "enforces moved constraints with a green verdict")
    return problems


def _load_markers(override: str | None, skill_root: str) -> list[str]:
    """The DS02 marker list, or an empty list.

    ⛔ An unreadable list means DS02 does not run. Silently skipping ONE advisory
    check is correct; inventing markers is not — an intuition-authored list is the
    exact defect the corpus derivation exists to prevent. Shared by lint, pack and
    verify so all three see the same list; two loaders would be two DS02s.
    """
    path = override or os.path.join(skill_root, "reference", "ds02-markers.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return [m["idiom"] for m in json.load(fh)["markers"]]
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return []


# ── self-test, with the negative controls that give it teeth ─────────────────

def _fixture(**over: Any) -> dict[str, Any]:
    base = {
        "id": "FX01", "tier": "warn", "class": "advisory", "claim": "S3",
        "rule": "a fixture rule", "rationale": "fixture", "remediation": "fix it",
        "fire_rate": {"value": 0.5, "n": 1, "total": 2,
                      "population": "fixture", "measured_on": "2026-08-24"},
    }
    base.update(over)
    return {"stale_after": "2026-11-20", "rules": [base]}


def self_test(max_claim: int) -> int:
    """Positive control first, then one negative control per invariant.

    A checker is only worth its exit code if a KNOWN-BAD table actually fails it.
    Every case below asserts a *specific* violation string, so a checker that
    rejected everything for the wrong reason would not pass.
    """
    cases: list[tuple[str, dict[str, Any], str | None]] = [
        ("positive control: a sound advisory rule passes", _fixture(), None),
        ("positive control: a sound ground-truth rule with no fire_rate passes",
         _fixture(**{"class": "ground-truth", "tier": "fail", "fire_rate": None}), None),
        ("advisory + tier:fail is REJECTED",
         _fixture(tier="fail"), "requires tier 'warn'"),
        ("advisory + fire_rate:null is REJECTED",
         _fixture(fire_rate=None), "requires a measured fire_rate"),
        ("empty remediation is REJECTED",
         _fixture(remediation="   "), "empty remediation"),
        ("a claim outside S1..S%d is REJECTED" % max_claim,
         _fixture(claim="S999"), "not a real S-id"),
        ("a non-existent claim shape is REJECTED",
         _fixture(claim="banana"), "not a real S-id"),
        ("a fire_rate whose value != n/total is REJECTED",
         _fixture(fire_rate={"value": 0.99, "n": 1, "total": 2,
                             "population": "fixture", "measured_on": "2026-08-24"}),
         "does not equal n/total"),
        ("a fire_rate missing its population is REJECTED",
         _fixture(fire_rate={"value": 0.5, "n": 1, "total": 2,
                             "measured_on": "2026-08-24"}), "missing 'population'"),
        ("a missing stale_after stamp is REJECTED",
         {"rules": [_fixture()["rules"][0]]}, "missing stale_after"),
    ]

    failed = 0
    for label, table, expect in cases:
        problems = check_invariants(table, max_claim)
        if expect is None:
            ok = not problems
            detail = "" if ok else "  unexpected: %s" % problems
        else:
            ok = any(expect in p for p in problems)
            detail = "" if ok else "  expected a violation containing %r, got %s" % (expect, problems or "NOTHING")
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, detail))
        if not ok:
            failed += 1

    print("\norgskill self-test: %s (%d/%d)"
          % ("PASS" if not failed else "FAIL", len(cases) - failed, len(cases)))
    return EXIT_OK if not failed else EXIT_FINDINGS


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="orgskill", description=__doc__.splitlines()[0])
    # Top-level flag, matching this repo's convention (forge-route.py --self-test,
    # premise-gate.py --self-test). NOT a subcommand: argparse cannot dispatch a
    # subparser whose name begins with '--'.
    ap.add_argument("--self-test", action="store_true",
                    help="run the invariant self-test (positive + negative controls)")
    ap.add_argument("--max-claim", type=int, default=27,
                    help="highest valid S-id (claims-table size)")
    sub = ap.add_subparsers(dest="cmd")

    p_rules = sub.add_parser("rules", help="load and validate the rule table")
    p_rules.add_argument("--path", default=None)
    p_rules.add_argument("--check", action="store_true", help="assert the table's invariants")
    p_rules.add_argument("--json", action="store_true")

    p_lint = sub.add_parser("lint", help="check a skill directory against the rule battery")
    p_lint.add_argument("target", help="path to the skill directory (containing SKILL.md)")
    p_lint.add_argument("--rules", default=None, help="override the rule-table path")
    p_lint.add_argument("--markers", default=None, help="override the DS02 marker list")
    p_lint.add_argument("--json", action="store_true")
    p_lint.add_argument("--run-record", default=None,
                        help="path to the EXTERNAL run record naming quarantine reviewers. "
                             "This is NOT an override: it can only satisfy the reviewer "
                             "condition of a quarantine, never skip a refusal.")
    p_lint.add_argument("--warn-only", action="store_true",
                        help="report warns but exit 0 unless a FAIL fired")

    p_pack = sub.add_parser("pack", help="build the archive (refuses on any FAIL)")
    p_pack.add_argument("target", help="path to the skill directory")
    p_pack.add_argument("-o", "--out", required=True, help="output .zip path")
    p_pack.add_argument("--rules", default=None)
    p_pack.add_argument("--markers", default=None)
    p_pack.add_argument("--run-record", default=None)

    p_verify = sub.add_parser("verify", help="re-open an archive and check it from its bytes")
    p_verify.add_argument("target", help="path to the .zip")
    p_verify.add_argument("--rules", default=None)
    p_verify.add_argument("--markers", default=None)
    p_verify.add_argument("--evidence", default=None,
                          help="override the ZP02 evidence file path")

    p_fix = sub.add_parser("fixtures", help="write the two zip-root probe archives")
    p_fix.add_argument("--out", required=True, help="directory to write the fixtures into")

    sp = sub.add_parser("report", help="(phase 3 — folded into lint)")
    sp.add_argument("target", nargs="?")

    args = ap.parse_args(argv)

    if args.self_test:
        return self_test(args.max_claim)

    if args.cmd is None:
        ap.print_help()
        return EXIT_USAGE

    if args.cmd == "rules":
        try:
            data = load_rules(args.path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print("orgskill: cannot read the rule table: %s" % exc, file=sys.stderr)
            return EXIT_USAGE
        problems = check_invariants(data, args.max_claim) if args.check else []
        if args.json:
            print(json.dumps({"rule_count": len(data["rules"]), "problems": problems}, indent=2))
        else:
            rules = data["rules"]
            gt = sum(1 for r in rules if r.get("class") == "ground-truth")
            adv = len(rules) - gt
            print("rule table: %d rules (%d ground-truth, %d advisory)" % (len(rules), gt, adv))
            print("stale_after: %s" % data.get("stale_after"))
            for p in problems:
                print("  VIOLATION: %s" % p)
            if args.check and not problems:
                print("invariants: PASS")
        return EXIT_FINDINGS if problems else EXIT_OK

    if args.cmd == "lint":
        try:
            import lint_rules
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import lint_rules
        try:
            table = load_rules(args.rules)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print("orgskill: cannot read the rule table: %s" % exc, file=sys.stderr)
            return EXIT_FINDINGS  # fail closed: no table means no checks ran

        markers = _load_markers(
            args.markers, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        findings, ambiguity = lint_rules.lint_skill(args.target, table, markers)

        # ── refusals (Phase 3) ───────────────────────────────────────────────
        # Re-read the frontmatter the same way lint_rules does, so the description
        # region the refusal scan treats as unconditional is byte-identical to the
        # one the linter checked. Two parsers would be two definitions of "the
        # description", and the strict one would be whichever ran second.
        import refusals
        try:
            _raw = open(os.path.join(args.target, "SKILL.md"), encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            _raw = ""
        _fm_block, _body = lint_rules.split_frontmatter(_raw)
        _fm = lint_rules.parse_scalars(_fm_block)[0] if _fm_block else {}
        bundled = []
        for _root, _dirs, _files in os.walk(args.target):
            for _f in _files:
                _rel = os.path.relpath(os.path.join(_root, _f), args.target)
                if _rel != "SKILL.md":
                    bundled.append(_rel)
        record = refusals.load_run_record(args.run_record)
        r_findings = refusals.scan_refusals(args.target, table, _body,
                                            _fm.get("description", ""), record, bundled)
        findings.extend(r_findings)
        risk, drivers = refusals.scanner_risk(r_findings)
        fails = [f for f in findings if f["tier"] == "fail"]
        warns = [f for f in findings if f["tier"] == "warn"]

        if args.json:
            print(json.dumps({"target": args.target, "findings": findings,
                              "ambiguity": ambiguity, "scanner_risk": risk,
                              "scanner_risk_drivers": drivers,
                              "scanner_risk_note": refusals.SCANNER_RISK_NOTE,
                              "fail_count": len(fails), "warn_count": len(warns)}, indent=2))
        else:
            print("orgskill lint: %s" % args.target)
            for f in fails + warns:
                label = "QUARANTINED" if f.get("quarantine_cleared_by") else f["tier"].upper()
                head = "  [%s] %s  %s" % (label, f["rule_id"], f["message"])
                print(head)
                print("        span: %s   claim: %s" % (f["span"], f["claim"]))
                print("        fix : %s" % f["remediation"])
                fr = f.get("fire_rate")
                if fr:
                    # An advisory finding without its provenance reads as a fact.
                    print("        measured: %.1f%% (%d/%d) on %s"
                          % (100 * fr["value"], fr["n"], fr["total"], fr["population"]))
            for a in ambiguity:
                print("  [AMBIGUITY] %s" % a)
            print("\n%d fail, %d warn, %d ambiguity" % (len(fails), len(warns), len(ambiguity)))
            print("\nscanner_risk: %s%s" % (risk, ("  <- " + ", ".join(drivers)) if drivers else ""))
            print(refusals.SCANNER_RISK_NOTE)
            print("\n" + lint_rules.WHAT_THIS_DOES_NOT_CHECK)

        if ambiguity:
            return EXIT_FINDINGS          # fail closed on anything we could not parse
        if fails:
            return EXIT_FINDINGS
        if warns and not args.warn_only:
            return EXIT_OK                # warns never block; they inform
        return EXIT_OK

    if args.cmd in ("pack", "verify", "fixtures"):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import packer

        skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if args.cmd == "fixtures":
            paths = packer.write_probe_fixtures(args.out)
            print("zip-root probe fixtures written:")
            for pth in paths:
                print("   %s" % pth)
            print("\nUpload BOTH at Organization settings > Skills and record BOTH "
                  "outcomes in\n%s (see #zip-root-settlement)."
                  % packer.evidence_path(skill_root))
            return EXIT_OK

        try:
            table = load_rules(args.rules)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print("orgskill: cannot read the rule table: %s" % exc, file=sys.stderr)
            return EXIT_FINDINGS
        markers = _load_markers(args.markers, skill_root)

        if args.cmd == "pack":
            import lint_rules
            import refusals
            findings, ambiguity = lint_rules.lint_skill(args.target, table, markers)
            raw = ""
            try:
                with open(os.path.join(args.target, "SKILL.md"), encoding="utf-8") as fh:
                    raw = fh.read()
            except (OSError, UnicodeDecodeError):
                pass
            fm_block, body = lint_rules.split_frontmatter(raw)
            fm = lint_rules.parse_scalars(fm_block)[0] if fm_block else {}
            bundled = []
            for root, _d, fs in os.walk(args.target):
                for f in fs:
                    rel = os.path.relpath(os.path.join(root, f), args.target)
                    if rel != "SKILL.md":
                        bundled.append(rel)
            findings.extend(refusals.scan_refusals(
                args.target, table, body, fm.get("description", ""),
                refusals.load_run_record(args.run_record), bundled))
            if ambiguity:
                for a in ambiguity:
                    print("orgskill pack: AMBIGUITY %s" % a, file=sys.stderr)
                return EXIT_FINDINGS
            layout, basis, basis_note = packer.derive_default_layout(
                packer.evidence_path(skill_root))
            try:
                result = packer.pack(args.target, args.out, table, findings, layout=layout)
            except packer.PackRefused as exc:
                print("orgskill pack: %s" % exc, file=sys.stderr)
                return EXIT_FINDINGS
            print("packed %s (%d entries, root layout %s)"
                  % (result["archive"], len(result["entries"]), result["layout"]))
            # ⛔ The BASIS travels with the layout. A user who is told "layout A" and not
            # told why has no way to know whether that was observed, researched, or
            # guessed — and those three carry very different odds of the upload working.
            if basis != "upload-verified":
                print("NOTE: root layout %s chosen on basis '%s' — %s."
                      % (result["layout"], basis, basis_note))
                print("      See reference/platform-constraints.md#zip-root-settlement. "
                      "One upload each settles it.")
            return EXIT_OK

        findings, notes = packer.verify(
            args.target, table, args.evidence or packer.evidence_path(skill_root), markers)
        fails = [f for f in findings if f["tier"] == "fail"]
        warns = [f for f in findings if f["tier"] == "warn"]
        print("orgskill verify: %s" % args.target)
        for f in fails + warns:
            print("  [%s] %s  %s" % (f["tier"].upper(), f["rule_id"], f["message"]))
            if f.get("remediation"):
                print("        fix : %s" % f["remediation"])
        for n in notes:
            print("  [note] %s" % n)
        print("\n%d fail, %d warn" % (len(fails), len(warns)))
        return EXIT_FINDINGS if fails else EXIT_OK

    print("orgskill: '%s' lands in a later phase" % args.cmd, file=sys.stderr)
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
