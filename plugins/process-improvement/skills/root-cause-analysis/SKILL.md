---
name: root-cause-analysis
description: "Drive to proven root cause using 5 Whys, fishbone/Ishikawa (6M categories), and Pareto (80/20 prioritization), then validate the suspected cause with data. Routes hypothesis testing to applied-statistics. Anti-pattern: solution-jumping before cause is proven."
---

# Skill: root-cause-analysis

> **Invoked by:** `process-improvement/lean-six-sigma-blackbelt` (primary — owns the Analyze phase verdict). Also used by `process-analyst` to structure a cause hypothesis set before the black belt validates.
>
> **When to invoke:** DMAIC Analyze phase, after the baseline is measured and the process is mapped; whenever a team proposes a solution and no one has proven what caused the problem; post-incident / post-defect retrospectives.
>
> **Output:** a fishbone diagram (Ishikawa) with 6M causes identified; a ranked Pareto of candidate causes; at least one root cause that has been confirmed with data (not just asserted); a go/no-go gate before the Improve phase begins.

## The cardinal rule: cause-first, solution-second

The most expensive mistake in process improvement is spending time and money on a solution to the wrong cause. The purpose of this skill is to prevent that.

Root cause is **proven** when:
1. A plausible mechanism connects the cause to the defect/variation.
2. Data shows the defect rate or cycle time changes systematically with the candidate cause.
3. When the cause is removed or controlled in a pilot, the problem improves.

Root cause is **not proven** by: group consensus, management assertion, gut feel, or a strong correlation without a mechanism.

## Step-by-step

### Step 1 — State the effect (the problem) precisely

Before listing causes, write the problem statement in one sentence with a number. Use the charter's problem statement.

Poor: "Hiring is broken."  
Better: "Time-to-fill open roles averages 67 days vs. a 30-day target, and 40% of offers are declined."

This sentence goes at the head of the fishbone and at the top of each Why in the 5 Whys chain.

### Step 2 — Build the fishbone (Ishikawa) diagram

The fishbone organizes candidate causes by the 6M categories. Use the `fishbone-and-5-whys.md` template.

| Category | Ask | Examples in varied operational contexts |
|---|---|---|
| **Machines / Technology** | What tools, systems, or equipment could cause this? | Ticketing system doesn't surface SLA breach warnings; deployment pipeline has no automated rollback |
| **Methods / Process** | What process steps, procedures, or work instructions contribute? | Approval workflow requires two sequential sign-offs with no parallel path; onboarding checklist is optional |
| **Materials / Information** | What inputs, data, or reference material are defective or missing? | Hiring requisition arrives without a salary band; claims arrive without supporting documentation |
| **Measurement** | Could the problem be a measurement artifact rather than a real defect? | Cycle-time clock starts at form submission, not at request — understates true wait; SLA resets on reassignment |
| **Man/People** | What training, staffing, awareness, or incentive issues could cause this? | Billing team rotates monthly — no one owns an invoice end-to-end; support agents aren't trained on tier-2 escalation criteria |
| **Mother Nature / Environment** | What external, seasonal, or environmental factors contribute? | Deployment failures spike on Fridays before release freeze; onboarding delays are worst in December (holiday overlap) |

**Rules for a good fishbone:**

- Each bone is a *cause*, not a *solution* or a *complaint* ("no budget" is a constraint — state what it causes: "understaffed review team → queues grow").
- Add sub-bones for causal chains (the cause of the cause).
- Write down every candidate — you are not yet judging. Premature pruning misses the real cause.
- Get input from the people doing the work, not just management. The frontline worker sees causes management is unaware of.

### Step 3 — Run the 5 Whys (for each strong candidate)

The 5 Whys is a vertical drill on a single candidate cause. For each candidate from the fishbone that looks plausible:

1. State the effect.
2. Ask "Why does this occur?" → state the first-level cause.
3. Ask "Why does *that* occur?" → second-level cause.
4. Repeat until you reach a root that is (a) actionable and (b) not just "because we didn't try hard enough."

Stop when:
- The cause is actionable (a person/team can change it).
- Removing it would prevent recurrence (not just the latest instance).
- You've gone deep enough that the next Why points to a system or process, not a person's error.

| Why | Answer |
|---|---|
| 1. Why is time-to-fill 67 days? | Offers take 3+ weeks to issue after the final interview |
| 2. Why does offer issuance take 3 weeks? | Comp band approval requires VP sign-off and averages 16 days |
| 3. Why does VP approval average 16 days? | Requests queue behind other VP work; no SLA exists for comp approvals |
| 4. Why is there no SLA? | No one owns the process from requisition to offer; Recruiting and HR are separate approval chains |
| 5. Why are they separate chains? | Org design — Recruiting reports to Ops, HR to Legal; comp approvals are routed through HR only |

**Root cause:** no single process owner from requisition to offer; two-chain approval with no SLA.

### Step 4 — Build a Pareto chart (prioritize with 80/20)

Not all candidate causes contribute equally. If defect data is stratified by cause, build a Pareto:

1. Count defects (or defect cost, or delay time) attributable to each cause category.
2. Sort descending.
3. Plot as a bar chart with a cumulative % line.
4. The bar(s) to the left of the 80% cumulative line are the vital few causes.

