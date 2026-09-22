#!/usr/bin/env python3
"""brand_guidance_lint.py - a zero-dependency structural checker for brand-guidance.md.

Converts gold-standard-website-pipeline G3's brand-guidance criterion from
agent-attested to CI-gateable, per the follow-up named in the FORGE plan that
built this skill (.ravenclaude/runs/forge/web-design-taste-system/plan.md §7 —
"the single highest-value follow-up ... this is the plugin's own
contrast_ratio.py precedent").

Checks EXACTLY the five structural facts G3's criterion names, and nothing
else:

  1. The file exists and is non-empty.
  2. All 7 required sections are present, in numeric order (## 1. .. ## 7.).
  3. Typeface count <= max (default 2), read from the machine-visible
     `typeface_count: N` marker in section 2 - never parsed from prose.
  4. Every anti-pattern catalogue row (section 7) has a resolved
     `override.status`; every non-"enforced" row has a non-empty rationale.
  5. Zero adjectival rules in the project's own authored prose (sections 1-6)
     - the same banned-word list the catalogue's own hygiene checklist uses.

This is a STRUCTURAL checker, not a taste judge - it says nothing about
whether the aesthetic is good. That judgment stays entirely with
brand-polish-checklist.md, which stays advisory. A file that passes every
check here can still look bad; a file that fails here is missing a
structural fact G3 requires regardless of how it looks.

Usage
-----
    brand_guidance_lint.py check <brand-guidance.md> [--catalogue FILE] [--typeface-max N] [--json]
    brand_guidance_lint.py --self-test

Exit codes:
  0   all five checks pass (or --self-test: every fixture behaved as expected)
  1   the target file (or catalogue file) could not be read
  2   one or more structural checks failed (or --self-test: teeth failed)

Stdlib only (argparse, json, re); runs anywhere Python 3.8+ is present.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

# Canonical catalogue IDs shipped with this skill (reference/anti-pattern-catalogue.md).
# Used as the default expected-ID set when --catalogue is not given, so the linter
# still works against a lone brand-guidance.md with no catalogue file nearby.
DEFAULT_CATALOGUE_IDS = tuple(f"AP-{n:02d}" for n in range(1, 11))

# The same banned-word list the catalogue's own hygiene checklist and this
# skill's SKILL.md section 4 use - one shared vocabulary, never reinvented.
ADJECTIVAL_WORDS = (
    "clean", "modern", "sleek", "polished", "beautiful", "elegant",
    "stylish", "gorgeous", "slick", "chic", "refined", "premium-looking",
)

# The 7 required section headings, matched by leading "## N." only - a project
# may phrase the rest of the heading differently, but the numeric anchor and
# order are the structural contract (see the template's own section numbers).
REQUIRED_SECTIONS = tuple(range(1, 8))

_SECTION_RE = re.compile(r"^##\s+(\d+)\.", re.MULTILINE)
_TYPEFACE_COUNT_RE = re.compile(r"typeface_count:\s*(\d+)")
_CATALOGUE_ROW_RE = re.compile(
    r"^\|\s*`(AP-\d\d)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$", re.MULTILINE
)


class LintError(Exception):
    """Raised for a file the linter cannot even open - exit 1, never 2."""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LintError(f"cannot read {path}: {exc}") from exc


def check_exists_and_nonempty(text: str) -> list[str]:
    if not text.strip():
        return ["brand-guidance.md is empty"]
    return []


def check_sections_in_order(text: str) -> list[str]:
    found = [int(m.group(1)) for m in _SECTION_RE.finditer(text)]
    findings = []
    missing = [n for n in REQUIRED_SECTIONS if n not in found]
    if missing:
        findings.append(
            "missing required section number(s): " + ", ".join(f"## {n}." for n in missing)
        )
    # Order check: the numbers that ARE present must appear in ascending order
    # in the file (a project that reordered sections fails structurally even
    # if none is missing).
    present_in_order = [n for n in found if n in REQUIRED_SECTIONS]
    if present_in_order != sorted(present_in_order):
        findings.append(
            "required sections are present but out of order: "
            + " -> ".join(f"## {n}." for n in present_in_order)
        )
    return findings


def check_typeface_count(text: str, max_typefaces: int) -> list[str]:
    m = _TYPEFACE_COUNT_RE.search(text)
    if not m:
        return [
            "no machine-visible `typeface_count: N` marker found in section 2 "
            "(this is a structural requirement, not a prose count - see the template)"
        ]
    count = int(m.group(1))
    if count > max_typefaces:
        return [f"typeface_count is {count}, exceeds the max of {max_typefaces}"]
    return []


def check_catalogue_overrides(text: str, expected_ids: tuple[str, ...]) -> list[str]:
    findings: list[str] = []
    rows = {m.group(1): (m.group(2), m.group(3), m.group(4)) for m in _CATALOGUE_ROW_RE.finditer(text)}

    missing = [rid for rid in expected_ids if rid not in rows]
    if missing:
        findings.append("catalogue rows missing from section 7: " + ", ".join(missing))
    extra = [rid for rid in rows if rid not in expected_ids]
    if extra:
        findings.append("catalogue rows present but not in the expected ID set: " + ", ".join(sorted(extra)))

    for rid, (_banned, status_cell, rationale_cell) in rows.items():
        status = status_cell.strip().lower()
        rationale = rationale_cell.strip()
        if status not in ("enforced", "relaxed", "replaced"):
            findings.append(f"{rid}: override.status is not resolved (got {status_cell.strip()!r})")
            continue
        if status != "enforced" and not rationale:
            findings.append(f"{rid}: override.status is {status!r} but rationale is empty")
    return findings


def check_no_adjectival_rules(text: str) -> list[str]:
    # Scope to sections 1-6 (the project's own authored prose) - section 7 is
    # largely the catalogue table copied in verbatim and is not where a
    # project writes its own rules. Slice from the first "## 1." to the first
    # "## 7." (or end of file if section 7 is absent - already flagged above).
    start = _SECTION_RE.search(text)
    if not start:
        return []  # already flagged by check_sections_in_order
    sec7 = re.search(r"^##\s+7\.", text, re.MULTILINE)
    end = sec7.start() if sec7 else len(text)

    # BLANK (not strip) <...> placeholder/instructional spans before scanning
    # - the TEMPLATE itself legitimately names banned words as examples of
    # what NOT to write (e.g. `<... never "modern and clean" ...>`), and a
    # shipped project file must not carry any unresolved <...> placeholder
    # anyway (the template's own header says so). This is this repo's own
    # recurring "source-scan gates match PROSE" trap, applied to this
    # linter's own target text - a real authored rule is never inside angle
    # brackets. Blanking (replacing each char with a space) rather than
    # deleting keeps every remaining character at its ORIGINAL offset, so
    # line numbers need no re-search.
    section_text = text[start.start():end]
    scoped = re.sub(r"<[^<>]*>", lambda m: " " * len(m.group(0)), section_text)

    findings = []
    pattern = re.compile(r"\b(" + "|".join(re.escape(w) for w in ADJECTIVAL_WORDS) + r")\b", re.IGNORECASE)
    for m in pattern.finditer(scoped):
        line_no = text[: start.start() + m.start()].count("\n") + 1
        findings.append(f"adjectival word {m.group(1)!r} found (sections 1-6, line {line_no})")
    return findings


def lint(path: Path, catalogue_path: Path | None, typeface_max: int) -> dict:
    text = _read(path)

    expected_ids = DEFAULT_CATALOGUE_IDS
    if catalogue_path is not None:
        cat_text = _read(catalogue_path)
        cat_ids = tuple(sorted(set(re.findall(r"`(AP-\d\d)`", cat_text))))
        if cat_ids:
            expected_ids = cat_ids

    checks = {
        "exists_and_nonempty": check_exists_and_nonempty(text),
        "sections_in_order": check_sections_in_order(text),
        "typeface_count": check_typeface_count(text, typeface_max),
        "catalogue_overrides_resolved": check_catalogue_overrides(text, expected_ids),
        "zero_adjectival_rules": check_no_adjectival_rules(text),
    }
    all_findings = [f"[{name}] {finding}" for name, fs in checks.items() for finding in fs]
    return {"path": str(path), "checks": checks, "findings": all_findings, "passed": not all_findings}


# ── self-test ────────────────────────────────────────────────────────────────
# A "good" fixture that passes every check, plus 5 single-mutation variants -
# each mutant must trip EXACTLY the check it targets, proving each of the 5
# structural facts is independently enforced rather than the checker passing
# by construction (the repo's own recurring "a gate that asserts nothing"
# failure mode).

_GOOD_SECTIONS = (
    "## 1. Named aesthetic\n\nEditorial technical, per two named references.\n\n"
    "## 2. Typography\n\n<!-- typeface_count: 2 -->\n\n| Role | Typeface |\n|---|---|\n"
    "| Display | Fraunces |\n| Body | Source Sans 3 |\n\n"
    "## 3. Palette\n\nOne accent, one neutral ramp.\n\n"
    "## 4. Spacing\n\n4 / 8 / 12 / 16.\n\n"
    "## 5. Radius & elevation\n\nSharp corners, hairline elevation.\n\n"
    "## 6. Motion philosophy\n\nRestrained; reduced-motion re-points to instant.\n\n"
    "## 7. Anti-pattern catalogue\n\n"
    "| ID | Banned by default | `override.status` | `override.rationale` |\n|---|---|---|---|\n"
)


def _fixture(catalogue_ids, statuses=None, rationales=None, typeface_line=None, extra_section1=""):
    statuses = statuses or dict.fromkeys(catalogue_ids, "enforced")
    # Default rationale: empty for enforced rows, a real one-liner otherwise -
    # but `rationales` lets a specific test force an EMPTY rationale on a
    # non-enforced row (the exact violation check_catalogue_overrides exists
    # to catch), which the blanket default below can never produce.
    rationales = rationales or {}
    body = _GOOD_SECTIONS
    if typeface_line is not None:
        body = body.replace("<!-- typeface_count: 2 -->", typeface_line)
    body = body.replace(
        "Editorial technical, per two named references.",
        "Editorial technical, per two named references." + extra_section1,
    )
    rows = "\n".join(
        f"| `{rid}` | some banned pattern | {statuses[rid]} | "
        f"{rationales.get(rid, '' if statuses[rid] == 'enforced' else 'a stated one-line reason')} |"
        for rid in catalogue_ids
    )
    return body + rows + "\n"


def self_test() -> int:
    ok = True

    def chk(name, got, want):
        nonlocal ok
        if got == want:
            print(f"  OK   {name}")
        else:
            ok = False
            print(f"  FAIL {name} (got {got!r}, want {want!r})")

    ids = tuple(f"AP-{n:02d}" for n in range(1, 11))

    with tempfile.TemporaryDirectory() as tmp:
        def write_and_lint(name, text, typeface_max=2, catalogue_ids=ids):
            p = Path(tmp) / name
            p.write_text(text, encoding="utf-8")
            r = lint(p, None, typeface_max)
            # lint() defaults to the shipped 10 AP-nn IDs when --catalogue is
            # None; override by monkeypatching only when a fixture uses a
            # different ID set (none of the mutants below do).
            return r

        good = _fixture(ids)
        r = write_and_lint("good.md", good)
        chk("the good fixture passes clean", r["passed"], True)

        r = write_and_lint("empty.md", "   \n\n  ")
        chk("an empty file trips exists_and_nonempty", bool(r["checks"]["exists_and_nonempty"]), True)

        missing_section = good.replace("## 4. Spacing\n\n4 / 8 / 12 / 16.\n\n", "")
        r = write_and_lint("missing-section.md", missing_section)
        chk("a missing section trips sections_in_order, nothing else",
            (bool(r["checks"]["sections_in_order"]), r["checks"]["typeface_count"],
             r["checks"]["catalogue_overrides_resolved"], r["checks"]["zero_adjectival_rules"]),
            (True, [], [], []))

        over_typeface = _fixture(ids, typeface_line="<!-- typeface_count: 3 -->")
        r = write_and_lint("over-typeface.md", over_typeface)
        chk("typeface_count: 3 trips typeface_count, nothing else",
            (bool(r["checks"]["typeface_count"]), r["checks"]["sections_in_order"],
             r["checks"]["catalogue_overrides_resolved"], r["checks"]["zero_adjectival_rules"]),
            (True, [], [], []))

        relaxed_no_rationale = _fixture(
            ids,
            statuses={rid: ("relaxed" if rid == "AP-01" else "enforced") for rid in ids},
            rationales={"AP-01": ""},
        )
        r = write_and_lint("relaxed-no-rationale.md", relaxed_no_rationale)
        chk("a relaxed row with no rationale trips catalogue_overrides_resolved, nothing else",
            (bool(r["checks"]["catalogue_overrides_resolved"]), r["checks"]["sections_in_order"],
             r["checks"]["typeface_count"], r["checks"]["zero_adjectival_rules"]),
            (True, [], [], []))

        adjectival = _fixture(ids, extra_section1=" It should feel clean and modern.")
        r = write_and_lint("adjectival.md", adjectival)
        chk("a real 'clean'/'modern' rule trips zero_adjectival_rules, nothing else",
            (bool(r["checks"]["zero_adjectival_rules"]), r["checks"]["sections_in_order"],
             r["checks"]["typeface_count"], r["checks"]["catalogue_overrides_resolved"]),
            (True, [], [], []))

        placeholder = good.replace(
            "Editorial technical, per two named references.",
            'Editorial technical. <One line — never "modern and clean." Name references.>',
        )
        r = write_and_lint("placeholder-not-flagged.md", placeholder)
        chk("banned words INSIDE <...> placeholder text are NOT flagged (the template's own shape)",
            bool(r["checks"]["zero_adjectival_rules"]), False)

    print()
    print("  brand_guidance_lint self-test: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test and exit")
    sub = ap.add_subparsers(dest="cmd")

    p_check = sub.add_parser("check", help="lint a brand-guidance.md against G3's 5 structural facts")
    p_check.add_argument("target", type=Path, help="path to the project's brand-guidance.md")
    p_check.add_argument("--catalogue", type=Path, default=None,
                          help="path to anti-pattern-catalogue.md (default: this skill's shipped 10 AP-nn IDs)")
    p_check.add_argument("--typeface-max", type=int, default=2)
    p_check.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.cmd != "check":
        ap.error("one of 'check' or --self-test is required")

    try:
        result = lint(args.target, args.catalogue, args.typeface_max)
    except LintError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["passed"]:
            print(f"OK: {args.target} passes all 5 structural checks")
        else:
            print(f"FAIL: {args.target} — {len(result['findings'])} finding(s):")
            for f in result["findings"]:
                print(f"  - {f}")
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    sys.exit(main())
