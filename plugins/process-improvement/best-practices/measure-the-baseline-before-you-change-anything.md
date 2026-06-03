# Measure the baseline before you change anything — no improvement claim without a quantified before-state

**Status:** Absolute rule — an improvement without a measured baseline is an untestable claim. The team may have worked hard; they cannot know whether the process improved.

**Domain:** DMAIC / process improvement

**Applies to:** `process-improvement`

---

## Why this exists

The most common failure in process improvement is not a bad solution — it is an unmeasured starting point. When a team skips the baseline and jumps to the fix, three things go wrong:

1. **The "improvement" cannot be validated.** Post-improvement data has nothing to compare against. "It feels better" is not a result.
2. **The team cannot learn.** Without a before/after comparison, the team cannot distinguish between a good countermeasure and a lucky quarter.
3. **The organization cannot decide.** A sponsor who hears "we fixed it" without a number cannot justify the next project's resources, promote the approach, or replicate the result.

There is a subtler failure mode too: **changing the process while measuring the baseline corrupts both.** The baseline no longer represents the old process, and the post-improvement data is contaminated by the mid-stream change.

## How to apply

Before any change is made to the process:

1. **Write the operational definition** — exactly how the primary CTQ metric is measured. Unit, numerator, denominator, data source, time boundary, rounding convention. Two people given the same raw data must compute the same number.

2. **Collect the baseline data** — minimum sample size depends on the metric type:
   - Control chart baseline: ≥ 20 data points to calculate stable control limits
   - Capability study: ≥ 30 data points for a reliable Cpk estimate (route to `applied-statistics` for small-sample guidance)
   - Attribute data (defect rates): enough to estimate the defect rate at a useful precision (route to `applied-statistics` for sample size)

3. **Confirm stability first** — plot the baseline on a control chart. If special-cause signals exist, find and eliminate them before declaring a baseline. A Cpk on an unstable process is a moving target, not a baseline.

4. **Document the baseline in the charter** — state the value, unit, sample size, time period, and data source. This is the "before" that the "after" will be compared against.

5. **Freeze the measurement definition** — the same operational definition used for the baseline must be used for the post-improvement measure. Changing the definition mid-project invalidates the comparison.

```
Baseline discipline — example:
  Metric: Customer ticket resolution time (P95)
  Operational definition: Elapsed calendar hours from ticket creation timestamp
                          to "Resolved" status timestamp in the ticketing system,
                          95th percentile across all P2/P3 tickets, excluding
                          tickets open > 30 days (counted as 30 days).
  Baseline: 38.4 hours (P95), n = 412 tickets, Jan–Mar 2026
  Data source: Zendesk API, field "created_at" to "solved_at"
  Target: ≤ 8 hours (P95) by end of project
```

**Do:**
- Collect baseline data before communicating the improvement timeline to stakeholders (avoids pressure to show results before the data is ready)
- Use the operational definition to audit the data source — confirm the system actually records what the definition says it does
- Treat "the data doesn't exist yet" as the first Measure-phase task, not a reason to skip the baseline

**Don't:**
- Use anecdotal evidence ("customers complain it's slow") as the baseline — it is the motivation, not the measurement
- Change the process "a little" while collecting the baseline — the baseline reflects only the old process
- Use a self-reported estimate from the process team as the baseline without cross-checking against system data

## Edge cases / when the rule has nuance

- **The data doesn't exist yet** — this is common and expected. The right response is to instrument the process (route to `data-platform` for the ELT + tracking infrastructure) and collect baseline data before improving. The wrong response is to proceed without one.
- **Emergency / safety situation** — if an immediate fix is needed to prevent harm, act. Then retroactively reconstruct the pre-fix state from available records. Even an imperfect retrospective baseline is better than none.
- **The process is new** — a newly designed process has no historical baseline. Set the initial control limits from the first 20–30 runs as the de facto baseline, then apply improvement against that.

## See also

- Skill: [`../skills/dmaic-project-charter/SKILL.md`](../skills/dmaic-project-charter/SKILL.md) — the charter's baseline section (§5) is where this rule is operationalized
- Skill: [`../skills/process-capability-and-spc/SKILL.md`](../skills/process-capability-and-spc/SKILL.md) — how to establish a stable baseline using a control chart
- Best-practice: [`./prove-root-cause-with-data-before-improving.md`](./prove-root-cause-with-data-before-improving.md) — the companion rule for the Analyze phase
- `applied-statistics/agents/applied-statistician.md` — sample size planning for the baseline measurement study

## Provenance

Distilled from `CLAUDE.md` §3 house opinion #1 ("Data before opinion — measure the current state before changing it") and §3 house opinion #7 ("Quantify the problem before and the gain after, in the same units"). The baseline-freeze requirement is standard DMAIC tollgate practice — the Measure-phase gate is not passed until the baseline is documented. `[unverified — training knowledge]` Six Sigma sample size recommendations above (≥ 20 for control charts, ≥ 30 for Cpk) — verify with `applied-statistics` for specific confidence levels.

---

_Last reviewed: 2026-06-03 by `claude`_