**Pareto example — support ticket escalations by cause:**

| Cause | Count | Cumulative % |
|---|---|---|
| Missing customer context in ticket | 41 | 41% |
| Agent not trained on product category | 28 | 69% |
| Escalation routing misconfigured | 17 | 86% |
| Customer unreachable for follow-up | 9 | 95% |
| Other | 5 | 100% |

The top two causes account for 69% of escalations — they are the Analyze-phase focus.

### Step 5 — Validate the root cause with data

**This step is non-negotiable.** A cause identified from a fishbone and 5 Whys is a hypothesis, not a root cause. Validation requires data.

Validation approaches (in order of rigor):

| Approach | When to use | Who runs it |
|---|---|---|
| **Stratified comparison** — compare defect rate when the suspected cause is present vs. absent | Categorical cause (trained vs. not trained) | `process-analyst` or `lean-six-sigma-blackbelt` |
| **Scatter plot / correlation** — plot the suspected cause measure against the output measure | Continuous cause (queue depth vs. cycle time) | `process-analyst` (visualization); route inference to `applied-statistics` |
| **Hypothesis test** — t-test, ANOVA, chi-square — formally test whether the difference is real | Any confirmation beyond descriptive | **Route to `applied-statistics`** — name the question, let the statistician run and defend it |
| **DOE (design of experiments)** — vary multiple causes simultaneously to quantify main effects and interactions | Multiple candidate causes interacting | **Route to `applied-statistics`** — this is not in scope for this plugin |
| **Pilot / controlled change** — change only the suspected cause and observe the effect | When observational data is ambiguous | `lean-six-sigma-blackbelt` owns the pilot design; route the statistical test to `applied-statistics` |

**The seam:** this skill names the validation question and the candidate test; `applied-statistics`'s `applied-statistician` runs, assumption-checks, and defends it.

### Step 6 — Gate: is root cause proven?

Before the Analyze phase closes, the gate question is:

> "Do we have data showing the process output changes predictably when this cause is present vs. absent, and is the change large enough to explain the observed problem?"

- **Yes** → proceed to Improve phase.
- **No** → return to Step 3/4 with additional data collection or a different candidate cause.

A "we're pretty sure" or a "the team agrees" does not pass the gate. See best-practice: `prove-root-cause-with-data-before-improving.md`.

## RCA checklist before the Analyze gate

- [ ] Problem statement is quantified (number confirms the problem exists)
- [ ] Fishbone populated across all 6M categories with input from frontline workers
- [ ] 5 Whys run to a system/process-level root for at least the top two candidate causes
- [ ] Pareto built if defect-cause data is available (or sample data collected)
- [ ] Vital-few causes identified (the ~20% causing ~80% of the effect)
- [ ] At least one root cause validated with data (not just assertion)
- [ ] Hypothesis test routed to `applied-statistics` if statistical validation was required
- [ ] Gate question answered: root cause proven, not just hypothesized
- [ ] FMEA (`fmea.md`) completed if failure mode severity warrants it

## Anti-patterns this skill flags

- **Jumping to "we need a new system"** — the fishbone wasn't finished; technology is one of 6M causes, not the default answer
- **Fishbone filled out only by management** — the frontline worker's view is missing; the real cause lives in the methods/man/machines they see
- **5 Whys stopping at "human error"** — this is never the root cause; it is always the penultimate Why. Ask: why did the system allow the human error to occur?
- **Pareto skipped because "we know the cause"** — assumptions about cause distribution are usually wrong; the data surprises
- **Calling correlation "proof"** — a scatter plot that looks correlated is a hypothesis; the hypothesis test (in `applied-statistics`) is the proof
- **Proceeding to Improve after a failed validation** — the gate exists precisely for this; a failed validation means the real cause hasn't been found yet
- **FMEA skipped for high-severity processes** — a billing system, a drug dispensing process, or a deployment pipeline with production impact warrants an FMEA before solution design

## See also

- Skill: [`../process-mapping/SKILL.md`](../process-mapping/SKILL.md) — Measure phase map that feeds this Analyze phase
- Skill: [`../process-capability-and-spc/SKILL.md`](../process-capability-and-spc/SKILL.md) — confirms whether the baseline is a stable process or already has special-cause variation
- Template: [`../../templates/fishbone-and-5-whys.md`](../../templates/fishbone-and-5-whys.md) — artifact for Steps 2–3
- Template: [`../../templates/fmea.md`](../../templates/fmea.md) — risk-priority scoring for high-severity processes
- Best-practice: [`../../best-practices/prove-root-cause-with-data-before-improving.md`](../../best-practices/prove-root-cause-with-data-before-improving.md)
- Best-practice: [`../../best-practices/separate-common-cause-from-special-cause.md`](../../best-practices/separate-common-cause-from-special-cause.md)
- `applied-statistics/agents/applied-statistician.md` — the seam for all inferential validation (hypothesis tests, DOE, regression)
- `applied-statistics/skills/statistical-qa-of-metrics/SKILL.md` — validates metric definitions before root-cause data is collected

---

_Last reviewed: 2026-06-03 by `claude`_
