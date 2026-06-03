---
name: control-plan-and-sustain
description: "Lock the gain after an improvement: build the control plan, design SPC monitoring, write standard work, add poka-yoke (mistake-proofing), define the reaction plan, and hand off to the process owner. A fix without a control plan didn't happen."
---

# Skill: control-plan-and-sustain

> **Invoked by:** `process-improvement/lean-six-sigma-blackbelt` (primary — owns the Control phase and the final tollgate). Also consulted by `process-analyst` when designing monitoring data-collection plans.
>
> **When to invoke:** DMAIC Control phase, after the Improve-phase pilot has confirmed the gain; any time an improvement is implemented without a monitoring plan; post-incident fixes that keep recurring (a sign the original fix lacked a control plan).
>
> **Output:** a completed `control-plan.md` covering every improved CTQ; a SPC monitoring setup (chart type, sampling plan, UCL/LCL); standard work for the new process; at least one poka-yoke per high-severity failure mode; a reaction plan; a named Process Owner who accepts the handoff.

## The discipline in one sentence

An improvement that is not maintained by a control system is only a temporary deviation from the old process.

Regression is not a sign of failure — it is the default outcome when process gains are not locked. Without a control plan, the team trains new hires on the old way, managers revert under pressure, and the process slides back within 6–18 months. The control plan is what makes "we improved this" a permanent statement.

## The four layers of control (in order of preference)

| Layer | What it is | Durability | Examples |
|---|---|---|---|
| **1. Eliminate the defect opportunity (poka-yoke)** | Design the defect out — make the wrong thing impossible or immediately obvious | Highest | Required field in form prevents missing data; automated check rejects non-conforming input; two-step confirmation prevents accidental deletion |
| **2. Standard work** | Documented procedure that makes the improved method the default, easiest way | High | Step-by-step SOP pinned in the workflow tool; checklist in the ticketing system; automated template with correct routing |
| **3. SPC / control chart** | Statistical monitoring detects when the process drifts — triggers investigation before defects accumulate | Medium | I-MR chart on daily cycle time; p chart on rework rate; automated dashboard alert on UCL breach |
| **4. Periodic audit** | Scheduled check that the process is being followed and the gain is holding | Lower | Monthly sampling audit; quarterly control-plan review; management walkthrough |

Prioritize elimination (poka-yoke) over detection (SPC + audit). The goal is a process that cannot fail in the old way, not a process that fails the old way and is quickly detected.

## Step-by-step

### Step 1 — Complete the control plan table

Use the `control-plan.md` template. One row per CTQ that was improved.

For each CTQ, specify:

| Column | What to fill in |
|---|---|
| **Process step** | The step in the improved process where this CTQ is produced |
| **CTQ** | The metric, with its operational definition (how exactly it is measured) |
| **Specification / target** | The customer requirement or improvement target (from the charter goal statement) |
| **Measurement method** | How and where the CTQ is measured — system, field, formula |
| **Sample size / frequency** | How many and how often — drives the SPC sampling plan |
| **Control chart type** | Selected from the decision tree in `process-capability-and-spc` skill |
| **Reaction plan** | What to do when a control-chart signal fires — decision tree, escalation path, rollback option |
| **Owner** | Named person responsible for monitoring this CTQ and executing the reaction plan |

**Every row needs a named owner.** A control plan with "team" or "TBD" as owner has no owner. The Process Owner signs the control plan.

### Step 2 — Set up SPC monitoring

From the control chart type selected in the Improve phase:

1. **Calculate new control limits** from the post-improvement baseline (if the improvement changed the process mean or variation, the old control limits are wrong — recalculate from ≥ 20 post-improvement data points).
2. **State the ruleset** — Western Electric Rules 1–4 are the standard default; add Nelson rules if the process is known to trend or cycle.
3. **Define the sampling plan** — who collects the data, from what source, on what cadence, and who plots the chart.
4. **Wire the alert** — an unmonitored control chart is decoration. Define who receives the signal (email, dashboard, Slack) and within what timeframe they must act.

If the measurement data doesn't exist yet (the process isn't instrumented), flag it: route to `data-platform` for the ELT + tracking pipeline.

### Step 3 — Write standard work

Standard work is the documented, current best-known method for the improved process step. It is not a procedure manual — it is the shortest, most useful guide that prevents regression.

Elements of useful standard work:

| Element | Description |
|---|---|
| **Step sequence** | The steps in order — numbered, with verbs |
| **Time standard** | Expected time per step (used for takt alignment) |
| **Quality check** | What the step output looks like when done correctly |
| **Common errors** | The one or two mistakes that happen and how to recognize them |
| **Location** | Where the standard work lives (pinned in the workflow tool, printed at the workstation, linked in the ticket template) |

Standard work must be **at the point of use** — where the worker performs the step. A procedure manual in a shared drive that no one opens is not standard work.

### Step 4 — Design poka-yoke (mistake-proofing)

For each failure mode in the FMEA (if one was built) or each NVA/rework loop in the process map, ask:

> "Can the defect be made impossible, or detected immediately at the source, rather than downstream?"

