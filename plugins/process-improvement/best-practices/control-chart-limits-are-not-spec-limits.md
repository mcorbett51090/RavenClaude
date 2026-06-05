# Control-chart limits are not specification limits

**Status:** Absolute rule
**Domain:** Process improvement — SPC / Control phase
**Applies to:** `process-improvement`

---

## Why this exists

Plotting specification limits (customer tolerances) on a control chart, or using spec limits to compute control limits, is one of the most common SPC errors in practice. It mixes two distinct questions: "Is the process stable?" (answered by ±3σ control limits derived from the *process data*) and "Does the process meet the customer's requirement?" (answered by capability indices Cpk/Ppk vs the spec). When teams draw the spec limits on the chart, they react to common-cause variation they cannot reduce with process-adjustment (tampering), and they ignore genuine special causes that fall inside the spec but outside the control limits. Both reactions increase variation.

## How to apply

**Control limits** are computed from the data:
- For an I-MR chart: `UCL = X̄ + 3(MR̄/1.128)`, `LCL = X̄ − 3(MR̄/1.128)`
- For Xbar-R: `UCL = X̄ + A₂R̄`, `LCL = X̄ − A₂R̄` (A₂ from control-chart constants table, indexed by subgroup size)
- All constants from the standard SPC table — **never hand-roll**; route any calculation to `applied-statistics`.

```
Two charts, two questions:
  ┌─────────────────────────────────────────────┐
  │ CONTROL CHART (I-MR / Xbar-R / p / u …)    │
  │  UCL ─────────────────────────────────────  │ ← computed from data (±3σ)
  │  CL  - - - - - - - - - - - - - - - - - - -  │
  │  LCL ─────────────────────────────────────  │
  │  Question: Is the process stable?           │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │ CAPABILITY ANALYSIS (Cpk / Ppk)             │
  │  USL: customer's upper requirement           │
  │  LSL: customer's lower requirement           │
  │  Question: Does it meet spec?               │
  └─────────────────────────────────────────────┘
```

**Do:**
- Keep the two charts entirely separate — one for stability, one for capability.
- Use WE/Nelson rules (from the process data and ±3σ limits) to signal special causes on the control chart; cite the rule number in any reaction plan.
- Run capability analysis (Cpk/Ppk) only after the process is *in statistical control* (no WE/Nelson violations); capability on an unstable process is a meaningless number.

**Don't:**
- Draw LSL/USL lines on the control chart — this conflates the two questions.
- Adjust the process when a point falls between the control limit and the spec limit (that is tampering on a common-cause event).
- Ignore a WE/Nelson signal just because the out-of-control point is still inside the spec band.

## Edge cases / when the rule does NOT apply

- **Regulatory or quality-system contexts** (e.g., some FDA/GMP frameworks) sometimes require *both* lines on one chart for compliance reporting. In that case, clearly label each line type ("Control Limit (3σ)" vs "Specification Limit") and document in the control plan that reactions are driven by the control limits, not the spec limits.
- **Pre-control charts** (used in some manufacturing startup procedures) intentionally use fractions of the spec; they are not SPC control charts and this rule does not apply to them.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — runs capability and SPC analysis; responsible for never conflating these two limit types
- [`./separate-common-cause-from-special-cause.md`](./separate-common-cause-from-special-cause.md) — companion rule: reacting to common cause variation (including by using spec limits as signals) is tampering

## Provenance

Codifies the "control before capability" sequence in the process-improvement decision tree (see [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md), "Is this process capable / in control?") and the anti-pattern in [`../CLAUDE.md`](../CLAUDE.md) §4 ("Confusing Cpk/Ppk and reporting one as the other"; "Reading an out-of-control signal by eyeball"). Standard SPC teaching: Montgomery *Introduction to Statistical Quality Control*; Wheeler & Chambers *Understanding Statistical Process Control*.

---

_Last reviewed: 2026-06-05 by `claude`_
