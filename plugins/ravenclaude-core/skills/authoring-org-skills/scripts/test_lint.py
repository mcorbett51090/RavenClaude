#!/usr/bin/env python3
"""Acceptance battery for `orgskill lint` (plan Phase 2).

Run: python3 scripts/test_lint.py            # the suite
     python3 scripts/test_lint.py --must-fail-harness   # prove the harness has teeth

⛔ THE FALSE-POSITIVE CONTROLS ARE THE POINT OF THIS FILE. A measured 0.3% first-person
rate on 934 real skills turned out to be 100% false positives — every hit was "I can"
inside a QUOTED USER UTTERANCE, i.e. the check fired on descriptions following best
practice. Those cases are pinned below. A regression here means somebody made the
pattern cleverer instead of the checked region smaller, which is the wrong direction.

⛔ THE HARNESS POSITIVE CONTROL (gap-delta D9). A top-level read that throws at
collection zeroes an entire assertion set silently — "0 test failures" beside
"Failed Suites 1" is the tell. So --must-fail-harness deliberately breaks the
rules-table path and asserts the suite goes RED, not green-with-zero-assertions.

Stdlib only. Python 3.9-safe.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_rules  # noqa: E402
from orgskill import load_rules  # noqa: E402

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RULES = os.path.join(_HERE, "schemas", "org-skill-rules.json")
_MARKERS = os.path.join(_HERE, "reference", "ds02-markers.json")


def _markers() -> list[str]:
    with open(_MARKERS, encoding="utf-8") as fh:
        return [m["idiom"] for m in json.load(fh)["markers"]]


def _skill(tmp: str, name: str, description: str, body: str = "# Body\n\nDo the thing.\n",
           extra_fm: str = "", dirname: str | None = None) -> str:
    d = os.path.join(tmp, dirname or name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write("---\nname: %s\ndescription: %s\n%s---\n\n%s" % (name, description, extra_fm, body))
    return d


def _run(d: str, table, markers) -> tuple[dict[str, str], list[str]]:
    findings, ambiguity = lint_rules.lint_skill(d, table, markers)
    return {f["rule_id"]: f["tier"] for f in findings}, ambiguity


def main(argv: list[str]) -> int:
    must_fail = "--must-fail-harness" in argv

    rules_path = _RULES
    if must_fail:
        # Break the rules-table path exactly as a collection-time error would.
        rules_path = os.path.join(tempfile.mkdtemp(), "does-not-exist.json")

    try:
        table = load_rules(rules_path)
    except Exception as exc:  # noqa: BLE001 — the point is to catch ANY collection error
        print("HARNESS ERROR: cannot load the rule table: %s" % exc)
        print("\nsuite: RED (harness could not run — this is NOT a pass)")
        return 1 if not must_fail else 0  # must-fail expects red; that IS its pass

    markers = _markers()
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

    tmp = tempfile.mkdtemp(prefix="orgskill-test-")
    try:
        # ── known-good corpus: zero FAIL (warns are expected, not failures) ──
        good = [
            ("processing-invoices", "Extracts totals and line items from supplier invoices. Use when the user asks to read an invoice or reconcile a bill."),
            ("drafting-replies", "Drafts a customer email reply grounded in the account record. Use when the user opens a support thread and asks for a draft."),
            ("auditing-permissions", "Reviews role grants for over-broad access. Use when the user asks who can see a record."),
            ("summarizing-meetings", "Summarizes a meeting transcript into decisions and owners. Use when the user asks for meeting notes."),
            ("validating-schemas", "Validates a JSON payload against its schema and reports the first divergence. Use when the user asks to check a payload."),
            ("triaging-incidents", "Classifies an incident by severity and routes it. Use when the user reports an outage."),
        ]
        for nm, desc in good:
            d = _skill(tmp, nm, desc)
            got, amb = _run(d, table, markers)
            fails = [r for r, t in got.items() if t == "fail"]
            check("known-good %-22s zero FAIL" % nm, not fails and not amb,
                  "got fails=%s amb=%s" % (fails, amb))

        # ── PV01 false-positive controls (the regression record) ──────────────
        fp_cases = [
            ("quoted first person",
             'Builds a leadership dashboard. Use when the user asks for "a report I can show leadership".'),
            ("I/O must not match",
             "Diagnoses disk I/O saturation on a host. Use when the user reports slow reads."),
            ("I-9 must not match",
             "Reviews an I-9 employment form for completeness. Use when the user asks about onboarding paperwork."),
            ("backticked your",
             "Applies a token file to a stylesheet. Use when the user asks to theme `your-app.css`."),
            ("their / the user's in object position",
             "Rewrites a draft in the user's own voice, preserving their phrasing. Use when the user asks to personalize a reply."),
        ]
        for label, desc in fp_cases:
            d = _skill(tmp, "checking-things", desc)
            got, _ = _run(d, table, markers)
            check("PV01 FP control: %-38s" % label, "PV01" not in got,
                  "PV01 fired on a legitimate description")

        # PV01 true positive — the check must still catch the real thing.
        d = _skill(tmp, "helping-out", "I can help you process Excel files whenever you need it.")
        got, _ = _run(d, table, markers)
        check("PV01 TRUE positive still fires", got.get("PV01") == "warn",
              "the check is now blind: %s" % got)

        # ── FM08 both directions: XML TAGS, not the characters < and > ────────
        # These fixtures ARE the 63/934 false-positive finding. A bare-angle-bracket
        # predicate hard-blocked descriptions whose only sin was an ASCII arrow.
        for label, desc in (
            ("ASCII arrow chain", "Maps the funnel stage-by-stage (inquiry->apply->admit->yield). Use when the user asks about conversion."),
            ("arrow with spaces", "Scores a rubric. Not legal advice -> routes hard calls to a reviewer. Use when the user asks for a score."),
            ("numeric comparison", "Flags any request slower than <300ms and faster than >5s. Use when the user asks about latency."),
        ):
            d = _skill(tmp, "measuring-things", desc)
            got, _ = _run(d, table, markers)
            check("FM08 FP control: %-38s" % label, "FM08" not in got,
                  "a FAIL-tier rule fired on punctuation, not a tag")

        for label, desc in (
            ("open tag", "Emits a responsive <picture> element. Use when the user asks for an image block."),
            ("hyphenated tag", "Renders a <model-viewer> embed. Use when the user asks for a 3D preview."),
            ("closing tag", "Strips a </thinking> block from a transcript. Use when the user asks to clean output."),
        ):
            d = _skill(tmp, "emitting-markup", desc)
            got, _ = _run(d, table, markers)
            check("FM08 TRUE positive: %-37s" % label, got.get("FM08") == "fail",
                  "the narrowed check is now blind to real tags: %s" % got)

        # ── DS02 both directions ──────────────────────────────────────────────
        d = _skill(tmp, "scoring-rubrics",
                   "Scores an artifact against a rubric. Reach for this on a quality question.")
        got, _ = _run(d, table, markers)
        check("DS02 house idiom 'reach for this ON' does NOT fire", "DS02" not in got,
              "this fixture IS the 47%-false-positive finding")

        d = _skill(tmp, "listing-things", "Lists the widgets in a catalog and their prices.")
        got, _ = _run(d, table, markers)
        check("DS02 fires when there is genuinely no trigger", got.get("DS02") == "warn")

        # ── NM02 false-positive controls: legit domain nouns → WARN, never FAIL ─
        for nm in ("choose-statistical-test", "test-assistive-tech", "agent-quality-rubric",
                   "prompt-pattern-library"):
            d = _skill(tmp, nm, "Selects the right approach. Use when the user asks which to pick.")
            got, _ = _run(d, table, markers)
            check("NM02 %-26s is WARN not FAIL" % nm, got.get("NM02") in (None, "warn"),
                  "tier was %r" % got.get("NM02"))

        # ── seeded-defect battery: each caught by ITS OWN id, at its tier ──────
        seeded = [
            ("FM03", _skill(tmp, "x" * 70, "Does a thing. Use when asked.", dirname="x" * 70)),
            ("FM04", _skill(tmp, "My_Helper Skill", "Does a thing. Use when asked.",
                            dirname="My_Helper Skill")),
            ("FM07", _skill(tmp, "padding-descriptions", "Use when asked. " + "x" * 1100)),
            ("FM09", _skill(tmp, "declared-name", "Does a thing. Use when asked.",
                            dirname="different-directory")),
            ("FM10", _skill(tmp, "empty-bodied", "Does a thing. Use when asked.", body="")),
            ("FM12", _skill(tmp, "extra-keyed", "Does a thing. Use when asked.",
                            extra_fm="allowed-tools: Bash\n")),
            ("BD02", _skill(tmp, "dangling-linker", "Does a thing. Use when asked.",
                            body="# B\n\nSee [the guide](reference/missing.md).\n")),
            ("BD03", _skill(tmp, "escaping-linker", "Does a thing. Use when asked.",
                            body="# B\n\nSee [up](../outside.md).\n")),
            ("DS03", _skill(tmp, "vague-describer", "Helps with documents")),
            ("NM01", _skill(tmp, "invoice-helper", "Does a thing. Use when asked.")),
        ]
        for rid, d in seeded:
            got, _ = _run(d, table, markers)
            expected_tier = next(r["tier"] for r in table["rules"] if r["id"] == rid)
            check("seeded defect %-5s caught at %-4s" % (rid, expected_tier),
                  got.get(rid) == expected_tier,
                  "expected %s=%s, got %r" % (rid, expected_tier, got.get(rid)))

        # ── FM09 is a WARN, and the reason is pinned to EVIDENCE not taste ────
        # ⛔ Demoted 2026-08-24 because Anthropic's own worked example violates the rule
        # (skill "Brand Guidelines" in folder "my-skill/") while a sibling page lists the
        # mismatch as a failure cause. Two vendor sources contradicting each other is the
        # condition under which this table warns instead of blocking. If someone
        # re-promotes this to FAIL, they must first record an observed upload that
        # rejects a mismatched pair — the assertion below is what makes that explicit.
        fm09 = next(r for r in table["rules"] if r["id"] == "FM09")
        check("FM09 is WARN, not FAIL", fm09["tier"] == "warn", fm09["tier"])
        check("        …and carries the evidence its demotion rests on",
              "demotion_evidence" in fm09 and "Brand Guidelines" in fm09["rationale"],
              "a tier change with no recorded basis is a preference wearing a rule id")
        d = _skill(tmp, "declared-name", "Does a thing. Use when asked.",
                   dirname="different-directory")
        got, _ = _run(d, table, markers)
        check("        …and a mismatch still REPORTS, it just does not block",
              got.get("FM09") == "warn", "demoted into silence: %r" % got.get("FM09"))

        # ── tier discipline: no advisory rule may hold tier fail ──────────────
        offenders = [r["id"] for r in table["rules"]
                     if r["class"] == "advisory" and r["tier"] != "warn"]
        check("tier discipline: no advisory rule holds tier 'fail'", not offenders,
              "offenders=%s" % offenders)

        # ── ambiguity fails closed ────────────────────────────────────────────
        d = os.path.join(tmp, "no-skill-md")
        os.makedirs(d, exist_ok=True)
        _, amb = _run(d, table, markers)
        check("a directory with no SKILL.md reports ambiguity", bool(amb))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = ok + len(bad)
    print("\norgskill lint suite: %s (%d/%d)"
          % ("PASS" if not bad else "FAIL", ok, total))
    if bad:
        print("failed:")
        for b in bad:
            print("   -", b)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
