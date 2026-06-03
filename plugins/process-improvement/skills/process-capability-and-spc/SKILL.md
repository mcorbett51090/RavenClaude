---
name: process-capability-and-spc
description: "Baseline a process: compute DPMO/sigma level and Cp/Cpk, select and read the right control chart (I-MR / Xbar-R / p / c / u), and apply Western Electric/Nelson rules to separate common-cause from special-cause variation. Routes deeper capability inference and hypothesis testing to applied-statistics."
---

# Skill: process-capability-and-spc

> **Invoked by:** `process-improvement/lean-six-sigma-blackbelt` (primary — owns the baseline verdict and control-phase monitoring design). Also used by `process-analyst` for data-collection planning and initial control-chart selection.
>
> **When to invoke:** DMAIC Measure phase (establishing the baseline); Control phase (setting up ongoing monitoring); any time someone asks "how capable is this process?" or "is this process stable?"; before and after an Improve-phase change to quantify the gain.
>
> **Output:** a stated sigma level / DPMO / yield (with the 1.5σ-shift convention explicitly noted); Cp/Cpk (or Pp/Ppk for long-term) with a capability verdict; a control chart type selected from the decision tree; out-of-control signals identified against stated Western Electric / Nelson rules; a clear separation of common-cause from special-cause.

## The two questions this skill answers

1. **Is the process stable?** (Control chart — separates common-cause from special-cause variation)
2. **Is the stable process capable?** (Capability indices — compares variation to the customer specification)

Answer #1 before #2. Capability on an unstable process is meaningless — the indices will change as special causes come and go.

## Part 1 — DPMO, Sigma Level, and Yield

### Operational definitions (required before any count)

Before counting defects, define:

- **Unit** — the entity being produced (one invoice, one support ticket, one hire, one deployment)
- **Defect** — any output that fails a customer CTQ (not an internal preference)
- **Opportunity** — the number of ways a single unit can fail (be specific; inflating opportunities inflates sigma artificially)

### DPMO and sigma level

**DPMO (Defects Per Million Opportunities):**

```
DPMO = (number of defects / (units × opportunities per unit)) × 1,000,000
```

Example — claims processing: 47 defects in 800 claims, each with 3 CTQ opportunities:
```
DPMO = (47 / (800 × 3)) × 1,000,000 = 19,583
```

**Sigma level** from DPMO (long-term, with the 1.5σ shift baked in — the industry-standard convention):

| Long-term sigma | DPMO | Yield |
|---|---|---|
| 2σ | 308,537 | 69.1% |
| 3σ | 66,807 | 93.3% |
| 4σ | 6,210 | 99.4% |
| 5σ | 233 | 99.977% |
| 6σ | 3.4 | 99.9997% |

**Always state the convention.** "This process is at 3.7 sigma (long-term, with 1.5σ shift)." Never quote a sigma level without stating which convention. The 1.5σ shift is an industry assumption about long-term process drift, not a mathematical derivation; omitting it creates confusion when comparing across sources.

For deeper capability inference (confidence intervals on sigma, capability with small samples) — route to `applied-statistics`.

### Part 2 — Cp, Cpk, Pp, Ppk

Use these indices only for **continuous, measurable** CTQs (cycle time in hours, error rate, invoice amount variance), not for defect counts.

| Index | What it measures | When to use |
|---|---|---|
| **Cp** | Process spread vs. spec width (centering ignored) | Short-term potential; subgroup data |
| **Cpk** | Process spread vs. spec, with centering penalty | Short-term actual; most common single-number summary |
| **Pp** | Long-term spread vs. spec width | Overall, all sources of variation |
| **Ppk** | Long-term spread vs. spec, with centering | Long-term actual; use when reporting to customers |

**Formulas:**
```
Cp  = (USL - LSL) / (6 × σ_within)
Cpk = min[(USL - x̄) / (3 × σ_within),  (x̄ - LSL) / (3 × σ_within)]
```
(Pp / Ppk: same formula but σ_overall replaces σ_within)

**Capability thresholds:**

| Cpk value | Verdict |
|---|---|
| < 1.00 | Incapable — the process is producing defects against the spec |
| 1.00–1.33 | Marginally capable — meets spec when centered; little room for drift |
| 1.33–1.67 | Capable — industry standard for established processes |
| ≥ 1.67 | Highly capable — Six Sigma target (Cpk ≥ 1.50 short-term → 6σ long-term) |

**Confusing Cpk and Ppk is an anti-pattern.** Cpk uses within-subgroup variation (σ_within); it overestimates long-term performance if between-subgroup variation is significant. Report both when available; explain which is which.

For capability confidence intervals, sample-size planning for a capability study, and Gage R&R analysis (measurement system validation before calculating capability) — route to `applied-statistics`.

## Part 3 — Control chart selection

Use this decision tree before drawing a chart:

```
Is the data continuous (measured) or attribute (counted)?
├── Continuous
│   ├── Individual measurements (subgroup size = 1, e.g., daily cycle time)
│   │   └── I-MR chart (Individuals + Moving Range)
│   └── Subgroups (multiple measurements per time period)
│       ├── Subgroup size 2–8  →  Xbar-R chart
│       └── Subgroup size ≥ 9  →  Xbar-S chart
└── Attribute (defects / defectives)
    ├── Tracking defectives (pass/fail units)?
    │   ├── Constant subgroup size  →  p chart (proportion defective)
    │   └── Varying subgroup size   →  p chart (also handles variable n)
    │       OR np chart (fixed n only, counts defectives not proportion)
    └── Tracking defects (multiple defects per unit)?
        ├── Constant area of opportunity  →  c chart (count of defects)
        └── Varying area of opportunity   →  u chart (defects per unit)
```

