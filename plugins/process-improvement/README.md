# process-improvement

> The **Lean Six Sigma Black Belt** for Claude Code — analyzes a team's operational processes and improves them with the rigor of a certified Black Belt: DMAIC, Lean waste removal, data-proven root-cause analysis, statistical process control, and control plans that make the gain stick.

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

**Domain-neutral by design.** Process improvement applies to *any* repeatable operational process — support-ticket resolution, employee onboarding, invoice/billing, deployment/release, hiring, claims, fulfillment. No vertical assumptions are baked in.

## What it does

| You ask | It returns |
|---|---|
| "Our onboarding takes too long and varies wildly — run a DMAIC" | A phased Define→Measure→Analyze→Improve→Control plan, the right tool per phase, and a quantitative baseline before anything changes |
| "Baseline this process's sigma level / capability" | A defect/CTQ definition + spec limits, a DPMO + sigma-level baseline (with the 1.5σ-shift convention stated), and Cp/Cpk/Pp/Ppk vs thresholds — after confirming the process is in control |
| "Map how this process actually works today" | A SIPOC + swimlane / value-stream map with value-add vs non-value-add tagged and the hidden queues/handoffs made visible |
| "Where is the waste in this workflow?" | An 8-wastes (DOWNTIME) walk + a Pareto of the biggest contributors |
| "This fix worked in a pilot — how do we sustain it?" | A control plan: the right SPC chart + out-of-control rules, standard work, a response plan, and a single named owner |

**Three rules it never breaks:** *measure the current state before you change it*, *prove root cause with data before designing the fix*, and *a control plan or it didn't happen.*

## What's inside

- **2 agents**
  - [`lean-six-sigma-blackbelt`](agents/lean-six-sigma-blackbelt.md) — the centerpiece. Runs the full DMAIC arc, frames the problem quantitatively, proves root cause, designs the fix, locks the gain.
  - [`process-analyst`](agents/process-analyst.md) — the green-belt analyst who maps and measures the current state (SIPOC, value-stream maps, data-collection plans, waste/Pareto) and feeds the Black Belt.
- **6 skills** — `dmaic-project-charter`, `process-mapping`, `root-cause-analysis`, `process-capability-and-spc`, `lean-waste-analysis`, `control-plan-and-sustain`.
- **3 knowledge files** —
  - [`dmaic-and-lean-toolkit.md`](knowledge/dmaic-and-lean-toolkit.md) — DMAIC phase-by-phase + the canonical tool per phase; DMAIC vs DMADV vs Kaizen/PDCA; the Lean overlay (8 wastes / DOWNTIME, value-add vs non-value-add).
  - [`six-sigma-statistics-and-spc.md`](knowledge/six-sigma-statistics-and-spc.md) — sigma↔DPMO↔yield (1.5σ shift), Cp/Cpk/Pp/Ppk + thresholds, control-chart selection + Western Electric / Nelson rules, MSA / Gage R&R, and the explicit map of what routes to `applied-statistics`.
  - [`process-improvement-decision-trees.md`](knowledge/process-improvement-decision-trees.md) — Mermaid trees: which methodology, which control chart, which root-cause tool, capable-vs-in-control triage.

## When to use it

- A process is **too slow, too inconsistent, or too error-prone** and you want it fixed *measurably*, not just reorganized.
- You need a **defensible baseline** (sigma level / DPMO / capability) before-and-after, so the gain is provable.
- A fix landed in a pilot and you need it to **stick** (control plan, SPC, standard work).
- You suspect **waste** (handoffs, rework, waiting, re-keying) and want it found and ranked.

Reach for `applied-statistics` instead when the question is purely "which statistical test / how big a sample / is this difference real?" with no process-improvement framing — and for `project-management` when you need the *project* wrapper (schedule, RAID, status) rather than the DMAIC content.

## How it seams with `applied-statistics`

```
process-improvement  →  WHICH metric, WHICH chart, WHICH tool, what a Cpk of 1.1 MEANS for this process
applied-statistics   →  "is the difference REAL?"  (the hypothesis test, DOE, regression, sample size, capability inference)
```

This plugin owns the **process framing and the method choice**; it does **not** re-derive the inferential math. The Black Belt routes Analyze-phase hypothesis tests, Improve-phase pilot analysis, DOE, and formal capability inference to [`applied-statistics/applied-statistician`](../applied-statistics/agents/applied-statistician.md) — invoking its `choose-statistical-test`, `experiment-analysis`, `power-and-sample-size`, and `statistical-qa-of-metrics` skills. It also seams to `project-management` (the DMAIC project wrapper / RAID) and `data-platform` (instrumenting a process so it can be measured + monitored).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install process-improvement@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
