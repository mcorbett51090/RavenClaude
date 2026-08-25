#!/usr/bin/env python3
"""Acceptance battery for the authoring procedure (plan Phase 5).

Run: python3 scripts/test_procedure.py
     python3 scripts/test_procedure.py --must-fail-literals  # prove the no-literals grep bites
     python3 scripts/test_procedure.py --must-fail-harness   # prove the harness has teeth

⛔ AT3/AT4 ARE THE LOAD-BEARING ONES. Two worked examples, in unrelated domains, must go
all the way through lint -> pack -> verify. A procedure that only its own author can
follow, on the one example it was written against, is not a procedure. The second example
is the one that would catch a document quietly specialised to customer support.

⛔ AT5 (no restated constants) exists because a limit written twice is a limit that will
drift, and the copy in the prose is the one nobody re-measures. The rule table is the
single source; SKILL.md points at rule IDS.

Stdlib only. Python 3.9-safe.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_rules  # noqa: E402
import packer  # noqa: E402
import refusals  # noqa: E402
from orgskill import _load_markers, load_rules  # noqa: E402

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RULES = os.path.join(_HERE, "schemas", "org-skill-rules.json")
_SKILL_MD = os.path.join(_HERE, "SKILL.md")
_EVIDENCE = os.path.join(_HERE, "reference", "platform-constraints.md")
_EXAMPLES = os.path.join(_HERE, "templates", "examples")
_SKELETON = os.path.join(_HERE, "templates", "skeleton")

_BODY_LINE_CAP = 200          # plan AT1; this file's own budget, not a platform constant


def _numeric_constants(table: dict) -> set:
    """Every numeric limit the rule table owns, as a string."""
    out = set()
    for rule in table["rules"]:
        for n in re.findall(r"\b(\d{2,})\b", str(rule.get("rule", ""))):
            out.add(n)
    return out


def _full_scan(skill_dir: str, table: dict, markers: list) -> tuple[list, list]:
    """lint + refusals over one skill directory, the way the CLI does it."""
    findings, ambiguity = lint_rules.lint_skill(skill_dir, table, markers)
    try:
        with open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8") as fh:
            raw = fh.read()
    except (OSError, UnicodeDecodeError):
        raw = ""
    fm_block, body = lint_rules.split_frontmatter(raw)
    fm = lint_rules.parse_scalars(fm_block)[0] if fm_block else {}
    bundled = []
    for root, _d, files in os.walk(skill_dir):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), skill_dir)
            if rel != "SKILL.md":
                bundled.append(rel)
    findings.extend(refusals.scan_refusals(skill_dir, table, body,
                                           fm.get("description", ""), {}, bundled))
    return findings, ambiguity


def main(argv: list[str]) -> int:
    must_fail_literals = "--must-fail-literals" in argv
    must_fail_harness = "--must-fail-harness" in argv

    rules_path = os.path.join(tempfile.mkdtemp(), "gone.json") if must_fail_harness else _RULES
    try:
        table = load_rules(rules_path)
    except Exception as exc:  # noqa: BLE001
        print("HARNESS ERROR: cannot load the rule table: %s" % exc)
        print("\nsuite: RED (harness could not run — this is NOT a pass)")
        return 0 if must_fail_harness else 1

    markers = _load_markers(None, _HERE)
    ok = 0
    bad: list[str] = []

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        if cond:
            ok += 1
            print("  OK    %s" % label)
        else:
            bad.append(label)
            print("  FAIL  %s%s" % (label, ("  — " + detail) if detail else ""))

    with open(_SKILL_MD, encoding="utf-8") as fh:
        skill_text = fh.read()
    fm_block, body = lint_rules.split_frontmatter(skill_text)
    fm = lint_rules.parse_scalars(fm_block)[0] if fm_block else {}
    desc = fm.get("description", "")

    # ── AT1: shape of the skill's own SKILL.md ───────────────────────────────
    n_lines = len(skill_text.splitlines())
    check("AT1 SKILL.md is under %d lines (%d)" % (_BODY_LINE_CAP, n_lines),
          n_lines < _BODY_LINE_CAP)
    check("AT1 its description carries a when-to-use clause",
          bool(re.search(r"\b(use when|reach for this when|reach for this on)\b", desc, re.I)),
          desc[:90])
    masked = lint_rules.mask_unchecked_spans(desc)
    check("AT1 its description uses no first person",
          not lint_rules._FIRST_PERSON.search(masked), desc[:90])
    check("AT1 its description uses no second person",
          not lint_rules._SECOND_PERSON.search(masked), desc[:90])
    check("AT1 the doc STATES it does not fully self-conform, rather than implying it",
          "does not fully conform" in skill_text and "allowed-tools" in skill_text,
          "an unstated exception reads as a claim of conformance")

    # ── AT2: the skill's own NAME lints clean under its own rules ────────────
    name = fm.get("name", "")
    check("AT2 the name is authoring-org-skills", name == "authoring-org-skills", name)
    toks = name.split("-")
    generic = {"test", "agent", "framework", "system", "service", "engine",
               "module", "manager", "handler", "tool"}
    stop = {"helper", "helpers", "utils", "util", "tools", "misc", "common", "stuff", "things"}
    check("AT2 the name passes NM02 (no generic domain noun)", not (set(toks) & generic))
    check("AT2 the name passes NM01 (no placeholder token)", not (set(toks) & stop))
    check("AT2 the name passes NM03 (gerund form)", bool(re.match(r"^[a-z0-9]+ing(-|$)", name)))
    check("AT2 org-skill-studio would NOT have passed NM03 — the name was chosen, not defaulted",
          not re.match(r"^[a-z0-9]+ing(-|$)", "org-skill-studio"))

    # ── AT5: no constant from the rule table is restated in SKILL.md ─────────
    consts = _numeric_constants(table)
    check("AT5 precondition: the rule table actually owns numeric constants",
          len(consts) >= 2, "a vacuous grep would pass on an empty set: %s" % consts)
    hay = skill_text if not must_fail_literals else skill_text + "\nname is at most 64 characters.\n"
    leaked = sorted({c for c in consts if re.search(r"\b%s\b" % re.escape(c), hay)})
    check("AT5 SKILL.md restates no numeric constant from the rule table",
          not leaked, "leaked=%s — the copy in prose is the one nobody re-measures" % leaked)
    check("AT5 SKILL.md points at rule IDS instead",
          len(re.findall(r"\b(?:FM|BD|DS|NM|PV|ZP|R)\d{1,2}\b", skill_text)) >= 3)

    # ── the skeleton is a real starting tree ─────────────────────────────────
    check("the skeleton ships a SKILL.md and a bundled reference",
          os.path.isfile(os.path.join(_SKELETON, "SKILL.md"))
          and os.path.isfile(os.path.join(_SKELETON, "reference", "details.md")))

    # ── AT3/AT4: both worked examples go lint -> pack -> verify ──────────────
    examples = sorted(d for d in os.listdir(_EXAMPLES)
                      if os.path.isdir(os.path.join(_EXAMPLES, d)))
    check("AT4 there are two worked examples, in different domains", len(examples) == 2, examples)

    tmp = tempfile.mkdtemp(prefix="orgskill-proc-")
    try:
        for ex in examples:
            d = os.path.join(_EXAMPLES, ex)
            findings, ambiguity = _full_scan(d, table, markers)
            fails = [f for f in findings if f["tier"] == "fail"]
            check("AT3 %-28s lints with zero FAIL" % ex, not fails and not ambiguity,
                  "%s amb=%s" % ([(f["rule_id"], f["message"][:44]) for f in fails], ambiguity))

            out = os.path.join(tmp, ex + ".zip")
            try:
                packer.pack(d, out, table, findings)
                packed = True
            except packer.PackRefused as exc:
                packed = False
                check("AT3 %-28s packs" % ex, False, str(exc)[:120])
            if packed:
                check("AT3 %-28s packs" % ex, os.path.isfile(out))
                vf, _notes = packer.verify(out, table, _EVIDENCE, markers)
                vfails = [f for f in vf if f["tier"] == "fail"]
                check("AT3 %-28s verifies from the archive bytes" % ex, not vfails,
                      [(f["rule_id"], f["message"][:44]) for f in vfails])

            # Each example must also do the thing the procedure asks for.
            with open(os.path.join(d, "SKILL.md"), encoding="utf-8") as fh:
                txt = fh.read()
            check("AT3 %-28s carries the scope-negation section" % ex,
                  re.search(r"^##+\s+Not for\b", txt, re.M) is not None,
                  "the exercise in §3 is not optional in the examples")
            edesc = lint_rules.parse_scalars(lint_rules.split_frontmatter(txt)[0])[0].get(
                "description", "")
            check("AT3 %-28s description names capability AND trigger" % ex,
                  bool(re.search(r"\buse when\b", edesc, re.I)) and len(edesc.split()) > 12,
                  edesc[:80])

        # ── DOGFOOD: the studio must pass its own FAIL tier ──────────────────
        # ⛔ This assertion earned itself the moment it was written. The studio would
        # have REFUSED TO PACK ITSELF: R1/R2/R5/R6 fired on the rule table's own rule
        # text and measured_note fields, and R3 on a fixtures file — every one of them
        # a literal quoted where a paraphrase would do, which is precisely the defect
        # refusals.md tells authors to fix first. Nothing operational was lost by
        # paraphrasing; a rule's content is the constraint and the measurement, never
        # the string. A tool that cannot survive its own rules has not tested them.
        self_findings, self_amb = _full_scan(_HERE, table, markers)
        self_fails = [f for f in self_findings if f["tier"] == "fail"]
        check("DOGFOOD the studio passes its own FAIL tier", not self_fails,
              [(f["rule_id"], f["span"], f["message"][:44]) for f in self_fails])
        check("        …and its only frontmatter warn is the documented allowed-tools",
              all(f["rule_id"] != "FM12" or "allowed-tools" in f["message"]
                  for f in self_findings), "an undocumented extra key crept in")
        check("        …and the dogfood is not vacuous — it saw real findings",
              len(self_findings) >= 2 or bool(self_amb),
              "zero findings of any tier means the scan did not run")

        # ── the examples are NOT discoverable as Claude Code skills ──────────
        # They live under templates/, two levels below the skills/*/ glob, so they
        # cannot be picked up as real skills or pollute the corpus measurements.
        import glob
        corpus = glob.glob(os.path.join(_HERE, "..", "*", "SKILL.md"))
        check("worked examples are not discoverable as Claude Code skills",
              not any("templates/examples" in p.replace("\\", "/") for p in corpus))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = ok + len(bad)
    print("\norgskill procedure suite: %s (%d/%d)"
          % ("PASS" if not bad else "FAIL", ok, total))
    if bad:
        print("failed:")
        for b in bad:
            print("   -", b)
    if must_fail_literals:
        print("\n--must-fail-literals: suite went %s (RED is the pass)"
              % ("RED" if bad else "GREEN"))
        return 0 if bad else 1
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
