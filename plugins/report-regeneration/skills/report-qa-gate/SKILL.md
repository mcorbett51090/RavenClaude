---
name: report-qa-gate
description: "Pipeline stage 5 of report-regeneration: collapses a fidelity-harness receipt (fidelity-receipt.schema.json, the six-leg + period-coherence harness) PLUS the two adjacent-gate sub-receipts (report-a11y-gate + report-injection-guard, both OPTIONAL) into ONE tiered verdict via qa_gate.py -- any BLOCKING leg fail OR a blocking a11y/injection failure => FAIL; any not_captured/PARTIAL/PROBE_ERROR leg or missing leg => PARTIAL (never PASS); every leg pass + no blocking a11y/injection => PASS (review-ready draft). Also emits a manual-residue checklist (human-WCAG residue, needs-review nodes, not_captured legs, V1 binding-correctness 'values unverified' note, folded a11y residue) that is NEVER empty. Stdlib-only, exit-coded, path-guarded. Does not run the harness/gates itself -- consumes their receipts."
---

# Skill: report-qa-gate

## What this is

A **stdlib-only, exit-coded CLI** -- [`qa_gate.py`](qa_gate.py) -- that reads one
fidelity-harness receipt (the output of stage 4, `report-regeneration`'s six-leg +
period-coherence harness) and answers the question a human reviewer actually asks:
*"can I trust this draft enough to start reviewing it, and what am I still on the
hook for?"* It does **not** run the harness -- it assembles the harness's own
receipt into a single tiered verdict plus a checklist of what a machine structurally
cannot verify.

This skill is stage 5 of the `report-regeneration` pipeline. Read first, before
touching the code: [`../../knowledge/core-architecture-spec.md`](../../knowledge/core-architecture-spec.md)
sec 5 ("The fidelity harness -- 6 legs + period-coherence") and sec 1 (the honest
guarantee), and [`../../knowledge/fidelity-receipt.schema.json`](../../knowledge/fidelity-receipt.schema.json)
(the frozen input contract this script codes to).

## The honest guarantee, restated for this skill

Per [`../../CLAUDE.md`](../../CLAUDE.md) sec 1, the plugin guarantees only (a) no
old-client-data leak and (b) every low-confidence classification is surfaced for
human review. **Auto-QA proves the checked surfaces; it never claims the whole
report is correct or accessible.** `report-qa-gate` never softens this: a `PASS`
verdict means "every proven leg came back clean," not "no human needs to look at
this." That is why the manual-residue checklist ships on **every** run -- PASS
included -- rather than only when something failed.

## The collapsing rule

| Condition | `computed_gate` |
|---|---|
| Any **BLOCKING** leg has verdict `fail`, **OR** a supplied a11y / injection sub-receipt has `gate: FAIL` | **FAIL** |
| Any leg (blocking or not) has verdict `not_captured` / `PARTIAL` / `PROBE_ERROR`, any **non**-blocking leg has verdict `fail`, or any of the 7 expected legs (`V1`-`V6`, `period-coherence`) is absent from the receipt | **PARTIAL** (never PASS) |
| Every present leg is `pass`, none of the 7 expected legs is missing, and no supplied a11y/injection sub-receipt failed | **PASS** (review-ready draft) |

FAIL always wins over PARTIAL, which always wins over PASS -- the tier is the worst
outcome across every leg **and every folded adjacent gate**, never an average.

### The two adjacent gates (a11y + injection)

`build_result(receipt, a11y=None, injection=None)` folds two OPTIONAL sub-receipts -- from
[`../report-a11y-gate`](../report-a11y-gate) and
[`../report-injection-guard`](../report-injection-guard) -- into the same verdict. They live
**outside** the six-leg fidelity harness (the harness honestly cannot judge a11y or injection), so
the harness reports `PARTIAL`/`PASS` on its own legs and the adjacent gate supplies the crisp
catch:

- a blocking **a11y** violation (e.g. seeded defect **D3**, a non-decorative `<img>` with no
  alt-text) folds the assembled verdict to **FAIL**; the a11y `manual_residue` (the ~30-50%
  machine-uncheckable WCAG floor) folds into the reviewer checklist under `a11y-manual-residue`,
  blocking violations under `a11y-blocking`. An a11y sub-receipt with no blocking violation never
  downgrades the verdict -- its residue is expected, not a defect.
- a blocking **injection** finding (e.g. seeded defect **D13**, a force-all-frozen partition
  anomaly or an un-provenanced token in a `regenerate` slot) folds the assembled verdict to
  **FAIL**; findings surface under `injection-blocking`.

With **neither** sub-receipt supplied, the assembled verdict is the fidelity tier alone -- a
harness-only caller is fully backward compatible (`a11y_gate` / `injection_gate` are `null`).
`overclaim_detected` is judged against the **fidelity tier only**: the receipt's `overall_gate`
speaks to its own legs, so an a11y/injection failure making the assembled verdict worse than the
receipt's self-report is **not** an over-claim by the receipt.

### Design decisions (documented, not left implicit)

- **`PROBE_ERROR` is grouped with `not_captured`, not with `fail`.** The receipt
  schema's own field description treats them as a pair -- both mean "this leg
  produced no trustworthy pass/fail signal" (a harness crash, or a leg that
  couldn't run at all), which degrades to `PARTIAL`. `fail` means a leg **ran and
  found a real defect**, which is the only thing that escalates a **blocking** leg
  to the harder `FAIL` tier. A blocking leg that merely crashed still forbids
  `PASS` -- it just doesn't get the harder label reserved for a proven hit.
