#!/usr/bin/env python3
"""classify_claim.py — premise-gate P0: a GRAMMATICAL claim classifier.

WHY THIS EXISTS. An agent probed `/cdn-cgi/l/email-protection`, got a 404, and
wrote down "the decoder is broken, therefore every visitor sees a mangled
address." The OBSERVATION (a 404) was true. The INFERENCE was false. Sixteen
files, a go-live checklist item and two turns of owner-facing architectural
advice were built on it.

FORGE's G1 gate validates PROVENANCE — "is this claim sourced?" — and that claim
WAS sourced: an in-session `curl` backed it. G1 has no notion of INFERENTIAL
DISTANCE. This module is that notion, and it reads only the GRAMMAR of the
written sentence, never the author's confidence. A 100%-certain author and a
hedging author produce byte-identical input here.

FIVE FAMILIES (plan.md 2.2):
    causal      therefore / so / because / hence / thus / which means
    defect      is broken / is down / doesn't work / is missing / fails / is dead
    quantifier  every / all / none / any / no ...        (UNENUMERATED ones)
    population  visitor / user / customer / everyone / nobody
    modal       must / would / will / cannot
Any family hit types the claim `inference`. Over-typing is deliberately cheap:
downstream, an inference that no build phase cites costs nothing, while an
un-typed inference is the whole incident.

UPWARD-ONLY. `resolve()` takes the author's own `kind` and may only RAISE it.
An author who types claim 5 `observation` gets `inference` anyway. This is what
makes the verdict not-a-self-report. Nothing in this module can move a claim
down the ladder; there is no code path that returns `observation` for a text the
patterns fired on.

WHAT IT CANNOT DO — stated because a checker that hides its blind spot is worse
than no checker. Grammar detects grammar. Claims 10 and 11 of this run's own
claims table are genuine inferences carrying NO family marker ("Gate teeth are
rule 6 already mechanized", "a prose rule is weaker than a fail-closed gate");
this module types both `observation`. They are caught only by the author's own
`kind`, which upward-only preserves. The classifier is a FLOOR, not an oracle.

THE CANARY (verification-discipline Rule 6 — "a new checker's first output is a
claim about the checker"). Four assertions run at IMPORT time against strings
embedded in this file (never fixtures on disk — a canary you can blind by
deleting a file is not a canary). A classifier that has gone blind must not
silently return "observation" for everything, so it raises `ClassifierBlind`
instead. They are explicit `raise`s, NOT `assert`s: `python -O` strips asserts,
which would delete the canary and leave exactly the silent-green failure it
exists to prevent.

Usage:
    python3 scripts/classify_claim.py --self-test
    python3 scripts/classify_claim.py --must-fail
    python3 scripts/classify_claim.py --text "the decoder is broken, therefore ..."
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "classify-claim"

OBSERVATION = "observation"
INFERENCE = "inference"
_RANK = {OBSERVATION: 0, INFERENCE: 1}

FAMILY_ORDER = ("causal", "defect", "quantifier", "population", "modal")

# Regex sources, VERBOSE (so no literal spaces and no `#` may appear inside).
# Kept as SOURCE strings, not compiled objects, so --must-fail can delete a
# family and recompile: a family with no fixture asserting it is dead weight,
# and this is how that gets proven rather than assumed.
FAMILY_SOURCES = {
    # Causal connectives. `so` is guarded against its non-causal idioms
    # ("so that" is purposive, "so far"/"so many" are degree).
    "causal": r"""
        \btherefore\b
      | \bhence\b
      | \bthus\b
      | \bconsequently\b
      | \bergo\b
      | \bbecause\b
      | \bas\s+a\s+result\b
      | \bwhich\s+means\b
      | \bmeans\s+that\b
      | \bmeaning\s+that\b
      | \bit\s+follows\s+that\b
      | \bimpl(?:y|ies)\b
      | \bso\b (?! (?: \s+ (?:that|far|many|much|long|few|little)\b | -called ) )
    """,
    # Defect predicates. Copula-anchored on purpose: a bare "fail" is a COUNT in
    # tool output ("688 pass, 0 fail, 1 skipped"), not a diagnosis, so only the
    # predicative `fails` is matched. "is working" must not read as a defect,
    # hence the negated forms are spelled out rather than an optional `not`.
    "defect": r"""
        \b(?:is|are|was|were)\s+
            (?:still\s+|completely\s+|totally\s+|apparently\s+|now\s+)?
            (?:broken|down|dead|missing|failing|unavailable|offline|unreachable|misconfigured)\b
      | \b(?:is|are|was|were)\s+not\s+working\b
      | \b(?:isn|aren|wasn|weren)['’]?t\s+working\b
      | \b(?:does|do|did)\s+not\s+work\b
      | \b(?:doesn|don|didn)['’]?t\s+work\b
      | \bfails\b
    """,
    # Unenumerated quantifiers. "at all" is an intensifier, "no-op" is a noun,
    # "no longer" is temporal — none of the three quantifies over a set.
    "quantifier": r"""
        \bevery\b
      | (?<!at\s) \ball\b
      | \bnone\b
      | \bany\b
      | \bno\b (?!-op) (?!\s+longer\b)
    """,
    # Population nouns — the generalization from one probe to everybody.
    "population": r"""
        \bvisitors?\b
      | \busers?\b
      | \bcustomers?\b
      | \beveryone\b
      | \beverybody\b
      | \bnobody\b
      | \banyone\b
      | \bno\s+one\b
      | \bend[-\s]users?\b
      | \bthe\s+public\b
    """,
    "modal": r"""
        \bmust\b
      | \bwould\b
      | \bwill\b
      | \bcannot\b
      | \bcan['’]?t\b
      | \bwon['’]?t\b
      | \bwouldn['’]?t\b
    """,
}

# Identifiers are not English. A path segment `plugins/all/`, a flag `must_pass`
# or a URL is not the author quantifying over a population, so code spans and
# URLs are removed before the grammar is read.
_CODE_SPAN = re.compile(r"`[^`]*`")
_URL = re.compile(r"https?://\S+")


class ClassifierBlind(RuntimeError):
    """Raised when the planted canary fails — the instrument cannot be trusted."""


def _compile(sources=None):
    src = FAMILY_SOURCES if sources is None else sources
    return {
        name: re.compile(pattern, re.IGNORECASE | re.VERBOSE)
        for name, pattern in src.items()
    }


_COMPILED = _compile()


def _prose(text: str) -> str:
    """Strip the parts of a claim that are code rather than grammar."""
    return _URL.sub(" ", _CODE_SPAN.sub(" ", text))


def families(text: str) -> list[str]:
    """Return the grammatical families this claim trips, in FAMILY_ORDER."""
    if not isinstance(text, str):
        raise TypeError("claim text must be a string, got %r" % type(text).__name__)
    prose = _prose(text)
    return [
        name
        for name in FAMILY_ORDER
        if name in _COMPILED and _COMPILED[name].search(prose)
    ]


def classify(text: str) -> str:
    """Type a claim from its grammar alone: "observation" or "inference"."""
    return INFERENCE if families(text) else OBSERVATION


def resolve(text: str, author_kind: str | None = None) -> str:
    """Reconcile the author's own `kind` with the grammar. UPWARD ONLY.

    The author may RAISE a claim (typing an unmarked sentence `inference`); the
    author may never LOWER one. `max` over the rank is the whole rule, and it is
    stated as `max` so no future edit can quietly introduce a downgrade branch.
    """
    grammatical = classify(text)
    if author_kind is None:
        return grammatical
    declared = str(author_kind).strip().lower()
    if declared not in _RANK:
        raise ValueError(
            "unknown author kind %r — expected 'observation' or 'inference'"
            % (author_kind,)
        )
    return grammatical if _RANK[grammatical] >= _RANK[declared] else declared


# --------------------------------------------------------------------------
# The canary. Embedded here, never loaded from disk. Runs at import.
# --------------------------------------------------------------------------

_CANARY_INFERENCE = (
    "The decoder is broken, therefore every visitor sees a mangled address"
)
_CANARY_INFERENCE_FAMILIES = ("causal", "defect", "quantifier", "population")
_CANARY_OBSERVATION = "curl -sI /cdn-cgi/trace returned HTTP/2 200 at 12:04 UTC"


def _run_canary() -> None:
    """Plant the incident's own sentence and prove the instrument still sees it."""
    hits = families(_CANARY_INFERENCE)
    if classify(_CANARY_INFERENCE) != INFERENCE:
        raise ClassifierBlind(
            "⛔ CLASSIFIER IS BLIND — the Incident-1 sentence types "
            "%r. Every 'observation' verdict this module returns is worthless."
            % classify(_CANARY_INFERENCE)
        )
    missing = [f for f in _CANARY_INFERENCE_FAMILIES if f not in hits]
    if missing:
        raise ClassifierBlind(
            "⛔ CLASSIFIER IS PARTIALLY BLIND — the Incident-1 sentence no longer "
            "trips %s (it tripped %s). The right verdict from the wrong family is "
            "not the right verdict." % (missing, hits or "nothing")
        )
    if classify(_CANARY_OBSERVATION) != OBSERVATION:
        raise ClassifierBlind(
            "⛔ CLASSIFIER IS STUCK-ON — a bare measured fact types %r, so an "
            "'inference' verdict carries no information."
            % classify(_CANARY_OBSERVATION)
        )
    if resolve(_CANARY_INFERENCE, OBSERVATION) != INFERENCE:
        raise ClassifierBlind(
            "⛔ UPWARD-ONLY IS BROKEN — an author typing the Incident-1 sentence "
            "'observation' was believed. The gate is now a self-report."
        )
    if resolve(_CANARY_OBSERVATION, INFERENCE) != INFERENCE:
        raise ClassifierBlind(
            "⛔ UPWARD-ONLY IS BROKEN — an author's raise to 'inference' was "
            "silently lowered back to 'observation'."
        )


_run_canary()


# --------------------------------------------------------------------------
# Fixtures + self-test
# --------------------------------------------------------------------------

FIXTURE_FILES = (
    "observations.json",
    "inferences.json",
    "upward-only.json",
)


def _load_fixtures(fixture_dir: Path) -> dict[str, list[dict]]:
    loaded = {}
    for name in FIXTURE_FILES:
        path = fixture_dir / name
        if not path.is_file():
            raise FileNotFoundError("missing fixture file: %s" % path)
        data = json.loads(path.read_text(encoding="utf-8"))
        cases = data.get("cases") or []
        if not cases:
            raise ValueError("fixture %s has no cases — it would pass vacuously" % path)
        loaded[name] = cases
    return loaded


def run_fixtures(fixture_dir: Path | None = None) -> tuple[int, list[str]]:
    """Run every fixture case. Returns (passed, failure messages)."""
    fixture_dir = FIXTURE_DIR if fixture_dir is None else fixture_dir
    cases = _load_fixtures(fixture_dir)
    passed = 0
    failures = []

    def check(ok: bool, msg: str) -> None:
        nonlocal passed
        if ok:
            passed += 1
        else:
            failures.append(msg)

    for case in cases["observations.json"]:
        cid, text = case["id"], case["text"]
        got, hits = classify(text), families(text)
        check(
            got == OBSERVATION,
            "%s: expected observation, got %s (tripped %s) — over-trigger: %r"
            % (cid, got, hits, text),
        )

    single_signal_seen = set()
    for case in cases["inferences.json"]:
        cid, text = case["id"], case["text"]
        declared = case.get("families") or []
        got, hits = classify(text), families(text)
        check(
            got == INFERENCE,
            "%s: expected inference, got %s — undetected: %r" % (cid, got, text),
        )
        # Rule 2 — assert the property that DEFINES the verdict, not a proxy. A
        # right answer produced by the wrong family is a family going untested.
        missing = [f for f in declared if f not in hits]
        check(
            not missing,
            "%s: declared families %s but %s did not trip (tripped %s)"
            % (cid, declared, missing, hits),
        )
        if case.get("single_signal"):
            single_signal_seen.update(declared)
            check(
                hits == declared,
                "%s: single-signal case must trip exactly %s, tripped %s"
                % (cid, declared, hits),
            )

    for case in cases["upward-only.json"]:
        cid, text = case["id"], case["text"]
        got = resolve(text, case.get("author_kind"))
        check(
            got == case["expect"],
            "%s: author_kind=%r expected %s, resolve() returned %s"
            % (cid, case.get("author_kind"), case["expect"], got),
        )

    # A family with no single-signal fixture is a family nothing asserts — it
    # could be deleted wholesale and every test would still be green.
    uncovered = [f for f in FAMILY_ORDER if f not in single_signal_seen]
    check(
        not uncovered,
        "families %s have no single-signal fixture — deleting them would go "
        "undetected" % uncovered,
    )
    return passed, failures


def _counts(fixture_dir: Path) -> tuple[int, int, int]:
    cases = _load_fixtures(fixture_dir)
    return (
        len(cases["observations.json"]),
        len(cases["inferences.json"]),
        len(cases["upward-only.json"]),
    )


def self_test(fixture_dir: Path | None = None) -> int:
    fixture_dir = FIXTURE_DIR if fixture_dir is None else fixture_dir
    try:
        passed, failures = run_fixtures(fixture_dir)
        obs, inf, up = _counts(fixture_dir)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print("self-test: UNRUNNABLE — %s" % exc, file=sys.stderr)
        return 1

    # Report the instrument's verdict separately from the subject's (Rule 6).
    print("  canary: ARMED — the Incident-1 sentence trips %s; a bare measured "
          "fact trips nothing" % list(_CANARY_INFERENCE_FAMILIES))
    for msg in failures:
        print("  FAIL: %s" % msg, file=sys.stderr)
    total = passed + len(failures)
    line = (
        "self-test: %d/%d assertions pass (%d observation, %d inference, "
        "%d upward-only cases) — canary ARMED" % (passed, total, obs, inf, up)
    )
    if failures:
        line = (
            "self-test: %d/%d assertions pass — %d FAILED"
            % (passed, total, len(failures))
        )
        print(line, file=sys.stderr)
        return 1
    print(line)
    return 0


# --------------------------------------------------------------------------
# --must-fail: plant defects, prove each one is detected. The teeth.
# --------------------------------------------------------------------------


def _mutant_family_deleted(name: str):
    src = {k: v for k, v in FAMILY_SOURCES.items() if k != name}
    return _compile(src)


def must_fail(fixture_dir: Path | None = None) -> int:
    """Every planted defect below MUST be caught. A gate that only proves it can
    pass is half a gate."""
    global _COMPILED, resolve
    fixture_dir = FIXTURE_DIR if fixture_dir is None else fixture_dir
    detected = 0
    planted = 0
    problems = []

    # Mutants 1-5: delete one grammatical family at a time. The single-signal
    # fixture for that family must flip to `observation` and go red BY NAME.
    saved_compiled = _COMPILED
    for name in FAMILY_ORDER:
        planted += 1
        _COMPILED = _mutant_family_deleted(name)
        try:
            _, failures = run_fixtures(fixture_dir)
        finally:
            _COMPILED = saved_compiled
        blob = " | ".join(failures)
        if not failures:
            problems.append(
                "deleting the %s family produced NO failure — that family is "
                "dead weight" % name
            )
        elif "single-%s" % name not in blob:
            problems.append(
                "deleting the %s family went red, but not on its own "
                "single-signal case: %s" % (name, blob)
            )
        else:
            detected += 1
            print("  ok: teeth — deleting the %s family is caught" % name)

    # Mutant 6: blind the instrument entirely. The canary must REFUSE, loudly,
    # rather than returning "observation" for everything.
    planted += 1
    _COMPILED = _compile({})
    try:
        _run_canary()
    except ClassifierBlind:
        detected += 1
        print("  ok: teeth — a fully blinded classifier raises ClassifierBlind")
    else:
        problems.append(
            "a classifier with ZERO patterns passed its own canary — the canary "
            "proves nothing"
        )
    finally:
        _COMPILED = saved_compiled

    # Mutant 7: let the author's kind win. Upward-only is the property that makes
    # this not-a-self-report; if it can be removed silently, nothing holds.
    planted += 1
    saved_resolve = resolve

    def _downgrading_resolve(text, author_kind=None):
        return classify(text) if author_kind is None else str(author_kind)

    resolve = _downgrading_resolve
    try:
        _, failures = run_fixtures(fixture_dir)
    finally:
        resolve = saved_resolve
    blob = " | ".join(failures)
    if failures and "author_kind='observation'" in blob:
        detected += 1
        print("  ok: teeth — a downward re-type (author's kind wins) is caught")
    else:
        problems.append(
            "letting the author downgrade a claim was NOT caught: %s"
            % (blob or "no failures at all")
        )

    for msg in problems:
        print("  FAIL: %s" % msg, file=sys.stderr)

    line = (
        "must-fail: %d/%d planted defects detected (5 family-deletion, "
        "1 blinding, 1 downward-retype) — classifier has teeth" % (detected, planted)
    )
    if problems:
        print(
            "must-fail: %d/%d planted defects detected — %d NOT DETECTED"
            % (detected, planted, len(problems)),
            file=sys.stderr,
        )
        return 1
    print(line)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true", help="run the fixture battery")
    ap.add_argument(
        "--must-fail",
        action="store_true",
        help="plant defects and assert each one is detected",
    )
    ap.add_argument("--text", help="classify a single claim and print its families")
    ap.add_argument(
        "--kind",
        default=None,
        help="the author's own kind for --text (raised, never lowered)",
    )
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.must_fail:
        return must_fail()
    if args.text is not None:
        kind = resolve(args.text, args.kind)
        print("%s\t%s" % (kind, ",".join(families(args.text)) or "-"))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