**Poka-yoke levels (in order of preference):**

| Level | Description | Example |
|---|---|---|
| **Prevention** | Makes the defect impossible to produce | Required field in form; system rejects invalid input at entry |
| **Detection — immediate** | Detects the defect at the step where it is made | Auto-check on save; visual indicator that step is incomplete |
| **Detection — downstream** | Detects the defect before it reaches the customer | Automated test in deployment pipeline; pre-send checklist in billing system |

Avoid designing poka-yokes that annoy the user into bypassing them (checkbox fatigue, pop-up blindness). The best poka-yoke is invisible — it just doesn't let the wrong thing happen.

### Step 5 — Define the reaction plan

A control chart signal without a reaction plan is an alarm with no instructions. For each CTQ in the control plan:

1. **Signal definition** — which rule(s) trigger a reaction (be specific — "1 point outside UCL" is specific; "process looks bad" is not)
2. **Immediate response** — stop-the-line? Continue and investigate? Who is notified within what timeframe?
3. **Investigation checklist** — the first 3–5 questions to ask when the signal fires (the cause candidates from the fishbone, ordered by frequency)
4. **Escalation path** — if first responder cannot resolve within X hours, who is next?
5. **Rollback / containment** — if the process has degraded, what is the containment action to protect the customer while the root cause is addressed?

The reaction plan is a decision tree, not a narrative. If it takes more than 1 minute to find the right action, it won't be used under pressure.

### Step 6 — Conduct the final tollgate and Process Owner handoff

The Control-phase tollgate answers:

| Question | Required evidence |
|---|---|
| Is the gain real and sustained? | Post-improvement control chart showing stable process at the new level (≥ 20 data points after the change) |
| Is the gain meaningful? | Before/after comparison in the charter's metric; sigma/capability improvement quantified |
| Is the process capable? | Cpk / Ppk calculated post-improvement; capability verdict stated |
| Is the control plan complete? | All CTQs covered; all rows have owners; reaction plans written |
| Is standard work in place? | SOP/checklist accessible at point of use |
| Is the Process Owner ready? | Named individual has reviewed the control plan and signed off |
| Is the financial benefit validated? | Finance representative has confirmed the savings claim (if financial benefit was in the charter) |

**The Process Owner's signature on the control plan is the handoff.** Without it, the improvement team is still on the hook for the process. The goal is a clean transfer.

## Control plan checklist

- [ ] Control plan table complete — one row per improved CTQ, all columns filled
- [ ] Every row has a named owner (not "team" or "TBD")
- [ ] Control chart control limits recalculated from post-improvement data (≥ 20 points)
- [ ] SPC alert wired to a real person/channel with a response timeframe
- [ ] Standard work written and placed at point of use
- [ ] At least one poka-yoke per high-RPN failure mode (from FMEA, if built)
- [ ] Reaction plan is a decision tree, not a narrative
- [ ] Rollback / containment action defined
- [ ] Post-improvement capability (Cpk/Ppk) calculated
- [ ] Before/after comparison in charter metric documented
- [ ] Financial benefit validated by Finance (if savings were claimed)
- [ ] Process Owner named, trained, and has signed the control plan
- [ ] Control phase tollgate completed with sponsor

## Anti-patterns this skill flags

- **Closing the project without a signed control plan** — "we'll document it later" is how gains revert
- **Control chart with no reaction plan** — the alarm rings and no one knows what to do
- **Control limits not recalculated after the improvement** — the old limits detect variation against the wrong baseline
- **Standard work stored somewhere no one looks** — SharePoint folder, email attachment; it must be at the point of use
- **Process Owner not named until the last week** — the Process Owner should be engaged from the charter; Control phase is the transfer, not the introduction
- **Financial benefit claimed without Finance validation** — the sponsor will be asked; if Finance doesn't agree, the benefit is disputed
- **Reaction plan that says "investigate"** — "investigate" is not actionable; the plan must say what to investigate, in what order, with what expected outcome
- **Poka-yoke that users learn to bypass** — a confirmation dialog clicked through in < 1 second is a motion waste, not a control

## See also

- Template: [`../../templates/control-plan.md`](../../templates/control-plan.md) — the artifact this skill populates
- Template: [`../../templates/fmea.md`](../../templates/fmea.md) — the RPN scores that prioritize which failure modes need poka-yoke
- Skill: [`../process-capability-and-spc/SKILL.md`](../process-capability-and-spc/SKILL.md) — control chart type selection + post-improvement Cpk/Ppk
- Skill: [`../dmaic-project-charter/SKILL.md`](../dmaic-project-charter/SKILL.md) — the charter goal statement that the control plan must show was achieved
- Best-practice: [`../../best-practices/a-fix-without-a-control-plan-didnt-happen.md`](../../best-practices/a-fix-without-a-control-plan-didnt-happen.md)
- Best-practice: [`../../best-practices/separate-common-cause-from-special-cause.md`](../../best-practices/separate-common-cause-from-special-cause.md)

---

_Last reviewed: 2026-06-03 by `claude`_
