---
description: "Triage a process with data: is it in statistical CONTROL first, and is it CAPABLE second? Reach for this when you have process readings + a spec/target and need the control-then-capability verdict before anyone reacts."
argument-hint: "[the situation — the process, the metric, the spec/target, and whatever data you have]"
---

# Triage capability and control

You are running `/process-improvement:triage-capability-and-control` for `$ARGUMENTS`. Run it the way the team's Black Belt would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3, and the **control-before-capability** rule above all (§3 #1; the §2 capability-on-an-unstable-process anti-pattern).

## Steps (traverse top-to-bottom; do not skip the order)

1. **Operationally define the metric.** Confirm the metric has a precise start/stop, inclusion rule, and data source — same input → same recorded value, any person. If it doesn't, STOP and write the operational definition first (an ambiguous metric makes every later number noise). See [`../best-practices/operational-definition-before-you-measure.md`](../best-practices/operational-definition-before-you-measure.md).
2. **Pick the control chart by data type.** Traverse the **which-control-chart** tree in [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md) (variable vs attribute; subgroup size; defects vs defectives). For individual readings, the `imr` mode of [`../scripts/lss_calc.py`](../scripts/lss_calc.py) computes the limits.
3. **Establish CONTROL first.** Check the series against a stated Western Electric / Nelson rule ([`../knowledge/six-sigma-statistics-and-spc.md`](../knowledge/six-sigma-statistics-and-spc.md) §4). If special-cause signals are present, the process is **unstable** — capability is meaningless; find and remove the special cause before going further. Do **not** react to common-cause noise (the anti-tampering gate in [`../knowledge/spc-response-decision-trees.md`](../knowledge/spc-response-decision-trees.md)).
4. **Then assess CAPABILITY.** Only on a stable process, compute Cp/Cpk/Pp/Ppk vs the spec (the `capability` mode of the calculator). Band the result (<1.0 / 1.0–1.33 / ≥1.33 / ≥1.67) and read the Cpk−Ppk gap for drift.
5. **If capability is low, diagnose WHICH problem.** Traverse the **capability-study-came-back-low** tree ([`../knowledge/spc-response-decision-trees.md`](../knowledge/spc-response-decision-trees.md)): centering (cheap setpoint move) vs spread (variation-reduction project) vs drift (control problem). Don't say "improve capability" generically.
6. **Route the inference, don't fake it.** A capability **confidence interval**, a Gage R&R, or "is this difference real?" routes to `applied-statistics` (CLAUDE.md §8). State the question in process terms and hand it across the seam; do not assert significance from a point estimate.

## Output

A control-then-capability verdict: the chosen chart + why, the stability finding (in control / out of control, with the rule that fired or didn't), and — only if stable — the capability indices with their bands and the specific improvement diagnosis (center / spread / drift). End with the §6 Output Contract block and the Structured Output Protocol JSON.

## Guardrails

- **Control before capability — always.** A Cpk on an out-of-control process is a meaningless number; never report one without the stability check + the spec limits + the sample window.
- Control limits are computed from the data (±3σ), **not** the spec limits — never draw spec lines on a control chart.
- State the **1.5σ-shift convention** on any sigma-level claim, and never substitute Cpk for Ppk (they answer different questions).
- The calculator is decision-support, not statistical certification — the inference seam (`applied-statistics`) owns CIs, Gage R&R, and significance.
- Cite a source + retrieval date for every external threshold/figure, or mark it `[unverified — training knowledge]`.
