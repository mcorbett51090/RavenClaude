#!/usr/bin/env python3
"""
qa_gate.py -- report-regeneration pipeline stage 5: report-qa-gate.

Reads a fidelity-harness receipt (schema: ../../knowledge/fidelity-receipt.schema.json)
and collapses its per-leg verdicts into ONE tiered result -- PASS / PARTIAL / FAIL --
plus a manual-residue checklist for the downstream HUMAN peer reviewer. This script
does not run the harness; it assembles the harness's own receipt (stage 4's output)
into the single verdict a human needs to see before deciding whether a draft is
review-ready.

The honest guarantee (../../knowledge/core-architecture-spec.md sec 1) governs every
line of this file: auto-QA proves the CHECKED surfaces; it never claims "the whole
report is correct/accessible." "Review-ready draft" means the mechanical/QA burden
has been removed -- it is NOT a claim of correctness. Concretely:

  * PASS never means "ship with no human eyes on it" -- it means every proven,
    inference-independent-or-checked leg came back clean. The manual-residue
    checklist is emitted on EVERY run, PASS included, because a11y is only ever
    PARTIALLY auto-covered by axe-core/veraPDF (core-architecture-spec.md sec 5,
    "V5 -- render referee": "proven where deterministic, judged for polish") --
    an EMPTY residue on a shipped report would itself be an over-claim.

Two ADJACENT gates are folded into the same verdict when their sub-receipts are supplied
(they live outside the six-leg fidelity harness, so the harness honestly cannot judge them):

  * the a11y gate (skills/report-a11y-gate/a11y_lint.py) -- a blocking a11y violation (e.g.
    a non-decorative <img> with no alt-text, seeded defect D3) folds the assembled verdict to
    FAIL; its manual residue (the ~30-50% machine-uncheckable WCAG floor) folds into the
    reviewer checklist. An a11y sub-receipt with no blocking violation never downgrades the
    verdict -- its manual residue is expected, not a defect.
  * the injection guard (skills/report-injection-guard/injection_guard.py) -- a blocking
    prompt-injection finding (a force-all-frozen partition anomaly, or an un-provenanced
    token in a `regenerate` slot, seeded defect D13) folds the assembled verdict to FAIL.

The collapsing rule (as specified for this skill, reconciled against the frozen
fidelity-receipt.schema.json `allOf` constraint -- see "Design decisions" below):

  1. Any BLOCKING leg with verdict "fail"/"PROBE_ERROR"/"disabled" (a blocking leg
     that ran-and-failed, crashed, or was neutered), OR a blocking a11y / injection
     sub-receipt failure                                        -> FAIL
  2. Any NON-blocking leg with verdict in
     {"fail", "not_captured", "PARTIAL", "PROBE_ERROR", "disabled"},
     any BLOCKING leg with verdict in {"not_captured", "PARTIAL"},
     or any of the 7 expected legs missing from the receipt     -> PARTIAL (never PASS)
  3. Otherwise (every present leg verdict == "pass", none
     of the 7 expected legs missing, no blocking a11y/injection
     failure)                                                   -> PASS (review-ready draft)

The receipt's own `overall_gate` speaks ONLY to the fidelity legs, so `overclaim_detected` is
computed against the fidelity tier alone -- an a11y/injection failure making the ASSEMBLED
verdict worse than the fidelity receipt's self-report is not an "over-claim" by the receipt.

Design decisions (documented, not left implicit):

  * PROBE_ERROR / disabled on a BLOCKING leg escalate to FAIL (P2 #6), matching the
    harness's own compute_gate (which returns FAIL for any blocking leg whose verdict
    is fail/PROBE_ERROR/disabled). A blocking leg that could not produce a trustworthy
    pass signal — because it crashed (PROBE_ERROR) or was neutered (disabled) — must
    not read as merely "degraded"; softening it to PARTIAL would make qa_gate disagree
    with the receipt's own overall_gate and let a blocking-leg crash ship as a
    non-failing draft. On a NON-blocking leg (e.g. V5) the same verdicts stay a
    PARTIAL-degrade (never PASS), since V5 is proven-where-deterministic / judged-for-
    polish and its crash is not a blocking fidelity defect.
  * "missing Tier-B leg" (per the spec's Fail-closed-degrade section) covers two
    concrete shapes: (a) a leg present but running in a degraded/binding-correctness
    mode -- which the schema already encodes as verdict "PARTIAL" (e.g. V1 with no
    live Power-BI data route) -- and (b) a leg ABSENT from the receipt's `legs[]`
    array entirely. Both are handled: (a) via the PARTIAL-verdict rule above, (b) via
    an explicit missing-legs check against the 7-member expected set
    {V1..V6, period-coherence}.
  * `computed_gate` is independently derived from `legs[]`, not copied from the
    receipt's own `overall_gate` field. If the receipt's self-reported `overall_gate`
    claims something BETTER than what qa_gate independently computes (e.g. it claims
    PASS while a leg is not_captured), that is flagged as `overclaim_detected` and
    `computed_gate` -- never the receipt's self-report -- is authoritative for this
    script's exit code. This mirrors the plugin-wide refusal to trust a self-graded
    result at face value.

Usage:
    python3 qa_gate.py --receipt <receipt.json> [--format text|json]
    python3 qa_gate.py --version

Exit codes:
    0 -- computed_gate == PASS
    1 -- computed_gate == FAIL (a blocking leg ran and found a real defect)
    2 -- usage / path-guard / I/O / JSON-parse / receipt-shape error (message on
         stderr + a best-effort JSON error object on stdout, so a caller parsing
         stdout never gets truncated JSON -- mirrors seed_defects.py's `_emit_error`)
    3 -- computed_gate == PARTIAL (never a success exit; distinct from the hard I/O
         error code 2 so a caller can tell "ran degraded" from "couldn't run at all")

Design constraints (binding): stdlib only (argparse, json, sys, pathlib). No network,
no subprocess, no third-party imports. Path-guarded: --receipt must be a relative
path, must not contain '..', and must resolve to a location inside the repository
root (same convention as seed_defects.py's `_guard_path` / check_refs.py's
`_resolve_safe`). Python 3.9.6 target: no `X | Y` union syntax, no `match` statements.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GATE_VERSION = "1.0.0"
SCHEMA = "report-regeneration/qa-gate@1"

# The fidelity harness is "six legs + period-coherence" (core-architecture-spec.md
# sec 5). A receipt missing any one of these is treated as PARTIAL, never PASS.
EXPECTED_LEGS = ["V1", "V2", "V3", "V4", "V5", "V6", "period-coherence"]

VALID_VERDICTS = {"pass", "fail", "not_captured", "PARTIAL", "PROBE_ERROR", "disabled"}
VALID_LABELS = {"proven", "judged"}
VALID_FORMATS = {"html", "office"}
VALID_GATES = {"PASS", "PARTIAL", "FAIL"}

# The two adjacent gates whose sub-receipts fold into the assembled verdict. Each is a dict
# with at least {"schema", "gate"} where gate is in VALID_GATES. They are OPTIONAL: when a
# sub-receipt is not supplied, the assembled verdict is the fidelity tier alone (backward
# compatible with a harness-only caller).
A11Y_SCHEMA = "report-regeneration/a11y-gate@1"
INJECTION_SCHEMA = "report-regeneration/injection-guard@1"

# Verdicts that keep a leg out of the "clean" bucket but do NOT, on their own,
# escalate to the hard FAIL tier (reserved for a BLOCKING leg with verdict=="fail").
_DEGRADE_VERDICTS = {"not_captured", "PARTIAL", "PROBE_ERROR"}

_GATE_RANK = {"FAIL": 0, "PARTIAL": 1, "PASS": 2}
_EXIT_CODE = {"PASS": 0, "FAIL": 1, "PARTIAL": 3}

# The "Question" column of core-architecture-spec.md sec 5's leg table, quoted
# verbatim -- used to make a not_captured/missing-leg checklist item legible
# without forcing the reviewer back to the spec.
_LEG_QUESTIONS = {
    "V1": "did value V from source S land in region R?",
    "V2": "did anything change outside the bound anchors?",
    "V3": "is the output's structure the template's?",
    "V4": "did any old-client data survive?",
    "V5": "does it render / lay out correctly?",
    "V6": "is the partition itself correct?",
    "period-coherence": "does the label match the value's period?",
}

# The human-WCAG residue -- the roughly 30-50% of WCAG that structural checkers
# (axe-core, veraPDF) cannot judge because it requires human sense-making, not
# schema/DOM validity. Present on EVERY run, PASS included: a11y is only ever
# partially auto-covered, so an empty residue would itself be an over-claim
# (core-architecture-spec.md sec 1; fidelity-receipt.schema.json `manual_residue`
# field description).
CANONICAL_WCAG_RESIDUE = [
    "Alt-text QUALITY, not just presence -- does each image/chart alt-text "
    "accurately and usefully describe its informational content? (axe/veraPDF "
    "check presence/emptiness, not adequacy.)",
    "Reading-order SENSE -- does the underlying tag/DOM order match the visually "
    "intended reading order for a screen-reader user? (structural checkers confirm "
    "an order exists, not that it makes sense.)",
    "Plain-language / cognitive load -- is prose written at an appropriate reading "
    "level, with jargon/abbreviations expanded on first use?",
    "Heading-hierarchy MEANING -- do heading levels reflect the document's actual "
    "semantic structure, beyond merely nesting without gaps?",
    "Color-independent meaning -- where color conveys information (e.g. a "
    "red/green KPI), is the same information also conveyed via text/pattern/icon?",
    "Complex-table header association SENSE -- for any table with merged/nested "
    "headers, do header/id or scope associations logically match, beyond schema "
    "validity?",
    "Non-text-media equivalents -- captions/transcripts for any embedded "
    "video/audio; a real long-description for any complex chart beyond a "
    "one-line alt.",
    "Focus order and keyboard operability for any interactive element embedded "
    "in the report -- outside the static-DOM/PDF scope axe/veraPDF cover.",
    "Overall substantive correctness / professional judgment -- auto-QA proves "
    "only the checked surfaces; it never claims the whole report is correct or "
    "accessible (the honest guarantee, core-architecture-spec.md sec 1).",
]


class QAGateError(Exception):
    """Raised for any path-guard, I/O, JSON-parse, or receipt-shape violation
    (exit 2)."""


# ---- path safety (mirrors seed_defects.py's _repo_root/_guard_path convention) ----

def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    root = here
    for _ in range(10):
        if (root / ".repo-layout.json").is_file() or (root / "AGENTS.md").is_file():
            return root
        if root.parent == root:
            break
        root = root.parent
    # Fallback: this file lives at
    # plugins/report-regeneration/skills/report-qa-gate/qa_gate.py
    return (here / ".." / ".." / ".." / "..").resolve()


def _guard_path(raw: str) -> Path:
    """Resolve `raw` and reject traversal / absolute-escape / a nonexistent file.
    Never touches the filesystem outside the repo root. Raises QAGateError (never a
    bare OSError) on any violation."""
    if not raw:
        raise QAGateError("empty path")
    p = Path(raw)
    if p.is_absolute():
        raise QAGateError(f"absolute paths are not allowed: {raw!r}")
    if ".." in p.parts:
        raise QAGateError(f"path traversal ('..') is not allowed: {raw!r}")
    repo_root = _repo_root().resolve()
    resolved = (Path.cwd() / p).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise QAGateError(f"path escapes the repo root: {resolved}") from exc
    if not resolved.is_file():
        raise QAGateError(f"receipt file not found: {raw!r} (resolved {resolved})")
    return resolved


# ---- receipt loading + light schema validation (no jsonschema dependency) ----

def validate_receipt(receipt: dict) -> None:
    """Validate `receipt` against the load-bearing shape of
    fidelity-receipt.schema.json (stdlib-only -- no jsonschema). Raises
    QAGateError with a specific message on the first violation found."""
    if not isinstance(receipt, dict):
        raise QAGateError("receipt root must be a JSON object")

    required = [
        "receipt_version", "run_id", "format", "generated_at", "ttl_seconds",
        "env_fingerprint", "overall_gate", "legs",
    ]
    missing = [k for k in required if k not in receipt]
    if missing:
        raise QAGateError(f"receipt missing required field(s): {', '.join(missing)}")

    if receipt["format"] not in VALID_FORMATS:
        raise QAGateError(
            f"receipt 'format' must be one of {sorted(VALID_FORMATS)}, "
            f"got {receipt['format']!r}"
        )
    if receipt["overall_gate"] not in VALID_GATES:
        raise QAGateError(
            f"receipt 'overall_gate' must be one of {sorted(VALID_GATES)}, "
            f"got {receipt['overall_gate']!r}"
        )

    legs = receipt["legs"]
    if not isinstance(legs, list) or not legs:
        raise QAGateError("receipt 'legs' must be a non-empty array")

    leg_required = ["leg", "verdict", "label", "inference_independent", "blocking"]
    for i, leg in enumerate(legs):
        if not isinstance(leg, dict):
            raise QAGateError(f"legs[{i}] must be an object")
        leg_missing = [k for k in leg_required if k not in leg]
        if leg_missing:
            raise QAGateError(
                f"legs[{i}] missing required field(s): {', '.join(leg_missing)}"
            )
        if leg["leg"] not in EXPECTED_LEGS:
            raise QAGateError(
                f"legs[{i}].leg must be one of {EXPECTED_LEGS}, got {leg['leg']!r}"
            )
        if leg["verdict"] not in VALID_VERDICTS:
            raise QAGateError(
                f"legs[{i}].verdict must be one of {sorted(VALID_VERDICTS)}, "
                f"got {leg['verdict']!r}"
            )
        if leg["label"] not in VALID_LABELS:
            raise QAGateError(
                f"legs[{i}].label must be one of {sorted(VALID_LABELS)}, "
                f"got {leg['label']!r}"
            )
        if not isinstance(leg["inference_independent"], bool):
            raise QAGateError(f"legs[{i}].inference_independent must be a boolean")
        if not isinstance(leg["blocking"], bool):
            raise QAGateError(f"legs[{i}].blocking must be a boolean")


def load_receipt(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise QAGateError(f"could not read receipt file: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise QAGateError(f"receipt is not valid JSON: {exc}") from exc
    validate_receipt(data)
    return data


def _load_json_guarded(raw: str) -> dict:
    """Path-guard + load a JSON sub-receipt (a11y / injection). Shape is validated later by
    `_validate_subreceipt` against its expected schema tag."""
    path = _guard_path(raw)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QAGateError(f"sub-receipt is not valid JSON: {exc}") from exc
    return data


# ---- the collapsing rule ----

def compute_tier(receipt: dict) -> dict:
    """Independently derive the tiered verdict from `receipt["legs"]`. Returns a
    dict with `computed_gate`, `blocking_leg_failures`, `degraded_legs`,
    `missing_legs`, and human-readable `reasons`."""
    legs = receipt["legs"]
    seen_leg_ids = set()
    blocking_leg_failures = []
    degraded_legs = []
    reasons = []

    for leg in legs:
        leg_id = leg["leg"]
        seen_leg_ids.add(leg_id)
        verdict = leg["verdict"]
        blocking = leg["blocking"]

        if verdict == "pass":
            continue
        # P2 #6 — a BLOCKING leg that FAILED, that crashed (PROBE_ERROR), or that was neutered
        # (disabled, the test-only must-fail knob) escalates to the hard FAIL tier, matching the
        # harness's own compute_gate (a blocking PROBE_ERROR/disabled is never a mere degrade there,
        # so qa_gate must not soften it to PARTIAL and disagree with the receipt's overall_gate).
        if blocking and verdict in ("fail", "PROBE_ERROR", "disabled"):
            blocking_leg_failures.append(leg)
        else:
            # verdict in {"fail" (non-blocking), "not_captured", "PARTIAL", "PROBE_ERROR",
            # "disabled" (non-blocking)} -- never a pass, never on its own a hard FAIL; forbids
            # PASS (see module docstring "Design decisions").
            degraded_legs.append(leg)

    missing_legs = sorted(set(EXPECTED_LEGS) - seen_leg_ids)

    if blocking_leg_failures:
        gate = "FAIL"
        for leg in blocking_leg_failures:
            reasons.append(
                f"BLOCKING leg {leg['leg']} verdict={leg.get('verdict', 'fail')} -- "
                f"{leg.get('evidence', 'no evidence given')}"
            )
    elif degraded_legs or missing_legs:
        gate = "PARTIAL"
        for leg in degraded_legs:
            role = "blocking" if leg["blocking"] else "non-blocking"
            reasons.append(
                f"leg {leg['leg']} verdict={leg['verdict']} ({role}) -- "
                f"degraded/never-pass"
            )
        for leg_id in missing_legs:
            reasons.append(
                f"leg {leg_id} absent from receipt -- treated as not_captured"
            )
    else:
        gate = "PASS"
        reasons.append("every leg verdict is 'pass'; no missing legs")

    return {
        "computed_gate": gate,
        "blocking_leg_failures": [leg["leg"] for leg in blocking_leg_failures],
        "degraded_legs": [
            {"leg": leg["leg"], "verdict": leg["verdict"], "blocking": leg["blocking"]}
            for leg in degraded_legs
        ],
        "missing_legs": missing_legs,
        "reasons": reasons,
    }


# ---- manual-residue checklist ----

def build_manual_residue_checklist(receipt: dict, tier: dict) -> list:
    """Build the manual-residue checklist for the human peer reviewer. NEVER
    empty (CANONICAL_WCAG_RESIDUE is unconditional) -- an empty residue on a
    partially-auto-covered a11y surface would itself be a defect (over-claim)."""
    checklist = []

    for item in CANONICAL_WCAG_RESIDUE:
        checklist.append({"category": "manual-wcag-residue", "detail": item})

    for item in receipt.get("manual_residue") or []:
        checklist.append({"category": "receipt-reported-residue", "detail": item})

    for leg in receipt["legs"]:
        evidence = leg.get("evidence") or ""
        if "needs-review" in evidence.lower() or "needs_review" in evidence.lower():
            checklist.append({
                "category": "needs-review-node",
                "detail": f"{leg['leg']}: {evidence}",
            })

    for leg in receipt["legs"]:
        if leg["verdict"] == "not_captured":
            question = _LEG_QUESTIONS.get(leg["leg"], "see core-architecture-spec.md sec 5")
            checklist.append({
                "category": "leg-not-captured",
                "detail": (
                    f"{leg['leg']} did not run -- manually verify what this leg "
                    f"would have checked ({question})."
                ),
            })

    for leg_id in tier["missing_legs"]:
        question = _LEG_QUESTIONS.get(leg_id, "see core-architecture-spec.md sec 5")
        checklist.append({
            "category": "leg-missing",
            "detail": (
                f"{leg_id} is absent from this receipt entirely -- manually verify "
                f"({question})."
            ),
        })

    for leg in receipt["legs"]:
        if leg["leg"] == "V1" and leg["verdict"] == "PARTIAL":
            checklist.append({
                "category": "values-unverified",
                "detail": (
                    "V1 (value accuracy) ran in binding-correctness mode -- no live "
                    "Power BI data-read route was reachable at harness time. The "
                    "Accurate rubric dimension fails closed to 'unverified'. A human "
                    "MUST independently confirm every PBI-sourced figure against the "
                    "new source before this draft ships."
                ),
            })

    return checklist


# ---- adjacent-gate sub-receipts (a11y + injection) ----

def _validate_subreceipt(sub: dict, expected_schema: str, kind: str) -> str:
    """Light-validate an a11y / injection sub-receipt and return its gate. Raises QAGateError
    (exit 2) on a malformed sub-receipt -- a gate that cannot be read is never trusted as PASS."""
    if not isinstance(sub, dict):
        raise QAGateError(f"{kind} sub-receipt must be a JSON object")
    schema = sub.get("schema")
    if schema != expected_schema:
        raise QAGateError(
            f"{kind} sub-receipt has schema {schema!r}, expected {expected_schema!r}"
        )
    gate = sub.get("gate")
    if gate not in VALID_GATES:
        raise QAGateError(
            f"{kind} sub-receipt 'gate' must be one of {sorted(VALID_GATES)}, got {gate!r}"
        )
    return gate


def _worse(a: str, b: str) -> str:
    """Return the worse (lower-ranked) of two gate tiers -- FAIL < PARTIAL < PASS."""
    return a if _GATE_RANK[a] <= _GATE_RANK[b] else b


# ---- assembling the final result ----

def build_result(receipt: dict, a11y: dict = None, injection: dict = None) -> dict:
    """Collapse the fidelity receipt (and, when supplied, the a11y + injection sub-receipts)
    into one tiered verdict. `a11y` / `injection` are OPTIONAL: with neither, the assembled
    verdict is the fidelity tier alone (a harness-only caller is unchanged)."""
    validate_receipt(receipt)
    tier = compute_tier(receipt)
    residue = build_manual_residue_checklist(receipt, tier)

    claimed = receipt["overall_gate"]
    fidelity_gate = tier["computed_gate"]
    # over-claim is judged against the FIDELITY tier only: the receipt's overall_gate speaks to
    # its own legs, not to the adjacent a11y/injection gates it never saw.
    overclaim = _GATE_RANK[claimed] > _GATE_RANK[fidelity_gate]

    reasons = list(tier["reasons"])
    if overclaim:
        reasons.append(
            f"OVER-CLAIM: receipt's own overall_gate={claimed!r} is better than "
            f"the independently computed {fidelity_gate!r} derived from its legs -- "
            f"computed_gate is authoritative for this script's verdict/exit code."
        )

    computed = fidelity_gate
    aux_gate_failures: list = []

    a11y_gate = None
    if a11y is not None:
        a11y_gate = _validate_subreceipt(a11y, A11Y_SCHEMA, "a11y")
        computed = _worse(computed, a11y_gate)
        if a11y_gate == "FAIL":
            aux_gate_failures.append("a11y")
            for v in a11y.get("violations", []):
                if v.get("blocking"):
                    reasons.append(
                        f"BLOCKING a11y violation {v.get('rule')} @ {v.get('node')} -- "
                        f"{v.get('detail', 'no detail')}"
                    )
                    residue.append({
                        "category": "a11y-blocking",
                        "detail": f"[{v.get('rule')} WCAG {v.get('wcag')}] {v.get('node')}: "
                                  f"{v.get('detail', '')}",
                    })
        # a11y manual residue (the ~30-50% floor + advisory flags) always folds into the
        # reviewer checklist, PASS or FAIL -- an empty a11y residue would itself be an over-claim.
        for item in a11y.get("manual_residue", []):
            residue.append({"category": "a11y-manual-residue", "detail": item})

    injection_gate = None
    if injection is not None:
        injection_gate = _validate_subreceipt(injection, INJECTION_SCHEMA, "injection")
        computed = _worse(computed, injection_gate)
        if injection_gate == "FAIL":
            aux_gate_failures.append("injection")
            for f in injection.get("findings", []):
                if f.get("blocking"):
                    reasons.append(
                        f"BLOCKING injection finding {f.get('check')} @ {f.get('node')} "
                        f"({f.get('token')}) -- {f.get('detail', 'no detail')}"
                    )
                    residue.append({
                        "category": "injection-blocking",
                        "detail": f"[{f.get('check')}] {f.get('node')} :: {f.get('token')} -- "
                                  f"{f.get('detail', '')}",
                    })

    if not residue:
        # Defensive: CANONICAL_WCAG_RESIDUE is unconditional, so this should be unreachable.
        raise QAGateError(
            "internal invariant violated: manual-residue checklist is empty "
            "(an empty residue on a partially-auto-covered a11y surface is "
            "itself a defect -- over-claim)"
        )

    return {
        "schema": SCHEMA,
        "gate_version": GATE_VERSION,
        "run_id": receipt["run_id"],
        "format": receipt["format"],
        "receipt_claimed_gate": claimed,
        "fidelity_gate": fidelity_gate,
        "a11y_gate": a11y_gate,
        "injection_gate": injection_gate,
        "aux_gate_failures": aux_gate_failures,
        "computed_gate": computed,
        "overclaim_detected": overclaim,
        "review_ready": computed == "PASS",
        "blocking_leg_failures": tier["blocking_leg_failures"],
        "degraded_legs": tier["degraded_legs"],
        "missing_legs": tier["missing_legs"],
        "reasons": reasons,
        "manual_residue_checklist": residue,
    }


# ---- CLI ----

def _emit_error(message: str) -> None:
    print(json.dumps({"schema": SCHEMA, "ok": False, "error": message}), file=sys.stdout)
    print(f"[error] {message}", file=sys.stderr)


def _print_text(result: dict) -> None:
    print(f"report-qa-gate v{GATE_VERSION} -- run {result['run_id']} ({result['format']})")
    print(f"  receipt claims:    {result['receipt_claimed_gate']}")
    print(f"  fidelity gate:     {result['fidelity_gate']}")
    if result["a11y_gate"] is not None:
        print(f"  a11y gate:         {result['a11y_gate']}")
    if result["injection_gate"] is not None:
        print(f"  injection gate:    {result['injection_gate']}")
    tag = "  <-- AUTHORITATIVE (over-claim detected)" if result["overclaim_detected"] else ""
    print(f"  computed verdict:  {result['computed_gate']}{tag}")
    if result["aux_gate_failures"]:
        print(f"  adjacent gate failure(s): {', '.join(result['aux_gate_failures'])}")
    print(f"  review-ready draft: {'yes' if result['review_ready'] else 'no'}")
    if result["blocking_leg_failures"]:
        print(f"  BLOCKING leg failure(s): {', '.join(result['blocking_leg_failures'])}")
    if result["degraded_legs"]:
        print("  degraded/non-pass leg(s):")
        for leg in result["degraded_legs"]:
            role = "blocking" if leg["blocking"] else "non-blocking"
            print(f"    - {leg['leg']}: {leg['verdict']} ({role})")
    if result["missing_legs"]:
        print(f"  missing leg(s): {', '.join(result['missing_legs'])}")
    print("  reasons:")
    for reason in result["reasons"]:
        print(f"    - {reason}")
    n = len(result["manual_residue_checklist"])
    print(f"  manual-residue checklist ({n} item(s)) -- human peer review REQUIRED "
          f"regardless of gate tier:")
    for item in result["manual_residue_checklist"]:
        print(f"    [{item['category']}] {item['detail']}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="qa_gate.py",
        description=(
            "Collapse a report-regeneration fidelity-harness receipt into ONE "
            "tiered verdict (PASS/PARTIAL/FAIL) plus a manual-residue checklist "
            "for the human peer reviewer."
        ),
    )
    p.add_argument(
        "--receipt", metavar="PATH",
        help="path to a fidelity-receipt JSON file, relative, no traversal "
             "(e.g. tests/fixtures/report-regeneration/receipt-clean.json)",
    )
    p.add_argument(
        "--a11y", metavar="PATH", default=None,
        help="optional a11y-gate sub-receipt JSON (from report-a11y-gate/a11y_lint.py) to fold "
             "into the assembled verdict; relative, no traversal",
    )
    p.add_argument(
        "--injection", metavar="PATH", default=None,
        help="optional injection-guard sub-receipt JSON (from report-injection-guard/"
             "injection_guard.py) to fold into the assembled verdict; relative, no traversal",
    )
    p.add_argument(
        "--format", dest="out_format", choices=["json", "text"], default="text",
        help="output format (default: text)",
    )
    p.add_argument(
        "--version", action="store_true", help="print the gate version and exit",
    )
    return p


def main(argv: list) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(GATE_VERSION)
        return 0

    if not args.receipt:
        parser.print_usage(sys.stderr)
        _emit_error("--receipt is required (or pass --version)")
        return 2

    try:
        path = _guard_path(args.receipt)
        receipt = load_receipt(path)
        a11y = _load_json_guarded(args.a11y) if args.a11y else None
        injection = _load_json_guarded(args.injection) if args.injection else None
        result = build_result(receipt, a11y=a11y, injection=injection)
    except QAGateError as exc:
        _emit_error(str(exc))
        return 2

    if args.out_format == "json":
        print(json.dumps(result))
    else:
        _print_text(result)

    return _EXIT_CODE[result["computed_gate"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
