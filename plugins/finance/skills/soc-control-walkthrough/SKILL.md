---
name: soc-control-walkthrough
description: Document a SOC 1 / SOC 2 control walkthrough — control description, test of design vs test of operating effectiveness, evidence-of-control patterns, sampling, exception triage, deficiency severity classification (control deficiency / significant deficiency / material weakness). Reach for this skill during pre-audit prep, when documenting a new control for the next SOC cycle, or when responding to an auditor's walkthrough request. Used by `audit-prep-specialist` (primary).
---

# Skill: soc-control-walkthrough

**Purpose:** Produce control walkthrough documentation that satisfies an auditor on first review — not third. Walkthroughs are where most SOC audit time gets burned. Used by `audit-prep-specialist` (primary).

## When to use

- Pre-audit prep (SOC 1 Type II, SOC 2 Type II, SOX, ICFR)
- New control activated — document before the first audit cycle that will test it
- Process / system change that alters an existing control
- Auditor walkthrough request (planning / interim / year-end)
- Internal audit testing
- Post-deficiency remediation documentation

## What a walkthrough is

A walkthrough demonstrates that a control:

1. **Exists** as documented (Test of Design — ToD)
2. **Operates consistently** as documented (Test of Operating Effectiveness — ToE)

The walkthrough is the package: control description + evidence-of-control across a representative time period + the auditor's reperformance results.

## Anatomy of a control description

Every control walks through six dimensions:

| Dimension | Question | Example |
|---|---|---|
| **What** | What does the control do? | "Bank reconciliations are prepared monthly for every operating bank account" |
| **Who** | Who performs it? Who reviews? | "Prepared by Staff Accountant; reviewed by Accounting Manager; both sign off" |
| **When** | What frequency? When relative to other steps? | "Monthly, completed by working day 5 of close" |
| **Where** | What system / artifact? | "In NetSuite Bank Recon module; sign-off captured in NetSuite review log" |
| **Why** | What risk does it mitigate? | "Mitigates risk of unrecorded transactions, misappropriation, or recording errors" |
| **Evidence** | What proves it happened? | "Reconciliation report exported; preparer + reviewer sign-off timestamps in audit log" |

A control description missing any dimension is incomplete. The walkthrough cannot pass.

## Test of Design (ToD)

ToD asks: **if the control operates as designed, would it actually prevent or detect the risk?**

Test of Design steps:

1. Read the control description with the risk it's meant to address
2. Identify the **completeness, accuracy, validity, restricted-access (CAVR)** assertions the control supports
3. Walk through one instance of the control end-to-end with the operator
4. Confirm the evidence trail captures enough to demonstrate the control happened
5. Note any design gap (e.g., "control says monthly but the risk requires daily")

Output: a memo or table — "Control X is designed to address risk Y. Design is adequate / inadequate because Z."

## Test of Operating Effectiveness (ToE)

ToE asks: **does the control actually operate as designed across the period?**

ToE requires a **sample**:

| Control frequency | Standard sample size |
|---|---|
| Daily | 25-40 instances (more for high-volume) |
| Weekly | 15-25 instances |
| Monthly | 2-6 instances depending on auditor's risk assessment |
| Quarterly | 2 instances |
| Annual | 1 (the population) |

(Exact sample sizes vary by audit firm and risk assessment. AICPA AT-C §205 and §315 govern. PCAOB AS 2410 governs for ICFR. State the framework being applied.)

For each sample item:

1. Operator provides the source artifact (the reconciliation, the approval, the reviewer sign-off)
2. Auditor re-performs the control or independently inspects the evidence
3. Auditor notes pass / exception / not-able-to-test

## Evidence-of-control patterns

The most-tested control evidence patterns:

| Control type | Evidence |
|---|---|
| Authorization | Approver name + date + dollar threshold check |
| Reconciliation | Recon worksheet + reviewer sign-off + supporting documentation reference |
| Segregation of duties | Two distinct users on the workflow (initiator ≠ approver) |
| Access control | User-role assignment list + last-access review + termination notice tie-out |
| System-generated report | Report parameters + timestamp + spot-check of inputs |
| Manual review | Reviewer initials / electronic sign-off + date + variance / exception notes |
| IT general controls | Change-management ticket + test evidence + production-deploy log + reviewer sign-off |

**Smell test:** if the evidence is "we always do it," the evidence is missing. If it's "here's the artifact dated Day Z signed by Person A and reviewed by Person B on Day Z+1," it's evidence.

## Sampling discipline

