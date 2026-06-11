# Outcomes & value-based care — reference

Deep reference for the `outcomes-and-quality-analyst`. Companion to
[`pt-practice-decision-trees.md`](pt-practice-decision-trees.md).

> **Compliance note:** MIPS and value-based program rules and measures change yearly. Treat all
> specifics as `[verify against current program rules and a compliance professional]`.

---

## MCID — the meaning of a meaningful change

A change in a functional outcome measure is only clinically meaningful if it exceeds the **minimal
clinically important difference (MCID)** for that measure. "Improved 6 points" means nothing until set
against the MCID (e.g., 8). Report change against MCID and the baseline, not as a raw delta. Use
[`../scripts/pt_calc.py`](../scripts/pt_calc.py) `outcome_change_vs_mcid`.

## Collection cadence

| Point | Captures | If missed |
|---|---|---|
| Intake | baseline | every later score is uninterpretable |
| Interval | progress | no mid-episode course correction |
| Discharge | outcome | the outcome itself is lost |

Consistency of measure per region is what makes the data comparable across clinicians and time.

## Outcomes as the medical-necessity bridge

Documented functional progress toward a goal, plus the remaining gap to that goal, is the evidence
that justifies continued, reimbursable visits. This is where the clinical and financial align: good
outcome capture defends the claim and improves care simultaneously.

## Patient-reported outcomes

PROs (patient-reported function, pain, satisfaction) complement performance measures and are
increasingly tied to value-based reporting. Capture them in the workflow, not retrospectively.

## Quality / value-based readiness

- Identify the applicable quality measures for the clinic's program participation.
- Audit data completeness — partial capture fails reporting thresholds.
- Build point-of-care capture so the data exists when reporting is due.
- Flag the program specifics (applicable measures, thresholds, scoring) for verification.

## Benchmarking honestly

Benchmark change scores by clinician and diagnosis against MCID and any external benchmark — but treat
external benchmark figures as `[unverified — segment/region/date-dependent]` and validate against the
clinic's own data before any deliverable, per the Claim-Grounding protocol.