**Most common choices for office/operational processes:**
- **I-MR** — single daily/weekly measurement (cycle time per order, claims per day, deployment failures per week)
- **p chart** — proportion defective with varying batch sizes (proportion of tickets re-opened, proportion of invoices requiring rework)
- **c chart** — count of defects per unit with fixed opportunity (errors per audit report)

### Reading a control chart

Every control chart has:
- **Center line (CL)** — the process average
- **Upper Control Limit (UCL)** and **Lower Control Limit (LCL)** — ±3σ from the center line, calculated from the data

**Control limits are not specification limits.** Control limits describe what the process actually does. Specification limits describe what the customer needs. Do not draw spec limits on a control chart and call a point "out of control" because it missed the spec.

## Part 4 — Western Electric / Nelson rules

Apply these rules to detect special-cause signals. State which ruleset you are using before applying it.

**Western Electric Rules (the standard four):**

| Rule | Signal |
|---|---|
| **Rule 1** | 1 point beyond ±3σ (outside UCL or LCL) |
| **Rule 2** | 2 of 3 consecutive points beyond ±2σ (same side) |
| **Rule 3** | 4 of 5 consecutive points beyond ±1σ (same side) |
| **Rule 4** | 8 consecutive points on the same side of the center line |

**Nelson Rules add:**

| Rule | Signal |
|---|---|
| **Rule 5** | 6 consecutive points trending steadily up or down |
| **Rule 6** | 14 consecutive points alternating up/down |
| **Rule 7** | 15 consecutive points within ±1σ (hugging the center) |
| **Rule 8** | 8 consecutive points beyond ±1σ (both sides, none within ±1σ) |

**Using multiple rules increases false-alarm rate.** For a baseline study, Rules 1–4 are sufficient. Apply additional rules only when the process is known to exhibit specific patterns (trending, cycling).

### Interpreting signals

| Signal type | Meaning | Action |
|---|---|---|
| **Common cause** — all points within control limits, no rule violations | Natural variation inherent to the current process design | Investigate and redesign the process (Improve phase); reacting to individual points is tampering |
| **Special cause** — any rule violation | An assignable cause entered or left the process | Identify and eliminate the special cause; do not calculate capability until the process is stable |

See best-practice: `separate-common-cause-from-special-cause.md` — reacting to common-cause variation as if it were special cause (tampering) increases process variation.

## Capability study checklist

- [ ] Unit, defect, and opportunity operationally defined before counting
- [ ] Measurement system validated (Gage R&R or equivalent) before collecting capability data — route to `applied-statistics` if formal MSA is needed
- [ ] Process stability confirmed first — control chart shows no special-cause signals
- [ ] Correct chart type selected from the decision tree (not assumed)
- [ ] Western Electric / Nelson ruleset stated explicitly
- [ ] Sigma level quoted with convention (long-term with 1.5σ shift, or short-term — state which)
- [ ] Cpk and Ppk both calculated and labeled correctly (short-term vs. long-term)
- [ ] Capability verdict stated against the threshold table
- [ ] Post-Improve remeasure planned: same metric, same definition, comparable sample size

## Anti-patterns this skill flags

- **Calculating Cpk before confirming stability** — an out-of-control process yields a misleading Cpk
- **Using control limits as specification limits** — these are different things with different purposes
- **Quoting sigma level without stating the 1.5σ-shift convention** — creates apples-to-oranges comparisons
- **Confusing Cpk (short-term) with Ppk (long-term)** — inflates reported capability
- **Drawing a control chart without stating the ruleset** — any one point outside 3σ might be Rule 1; calling a run of 7 "out of control" when Rule 4 requires 8 is wrong
- **Reacting to a single point** without confirming it is a special-cause signal — the most common form of tampering
- **Inflating the number of opportunities per unit** to inflate the sigma level — sigma is only comparable across processes when opportunities are defined consistently
- **Skipping MSA** — calculating Cpk with a measurement system that contributes > 10% of process variance inflates variation and understates capability

## See also

- Skill: [`../root-cause-analysis/SKILL.md`](../root-cause-analysis/SKILL.md) — uses the control chart to establish whether the baseline is stable before root-cause analysis
- Skill: [`../control-plan-and-sustain/SKILL.md`](../control-plan-and-sustain/SKILL.md) — uses the control chart type and UCL/LCL in the Control phase
- Best-practice: [`../../best-practices/measure-the-baseline-before-you-change-anything.md`](../../best-practices/measure-the-baseline-before-you-change-anything.md)
- Best-practice: [`../../best-practices/separate-common-cause-from-special-cause.md`](../../best-practices/separate-common-cause-from-special-cause.md)
- `applied-statistics/agents/applied-statistician.md` — Gage R&R / MSA, capability CIs, sample-size planning, hypothesis tests for pre/post comparison
- `applied-statistics/skills/statistical-qa-of-metrics/SKILL.md` — validates metric definitions and measurement reliability before the capability study begins
- Knowledge: [`../../knowledge/six-sigma-statistics-and-spc.md`](../../knowledge/six-sigma-statistics-and-spc.md) — the sigma↔DPMO table, control-chart rules, and Cp/Cpk thresholds with retrieval dates

---

_Last reviewed: 2026-06-03 by `claude`_
