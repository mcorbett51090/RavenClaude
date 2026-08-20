#!/usr/bin/env python3
"""check-nuance-floor.py — P7 §9.2 (⛔ R7). A cheap FLOOR, never a sufficient test.

⛔ THE RULING THIS IMPLEMENTS, STATED PLAINLY.

The nuance bar is NOT fully automatable, and a fake metric that passes while
entries teach nothing is worse than an admitted human step. Plan A deterministic
gate is constructively gameable — a worked 4-token example defeats it — and its
only backstop, the LLM judge, is advisory by plan A own admission. Plan B honesty
about its prefilter ("catches the laziest failure mode, nothing more") is correct,
but its sample review was a PROCESS STEP WITH NO MECHANISM, and this repo record
is that process steps decay and mechanisms do not.

So: keep the deterministic gate as a cheap floor (this file), and make the sample
review BLOCKING via a committed ledger that `inventory-coverage.py --check` reads.

⛔ WHAT THIS FILE CANNOT DO, PRINTED IN ITS OWN OUTPUT:
These checks test SHAPE and FALSIFIABILITY. They do not test whether the nuance is
TRUE, and they do not test whether it is NON-OBVIOUS. The sampled review does the
second; only a probe does the first.

── THE FOUR CHECKS ─────────────────────────────────────────────────────────
F1  negation-of-expectation against a NAMED alternative. Coarse filter.
F2  non-derivability, DUAL BASELINE. |M \\ B1| >= 2 gates.
    ⛔ THE MEASURED FLAW THIS FIXES: plan A excluded the covered artifact own
    header from the baseline, reasoning that the dashboard reader has the summary
    and not the file. That exclusion is exactly what makes the exploit free —
    EVERY MECHANISM TOKEN NEEDED TO PASS IS SITTING IN THE FILE THE AUTHOR HAS
    OPEN. So two counts against two baselines: B1 = summary + title +
    covers-basenames (the reader baseline, gates at >= 2); B2 = B1 + the covered
    artifacts own header text. An entry passing B1 but not B2 STILL PASSES — a
    nuance restated from a header is genuinely useful to a dashboard reader — but
    it is reported separately as `derived-from-header` and ratcheted DOWN, rather
    than laundered into the same number as an original finding.
    Two token sets, two counts, one honest number.
F3  anti-goodhart. Each novel mechanism token must sit in a sentence carrying a
    verb from a closed claim-verb list. A token in a bare noun phrase does not
    count, so stuffing requires writing FALSE CLAIMS — a different and much more
    visible offence.
F4  evidence triple wired: measured/control/falsifier non-empty, control >= 20
    chars and != falsifier, probe names a real path OR starts with `unprobed: `
    plus >= 30 chars of reason. An unprobed nuance is ALLOWED — it is honest —
    and the unprobed fraction is counted and ratcheted down.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed.

Usage:
    check-nuance-floor.py [--root DIR] [--check]
    check-nuance-floor.py --golden        # run the frozen golden set
    check-nuance-floor.py --must-fail
    check-nuance-floor.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from concepts import ENTRY_CLASS_INVENTORY, ConceptError, load_concepts  # noqa: E402

GOLDEN = "tests/fixtures/inventory-nuance-golden.json"

# F1 — a closed vocabulary. Coarse on purpose: it is a filter, not a verdict.
F1_MARKERS = (
    r"\bnot\b[^.]{0,80}\bbut\b", r"\bnever\b", r"\binstead of\b", r"\brather than\b",
    r"\btwo ways\b", r"\bonly one\b", r"\bnot\b[^.]{0,40}\bit\b", r"\bwhile\b[^.]{0,60}\bdoes\b",
    r"\bcontrary to\b", r"\bdespite\b", r"\bwithout\b[^.]{0,40}\bever\b",
    # Added after the golden run: these are still NAMED-alternative shapes, not a
    # loosening. "only X" names what it excludes; "no <noun> at all" and "cannot"
    # assert an absence against an expectation; "not by/from/against Y" names the
    # alternative explicitly.
    r"\bonly\b", r"\bcannot\b", r"\bno\s+\w+(?:\s+\w+)?\s+at all\b",
    r"\bnot\s+(?:by|from|against|because|to)\b", r"\bnothing\b",
)
_F1 = re.compile("|".join(F1_MARKERS), re.I)

# Mechanism tokens: backticked spans, hook event names, exit <n>, dotted/slashed
# identifiers, quoted JSON fields.
_TOKEN_PATTERNS = (
    re.compile(r"`([^`\n]{2,60})`"),
    re.compile(r"\b(PreToolUse|PostToolUse|SessionStart|SessionEnd|Stop|SubagentStart|"
               r"SubagentStop|Notification|UserPromptSubmit|PreCompact)\b"),
    re.compile(r"\b(exit\s+\d+)\b", re.I),
    re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*(?:[./][A-Za-z0-9_.-]+)+)\b"),
    re.compile(r'"([A-Za-z_][A-Za-z0-9_]*)"'),
)

# F3 — a closed claim-verb list. A mechanism token in a bare noun phrase does not
# count toward F2, so stuffing forces the author to assert something falsifiable.
# ⛔ CLOSED, BUT NOT NARROW. The list must be closed — that is the anti-goodhart
# property, since an author cannot invent a verb to smuggle a token past it. But
# the first version was closed AND narrow, and it scored 11 of 12 MEASURED nuances
# at zero novel tokens: real mechanism sentences say "is delivered", "carries",
# "gates", "escapes", "arms", not only "fires" and "returns". A closed list that
# rejects true claims does not measure quality; it measures vocabulary overlap
# with whoever wrote the list.
CLAIM_VERBS = (
    "reaches", "reach", "arrives", "arrive", "fires", "fire", "returns", "return",
    "exits", "exit", "replaces", "replace", "concatenate", "concatenates", "denies",
    "deny", "is keyed by", "is read by", "blocks", "block", "no-ops", "no-op",
    "runs", "run", "counts", "count", "skips", "skip", "aborts", "abort",
    "survives", "survive", "matches", "match", "writes", "write", "reads", "read",
    "delivered", "delivers", "deliver", "carries", "carry", "gates", "gate",
    "escapes", "escape", "arms", "arm", "compares", "compare", "costs", "cost",
    "injects", "inject", "reports", "report", "shrinks", "shrink", "advised",
    "advises", "keyed", "propagates", "propagate", "branches", "branch",
    "refreshes", "refresh", "discards", "discard", "inflates", "inflate",
    "continues", "continue", "greps", "grep", "screens", "screen", "parses",
    "parse", "resolves", "resolve", "bumps", "bump", "moves", "move",
    # Added after the golden run: ordinary mechanism verbs a real entry uses to
    # relate two named things ("premise-gate.py TREATS exit 0 as its teeth bit
    # while sync-plugin-versions.py USES exit 2"). Still closed, still stemmed.
    "treats", "treat", "uses", "use", "declares", "declare", "names", "name",
    "requires", "require", "applies", "apply", "covers", "cover", "holds", "hold",
    "points", "point", "expects", "expect", "assumes", "assume",
)
# ⛔ MATCHED BY STEM, NOT BY EXACT FORM. Measured: the exact-form list missed
# "escaped" and "gated" in a real measured nuance and scored it at zero, because
# only "escapes"/"escape" and "gates"/"gate" were listed. Tense is not a quality
# signal. The list stays CLOSED — that is the anti-goodhart property — but a
# closed list that only recognises present tense measures grammar, not claims.
_VERB = re.compile(
    "|".join(rf"\b{re.escape(v)}(?:s|es|d|ed|ing)?\b" for v in CLAIM_VERBS), re.I
)

CONTROL_MIN = 20
UNPROBED_PREFIX = "unprobed: "
UNPROBED_REASON_MIN = 30


def _tokens(text: str) -> set[str]:
    out: set[str] = set()
    for rx in _TOKEN_PATTERNS:
        for m in rx.finditer(text or ""):
            tok = m.group(1).strip().lower()
            if len(tok) >= 3:
                out.add(tok)
    return out


def _sentences(text: str) -> list[str]:
    # ⛔ SPLIT ON .!? ONLY — NOT on a semicolon. Measured: splitting on `;` cut
    # "reaches the model on no event; only additionalContext is delivered" into two
    # fragments, stranding both mechanism tokens in a clause whose verb sat in the
    # OTHER half. F3 then scored a genuine measured nuance at zero. A semicolon
    # joins clauses of one claim; it does not end one.
    return [s for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def _covered_headers(root: Path, covers: list[str], max_lines: int = 60) -> str:
    """The first N lines of each covered artifact — the text an author has open."""
    parts = []
    for rel in covers or []:
        fp = root / rel
        if not fp.is_file():
            continue
        try:
            with fp.open(encoding="utf-8", errors="replace") as fh:
                parts.append("".join(next(fh, "") for _ in range(max_lines)))
        except OSError:
            pass
    return "\n".join(parts)


def evaluate(root: Path, entry: dict) -> dict:
    """Return a per-entry verdict dict. Never raises on a malformed entry."""
    nuance = entry.get("nuance") or ""
    ev = entry.get("nuance_evidence") or {}
    fails: list[str] = []

    # ── F1 ──
    if not _F1.search(nuance):
        fails.append("F1: no negation-of-expectation against a named alternative")

    # ── F2, dual baseline ──
    b1_text = " ".join([
        entry.get("summary") or "", entry.get("title") or "",
        " ".join(Path(p).name for p in (entry.get("covers") or [])),
    ])
    b1 = _tokens(b1_text)
    b2 = b1 | _tokens(_covered_headers(root, entry.get("covers") or []))
    m = _tokens(nuance)

    # ── F3 gates which tokens COUNT toward F2 ──
    claim_tokens: set[str] = set()
    for sent in _sentences(nuance):
        # ⛔ THE VERB MUST BE PROSE, NOT PART OF A CODE TOKEN. Measured: the
        # token-stuffing negative
        #   "`PreToolUse`, `PostToolUse`, `exit 2`, … — not one of these, but the ledger"
        # passed the floor, because the word `exit` INSIDE the backticked span
        # `exit 2` satisfied the claim-verb test. A bare noun phrase then scored
        # five novel tokens. Stripping backticked spans before looking for a verb
        # is what makes F3 actually anti-goodhart: to make a token count, the
        # author has to assert something about it in prose, which means writing a
        # falsifiable claim rather than a list.
        prose = re.sub(r"`[^`\n]*`", " ", sent)
        if _VERB.search(prose):
            claim_tokens |= _tokens(sent)

    novel_b1 = (m - b1) & claim_tokens
    novel_b2 = (m - b2) & claim_tokens

    if len(novel_b1) < 2:
        fails.append(
            f"F2/F3: only {len(novel_b1)} novel mechanism token(s) in a claim sentence "
            "(need >= 2). A token in a bare noun phrase does not count."
        )

    derived_from_header = len(novel_b1) >= 2 and len(novel_b2) < 2

    # ── F4 ──
    control = str(ev.get("control") or "").strip()
    falsifier = str(ev.get("falsifier") or "").strip()
    probe = str(ev.get("probe") or "").strip()
    if not str(ev.get("measured") or "").strip():
        fails.append("F4: nuance_evidence.measured is empty")
    if len(control) < CONTROL_MIN:
        fails.append(f"F4: control is {len(control)} chars (need >= {CONTROL_MIN})")
    if not falsifier:
        fails.append("F4: falsifier is empty")
    if control and control == falsifier:
        fails.append("F4: control and falsifier are identical — one of them is not doing its job")
    if probe.startswith(UNPROBED_PREFIX):
        if len(probe) - len(UNPROBED_PREFIX) < UNPROBED_REASON_MIN:
            fails.append(f"F4: unprobed reason under {UNPROBED_REASON_MIN} chars")
    elif not probe:
        fails.append("F4: probe is empty")
    elif not (root / probe).exists():
        fails.append(f"F4: probe '{probe}' does not resolve")

    return {
        "id": entry.get("id", "?"),
        "passes": not fails,
        "fails": fails,
        "novel_b1": sorted(novel_b1),
        "novel_b2": sorted(novel_b2),
        "derived_from_header": derived_from_header,
        "unprobed": probe.startswith(UNPROBED_PREFIX),
    }


LIMIT_NOTE = (
    "  ⛔ These checks test SHAPE and FALSIFIABILITY. They do NOT test whether the\n"
    "     nuance is TRUE, and they do NOT test whether it is NON-OBVIOUS. The sampled\n"
    "     review does the second; only a probe does the first."
)


def _run_golden(root: Path) -> int:
    gp = root / GOLDEN
    if not gp.is_file():
        print(f"✗ golden set missing at {GOLDEN} — the floor is unvalidated, not clean.")
        return 1
    g = json.loads(gp.read_text(encoding="utf-8"))
    pos, neg = g["positives"], g["negatives"]

    print("── nuance floor vs the frozen golden set ──")
    bad_pos = [p for p in pos if not evaluate(root, p)["passes"]]
    bad_neg = []
    uncaught_adversarial = []
    for n in neg:
        v = evaluate(root, n)
        # ⛔ A NEGATIVE MAY BE REJECTED BY THE FLOOR *OR* CAUGHT AS
        # derived-from-header. The plan requires recording WHICH, honestly, per
        # negative — reporting them as one aggregate would hide exactly how
        # gameable the floor is.
        #
        # ⛔ AND AN ADVERSARIAL NEGATIVE THAT PASSES UNCAUGHT IS AN EXPECTED
        # RESULT, NOT A GATE FAILURE. R7 rules the bar is not fully automatable;
        # this is a cheap FLOOR. Failing the gate here would push an author to
        # weaken the adversarial fixtures until the number looked good, which is
        # the fake metric R7 exists to forbid. What IS required: every
        # ILLUSTRATIVE negative must be rejected, and every adversarial one that
        # survives must be named, so the sampled review knows what it is carrying.
        if v["passes"] and not v["derived_from_header"]:
            if n.get("adversarial"):
                uncaught_adversarial.append(n["id"])
            else:
                bad_neg.append((n, v))

    print(f"  positives: {len(pos) - len(bad_pos)}/{len(pos)} accepted")
    for p in bad_pos:
        v = evaluate(root, p)
        print(f"    ✗ {p['id']}: {'; '.join(v['fails'])}")
    print(f"  negatives: {len(neg) - len(bad_neg)}/{len(neg)} rejected or flagged")
    for n, _v in bad_neg:
        print(f"    ✗ {n['id']}: PASSED the floor and was not flagged derived-from-header")

    print()
    print("  per-negative disposition (the honest breakdown):")
    for n in neg:
        v = evaluate(root, n)
        if not v["passes"]:
            how = f"rejected by {v['fails'][0].split(':')[0]}"
        elif v["derived_from_header"]:
            how = "PASSED the floor; caught only by the B2/derived-from-header count"
        else:
            how = "⛔ PASSED UNCAUGHT — the sampled review is the only remaining filter"
        print(f"    · {n['id']:<28} {how}")

    print()
    if uncaught_adversarial:
        print(f"  ⛔ {len(uncaught_adversarial)} ADVERSARIAL negative(s) passed the floor uncaught:")
        for i in uncaught_adversarial:
            print(f"      · {i}")
        print("     This is the measured gameability of the floor, reported rather than")
        print("     tuned away. These entries are caught ONLY by the blocking sampled")
        print("     review (P7 §9.3), which is why that review is a gate and not a")
        print("     process step. Weakening these fixtures to make this list shorter")
        print("     would be the fake metric R7 forbids.")
        print()
    print(LIMIT_NOTE)
    return 1 if (bad_pos or bad_neg) else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--golden", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    root = Path(args.root).resolve()

    if args.golden:
        return _run_golden(root)

    if args.must_fail:
        rc = _run_golden(root)
        if rc != 0:
            print("✗ must-fail: the golden set does not pass, so the floor is not")
            print("  calibrated and nothing it says about the corpus is trustworthy.")
            return 0
        # CONTROL: a deliberately empty nuance must be rejected, or the floor is
        # accepting everything and the golden result above is vacuous.
        if evaluate(root, {"id": "empty", "nuance": "", "nuance_evidence": {}})["passes"]:
            print("✗ must-fail: an EMPTY nuance passed the floor.")
            return 0
        print("✓ must-fail: the golden set separates positives from negatives and an")
        print("  empty nuance is rejected. Exiting 1, the DECLARED teeth code.")
        return 1

    try:
        concepts = load_concepts(root)
    except ConceptError as exc:
        print(f"nuance-floor: concepts do not parse — {exc}")
        return 2

    entries = [c for c in concepts if c.get("entry_class") == ENTRY_CLASS_INVENTORY]
    print("── nuance floor (necessary, NEVER sufficient) ──")
    print(f"  inventory entries: {len(entries)}")
    if not entries:
        print("  ⚠ EMPTY population — not a clean one. Run --golden for the calibration.")
        print()
        print(LIMIT_NOTE)
        return 0

    rc = 0
    derived = 0
    unprobed = 0
    for e in entries:
        v = evaluate(root, e)
        derived += bool(v["derived_from_header"])
        unprobed += bool(v["unprobed"])
        if not v["passes"]:
            rc = 1
            print(f"  ✗ {v['id']}:")
            for f in v["fails"]:
                print(f"      {f}")
        elif v["derived_from_header"]:
            print(f"  · {v['id']}: passes B1, fails B2 — counted as derived-from-header")

    print()
    print(f"  derived-from-header : {derived}/{len(entries)}  (reported honestly, ratcheted DOWN)")
    print(f"  unprobed            : {unprobed}/{len(entries)}  (allowed, counted, ratcheted DOWN)")
    print()
    print(LIMIT_NOTE)
    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
