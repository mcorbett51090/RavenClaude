# Separate common cause from special cause — reacting to noise as if it were signal makes processes worse

**Status:** Pattern — apply this framing before any reaction to process data. Tampering (reacting to common-cause variation) is one of the most prevalent and damaging process management mistakes.

**Domain:** Statistical Process Control / process monitoring

**Applies to:** `process-improvement`

---

## Why this exists

When a process metric moves — a batch is late, the defect count is up this week, the cycle-time average rose — managers and teams instinctively react. That instinct is right when the movement is a special cause (an assignable, unusual event). It is wrong — and actively harmful — when the movement is common-cause variation (the normal, random noise of an unchanged process).

**Tampering** is the name for reacting to common-cause variation as if it were special cause. W. Edwards Deming's funnel experiment demonstrates the result: each "correction" adds variation to the next observation, and repeated adjustments make the process steadily worse. In operational processes, tampering looks like:

- Adjusting a process setting every time a metric moves, without determining whether the move is a signal or noise
- Launching a root-cause investigation (and spending the team's time) on a week that was bad by random chance
- Blaming or praising individuals for results that are explained by common-cause variation in the system
- Changing a process that is in statistical control because "this week's numbers were high"

The opposite error is also costly: **missing a special cause** by treating an assignable event as noise. A real signal left uninvestigated persists and often worsens.

A control chart resolves the ambiguity.

## How to apply

### Step 1 — Establish control limits from the process data

Plot the metric on the appropriate control chart (see `process-capability-and-spc` skill for chart type selection). Control limits are calculated from the data as ±3σ around the process mean. Do not set them to specification limits or management targets.

### Step 2 — Apply the ruleset before reacting

Check the chart against the stated ruleset (Western Electric Rules 1–4 are the standard):

| Rule | Signal (special cause) | Reaction |
|---|---|---|
| 1 point outside ±3σ (Rule 1) | Unusual — investigate | Find the assignable cause; eliminate it; add to the reaction plan |
| 2 of 3 beyond ±2σ, same side (Rule 2) | Shift or trend beginning | Investigate; confirm whether a process change occurred |
| 4 of 5 beyond ±1σ, same side (Rule 3) | Drift | Investigate |
| 8 consecutive, same side (Rule 4) | Sustained shift | Investigate; likely a real change in the process level |
| No rule violated | Common cause | Do NOT adjust; redesign the process in the Improve phase if the level is unacceptable |

**State the ruleset before applying it.** "Out of control" is only meaningful against a specific set of rules. Calling a run of 7 "out of control" when Rule 4 requires 8 is incorrect.

### Step 3 — React appropriately by type

| Signal type | The right action | The wrong action |
|---|---|---|
| **Special cause confirmed** | Identify the assignable cause; eliminate it or prevent recurrence; update the control plan reaction plan | Ignore it; assume it will resolve itself; "investigate" without a structured checklist |
| **Common cause only** | If the process level is acceptable → monitor and maintain. If unacceptable → redesign the process (DMAIC Improve phase). | Adjust the process based on individual data points; launch a root-cause investigation on a random bad week; blame the person who did the work that period |

### Step 4 — Recalculate control limits after a confirmed improvement

If a process change genuinely shifts the mean or reduces variation (confirmed by ≥ 20 post-change points with no special-cause signals), recalculate the control limits from the new data. Carrying pre-improvement limits into the post-improvement monitoring period creates false signals.

```
Operational example — support ticket resolution time:
  Before improvement: P95 = 38 hrs, UCL = 61 hrs, LCL = 15 hrs
  Week 7 shows P95 = 54 hrs. Rule 1 check: 54 < UCL (61). Rule 4 check: not 8 in a row.
  Verdict: Common cause variation. No investigation warranted.
           If the 38-hr baseline is unacceptable, run a DMAIC to reduce it.
           Do NOT adjust the process based on this week's number.

  Week 11 shows P95 = 64 hrs. Rule 1: 64 > UCL (61). Special cause signal.
  Reaction plan: Check whether a staffing outage, system incident, or intake
                 spike occurred this week. Investigate within 24 hours.
```

## The policy implication

If a process is in statistical control (only common-cause variation), the level of that variation is a **system property**, not an individual's fault. Deming's point: the workers operate within the system; only management can change the system. Attributing a bad-week result to the person who worked that week — when the control chart shows it was random variation — erodes trust and does not improve the process.

## Edge cases / when the rule has nuance

- **Very tight spec limits** — if the customer's specification requires a process capability the common-cause variation cannot meet (Cpk < 1.0), the process must be redesigned. The control chart tells you it's stable; the capability index tells you it's not capable. Both can be true simultaneously.
- **Control chart just established (fewer than 20 points)** — control limits calculated from small samples are wide and unreliable. Treat signals with lower confidence; collect more data before declaring the limits stable.
- **The process is never in statistical control** — if the chart shows continuous special-cause signals, the process is fundamentally unstable. Eliminate the assignable causes one by one until the chart stabilizes; then assess capability.

## See also

- Skill: [`../skills/process-capability-and-spc/SKILL.md`](../skills/process-capability-and-spc/SKILL.md) — control chart selection, Western Electric/Nelson rules, how to read signals
- Skill: [`../skills/control-plan-and-sustain/SKILL.md`](../skills/control-plan-and-sustain/SKILL.md) — reaction plan design for the Control phase
- Best-practice: [`./a-fix-without-a-control-plan-didnt-happen.md`](./a-fix-without-a-control-plan-didnt-happen.md) — sustaining the gain after a genuine special-cause is eliminated
- Knowledge: [`../knowledge/six-sigma-statistics-and-spc.md`](../knowledge/six-sigma-statistics-and-spc.md) — the authoritative reference for control-chart rules and thresholds with retrieval dates

## Provenance

Distilled from `CLAUDE.md` §4 anti-pattern ("Reading an out-of-control signal off a chart by eyeball instead of against a stated Western Electric / Nelson rule") and the common-cause / special-cause distinction at the core of Statistical Process Control. Deming's funnel experiment (tamper-effect) is a foundational SPC illustration; the formal two-type-error framing (false alarm vs. missed signal) is standard control-chart theory. `[unverified — training knowledge]` Deming funnel experiment details — verify against Deming's *Out of the Crisis* or an SPC primary source if quoting to a client.

---

_Last reviewed: 2026-06-03 by `claude`_