- **Random selection** from the population, not "the auditor picked a month they like." Document the random-selection method.
- **Stratified sampling** when the population has obvious sub-groups (e.g., big-dollar vs small-dollar approvals) — sample both strata.
- **Population definition matters.** A control over "all journal entries" requires a population list. A control over "manual journal entries above $X" has a different population. State which.
- **Coverage of the period.** Samples should span the audit period — not all from Q1.

## Exception triage

When ToE finds an exception (the control didn't operate, or evidence is missing):

```
Step 1. Confirm the exception is real (not an inspection error)
Step 2. Quantify the population affected (just this one? more?)
Step 3. Classify the cause:
  - Operator error (one-off vs systemic?)
  - Design gap (control doesn't cover what it claims)
  - System failure (automation didn't fire)
  - Evidence gap (control happened but no proof)
Step 4. Assess potential impact:
  - Direct financial misstatement risk?
  - Compensating control covers it?
  - Is it a single instance or symptomatic?
Step 5. Document the cause + extent + management response
```

## Deficiency severity classification

After exceptions are triaged, classify:

| Class | Definition | Auditor action |
|---|---|---|
| **Inconsequential** | Deficiency exists but does not rise to a meaningful concern individually or in aggregate | Note for management; usually no report mention |
| **Control deficiency** | Design or operation does not enable management or employees to prevent / detect misstatements timely; less than significant | Management letter |
| **Significant deficiency (SD)** | A deficiency, or combination of deficiencies, that is less severe than a material weakness, yet important enough to merit attention by those charged with governance | Communicated to those-charged-with-governance |
| **Material weakness (MW)** | A deficiency, or combination, such that there is a reasonable possibility that a material misstatement will not be prevented or detected | Reported in audit opinion (for ICFR); restricts the audit opinion |

(Definitions from PCAOB AS 2201 / AICPA AU-C §265. Pull the current authoritative wording for the engagement's framework.)

**Threshold question:** "Could a material misstatement in the financial statements arise from this and not be caught?" — yes → MW track; no → SD or lesser.

Document the rationale for the classification explicitly. Auditors will challenge.

## Compensating controls

When a primary control fails, a **compensating control** may reduce the deficiency severity. Compensating controls must:

- Be in place and operating during the same period
- Be effective at detecting the same risk
- Be at sufficient precision (a quarterly review doesn't compensate for a daily authorization gap on transactions > $X)

Document the compensating control's design and operating-effectiveness evidence the same way as a primary control. Don't claim a compensating control without testing it.

## Remediation tracking

Each open finding gets:

- Description of the deficiency
- Severity classification
- Root cause
- Remediation owner (named)
- Remediation target date
- Validation step (re-test after remediation)
- Status (Open → In Progress → Remediated → Validated → Closed)

Track in a central tracker. Roll forward monthly. Stale "Open" items > 90 days are themselves a finding pattern.

## Common failure modes

- **"We do it" without evidence** — verbal walkthrough with no artifact. Auditor cannot test.
- **Reviewer sign-off without a date** — meaningless. Sign-off must be timestamped.
- **Sample of 1 from the start of the period** — fails coverage. Spread across the period.
- **Operator describes what they "should" do, not what they actually did** — interview vs evidence mismatch. Always ask for the artifact.
- **System-generated report claimed as evidence without parameter / timestamp** — claim is unverifiable.
- **Compensating control claimed but never tested** — doesn't count.
- **Deficiency-severity classification done without consultation** — significant deficiencies and material weaknesses are auditor calls; management's view matters but doesn't bind.
- **Remediation "in progress" for 18 months** — itself a deficiency in the remediation process.
- **Different auditor framework cited inconsistently** — SOC 1 vs SOC 2 vs ICFR have different criteria. State which.

## Walkthrough output

Each walkthrough produces:

1. **Control description** — six dimensions (What / Who / When / Where / Why / Evidence)
2. **Walkthrough memo** — narrative of the one-instance demonstration
3. **ToD conclusion** — design adequate / inadequate + rationale
4. **ToE testing memo** — sample size + selection method + per-item result
5. **Exceptions log** — for any items that failed
6. **Deficiency classification** (if any)
7. **Cross-reference to risk register / control matrix**

## See also

- Skill: [`../month-end-close/SKILL.md`](../month-end-close/SKILL.md) — many ToD/ToE walkthroughs occur in close
- Template: [`../../templates/audit-pbc-tracker.md`](../../templates/audit-pbc-tracker.md)
- Agent: [`../../agents/audit-prep-specialist.md`](../../agents/audit-prep-specialist.md)
- Agent: [`../../agents/controller.md`](../../agents/controller.md)
- Cross-plugin: [`../../../regulatory-compliance/skills/control-testing/SKILL.md`](../../../regulatory-compliance/skills/control-testing/SKILL.md) — regulator-facing control testing (related but distinct discipline)
