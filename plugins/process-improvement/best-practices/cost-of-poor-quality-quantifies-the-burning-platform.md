# Cost of Poor Quality Quantifies the Burning Platform

**Status:** Pattern
**Domain:** Process Improvement — Define / business case
**Applies to:** `process-improvement`

---

## Why this exists

A DMAIC project without a financial justification competes for sponsorship against every other organizational priority on subjective grounds. Cost of Poor Quality (COPQ) converts a process symptom — "we have a lot of rework" — into a dollar figure that makes the business case for the project and sets the expected return. Projects with a documented COPQ get funded; projects that say "it's slow and people are frustrated" frequently don't. COPQ also provides the financial baseline against which the Control phase measures hard-dollar ROI.

## How to apply

COPQ is organized into four cost categories (the **Cost of Quality** model):

| Category | Definition | Examples |
|---|---|---|
| **Internal failure** | Cost of defects caught *before* the customer sees them | Rework, scrap, re-inspection, re-processing |
| **External failure** | Cost of defects the customer *experienced* | Returns, warranty claims, credits, complaint handling, lost accounts |
| **Appraisal** | Cost of *inspecting* to find defects | Inspection time, testing, audits (labor + tools) |
| **Prevention** | Cost of *preventing* defects | Training, process design, mistake-proofing investment |

> COPQ in the Six Sigma context is the sum of **internal failure + external failure + appraisal** — the money that exists solely because the process is not perfect. Prevention is the investment that reduces COPQ.

**Calculation steps:**
1. Identify failure events using defect counts from the baseline.
2. Attach a unit cost per failure event (labor hours × rate, plus material and overhead where applicable).
3. Sum across the measurement period to get the annualized COPQ.
4. Document assumptions and data sources.

**Do:**
- Present COPQ in the Define phase charter as the financial size of the problem.
- Re-compute the COPQ after the Control phase at the same metric definitions to show the hard-dollar gain.
- Use conservative assumptions; a COPQ that can survive a 30% auditor haircut is more credible than an optimistic one.

**Don't:**
- Double-count: a rework cost that appears in both internal failure and appraisal.
- Include prevention investment as part of COPQ (it is the cure, not the cost).
- Report a COPQ without documenting which cost categories were included and excluded.

## Edge cases / when the rule does NOT apply

- **Regulatory or safety-driven projects** may proceed regardless of financial ROI; COPQ is still useful for prioritization but is not the gating criterion.
- **Projects with non-monetizable benefits** (employee experience, cycle time where the output is not a direct revenue generator): supplement COPQ with a non-financial impact statement rather than forcing an implausible dollar estimate.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — frames the business case in the project charter
- [`./measure-the-baseline-before-you-change-anything.md`](./measure-the-baseline-before-you-change-anything.md) — the baseline data COPQ is calculated from

## Provenance

Cost-of-Quality model from ASQ (Juran, "Quality Control Handbook"). COPQ framing in DMAIC context from iSixSigma and Pyzdek & Keller, "The Six Sigma Handbook." _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