- **"missing Tier-B leg"** (core-architecture-spec.md sec 5's fail-closed-degrade
  language) covers two concrete shapes, both handled: (a) a leg present but running
  degraded -- the schema already encodes this as verdict `PARTIAL` (e.g. V1 with no
  live Power BI data route -- "the Accurate rubric dimension fails closed to
  'unverified,' never PASS"); (b) a leg **absent** from `legs[]` entirely, checked
  against the 7-member expected set.
- **`computed_gate` is independently derived from `legs[]`, never copied from the
  receipt's own `overall_gate`.** If a receipt's self-reported `overall_gate` claims
  something *better* than what `qa_gate.py` computes (e.g. it says `PASS` while a
  leg is `not_captured`), that is flagged as `overclaim_detected` and
  `computed_gate` -- not the self-report -- drives this script's exit code. A
  self-graded verdict is never trusted at face value.

## The manual-residue checklist

Emitted every run, in every tier, as a list of `{category, detail}` objects:

| Category | When it appears |
|---|---|
| `manual-wcag-residue` | **Always** -- the ~30-50% of WCAG that axe-core/veraPDF structurally cannot judge: alt-text *quality* (not presence), reading-order *sense*, plain-language/cognitive load, heading-hierarchy *meaning*, color-independent meaning, complex-table header *sense*, non-text-media equivalents, focus order/keyboard operability, and overall substantive judgment. |
| `receipt-reported-residue` | The receipt's own `manual_residue` array (if the harness populated one), echoed through. |
| `needs-review-node` | Any leg whose `evidence` text mentions "needs-review" / "needs_review" -- surfaces the flagged node even when the leg's own verdict is `pass` (a leg can pass its aggregate check while still calling out one node for human sign-off). |
| `leg-not-captured` | Every leg with verdict `not_captured`, naming the leg's own "Question" from the spec table so the reviewer knows exactly what to check by hand. |
| `leg-missing` | Every one of the 7 expected legs absent from the receipt entirely. |
| `values-unverified` | When `V1` ran with verdict `PARTIAL` (binding-correctness degrade, no live PBI data route) -- an explicit instruction that the human MUST independently confirm every PBI-sourced figure. |

The checklist is **never empty** -- `manual-wcag-residue` is unconditional, so even
a clean `PASS` receipt still surfaces 9 human-judgment items. `build_result()`
defensively raises if the checklist were ever empty, treating that as the
over-claim it would be.

## CLI contract

```text
python3 plugins/report-regeneration/skills/report-qa-gate/qa_gate.py --receipt <PATH> [--format text|json]
python3 plugins/report-regeneration/skills/report-qa-gate/qa_gate.py --version
```

`<PATH>` MUST be relative, MUST NOT contain `..`, and MUST resolve inside the repo
root (else exit 2) -- the same path-guard convention as `seed_defects.py` and
`check_refs.py`.

| Exit code | Meaning |
|---|---|
| `0` | `computed_gate == PASS` |
| `1` | `computed_gate == FAIL` (a blocking leg ran and found a real defect) |
| `2` | usage / path-guard / I/O / JSON-parse / receipt-shape error |
| `3` | `computed_gate == PARTIAL` (never a success exit; distinct from `2` so a caller can tell "ran degraded" from "couldn't run at all") |

`--format json` emits the full envelope on stdout: `schema`, `gate_version`,
`run_id`, `format`, `receipt_claimed_gate`, `computed_gate`, `overclaim_detected`,
`review_ready`, `blocking_leg_failures`, `degraded_legs`, `missing_legs`, `reasons`,
`manual_residue_checklist`. `--format text` (the default) prints the same
information as human-readable lines.

## Dependency / purity contract

Stdlib only (`argparse`, `json`, `sys`, `pathlib`). No network, no subprocess, no
third-party imports (no `jsonschema` -- the schema shape is validated by hand in
`validate_receipt()` against the required fields / enums in
`fidelity-receipt.schema.json`). Targets Python 3.9.6: no `X | Y` union syntax, no
`match` statements.

## When this runs in the pipeline

After stage 4 (the fidelity harness) emits a receipt for a candidate review-ready
draft, and before the draft is handed to the human peer reviewer. `report-qa-gate`
is the last automated step -- its output is what a human reads to decide whether to
start reviewing, and its manual-residue checklist is the literal to-do list they
work from. It never gates a re-run of the harness itself; a `PARTIAL`/`FAIL`
verdict routes back to whichever upstream stage owns the failing leg (surgical
rebind for a `V1`/`V2` miss, structure inference for `V3`, the egress scanner for
`V4`, the render pipeline for `V5`, the manifest for `V6`).

## Scope boundary

This skill assembles a verdict from an **existing** receipt -- it does not
implement any of the six legs or the period-coherence check, and it does not
mutate the draft. Leg implementation lives in the (separate) fidelity-harness
build; RSG/manifest concerns live in the structure-inference and binding-manifest
stages. `report-qa-gate` is intentionally the thinnest possible layer over the
frozen schema so that a change to a leg's semantics never requires touching this
script -- only a genuine change to the collapsing rule or the residue checklist
does.

## Tests

[`tests/test_qa_gate.py`](tests/test_qa_gate.py) -- 25 unittest cases: the four
required cases (V4-fail -> FAIL, not_captured-V5 -> PARTIAL, clean -> PASS,
non-empty residue in the PARTIAL case), plus the never-empty-on-PASS invariant,
needs-review extraction, the V1-degrade values-unverified note, missing-leg
handling, non-blocking-fail vs blocking-fail tiering, PROBE_ERROR-degrades-not-FAIL,
over-claim detection, receipt-shape validation, path-guard rejection, and CLI
exit-code coverage (0/1/2/3) via subprocess.

```bash
python3 plugins/report-regeneration/skills/report-qa-gate/tests/test_qa_gate.py -v
```
