---
name: rate-and-report-audit-findings
description: "Turn tested control gaps into well-formed internal-audit findings and report them by traversing the issue-rating branch of the internal-audit decision tree, then return each finding on the 5 C's (Criteria/Condition/Cause/Consequence/Corrective action), an impact×likelihood rating (high/medium/low), the agreed management action plan (owner + date), the audit-committee summary, and the follow-up / remediation-validation plan. Reach for this when the user asks 'write this control gap as a finding', 'how bad is this issue / what rating?', 'draft the audit report or committee summary', or 'how do we validate the fix closed?'. Used by audit-engagement-specialist (primary) and internal-audit-lead."
---

# Skill: rate-and-report-audit-findings

> **Invoked by:** `audit-engagement-specialist` (primary — writing up the fieldwork) and `internal-audit-lead` (rolling issues up to the audit-committee residual-risk picture).
>
> **When to invoke:** "write this deviation/gap up as a finding"; "what's the rating — high/medium/low?"; "draft the audit report / the audit-committee summary"; "agree a management action plan"; "how do we follow up and validate the remediation closed?"; any "how do we report and close this issue?" question.
>
> **Output:** each finding on the 5 C's + an impact×likelihood rating + the management action plan (owner/action/date) + the report / audit-committee summary + the follow-up / remediation-validation plan + the 1-2 flip conditions on the rating.

## Procedure

1. **Confirm there's a finding, not an observation.** A finding needs a **criterion** (the "should-be") the condition breaches. No criterion → it's an observation or an improvement suggestion; label it as such rather than inflating it.
2. **Write every finding on the 5 C's.** **Criteria** (the policy/reg/framework/standard should-be) · **Condition** (what testing actually found, with the sample result) · **Cause** (the *root* cause — why it happened, not the symptom) · **Consequence** (the so-what: the risk/exposure, quantified where you can) · **Corrective action** (management's agreed fix). Weak Cause or Consequence is the most common reason a finding fails to drive action.
3. **Rate the issue on impact × likelihood.** Traverse the issue-rating branch in [`../../knowledge/internal-audit-decision-tree.md`](../../knowledge/internal-audit-decision-tree.md): position the issue on the **impact × likelihood** matrix to a **high / medium / low** rating, factoring the consequence severity, the pervasiveness (isolated vs systemic), and any compensating controls. Rate the *residual* risk after compensating controls, and be consistent across the engagement so ratings roll up meaningfully.
4. **Agree a management action plan — don't author it.** For each finding, management commits an **action**, an **owner**, and a **due date**. IA facilitates and challenges the adequacy of the plan; **IA does not write the remediation for management** (that would forfeit the independence to later validate it). Record management's response, including any accepted-risk / no-action position and its rationale.
5. **Report at the right altitude for the audience.** The **engagement report** carries the objective, scope, opinion/conclusion, the findings with ratings, and the action plans. The **audit-committee summary** rolls up — coverage, the **significant** issues, the **residual-risk narrative**, and the state of open/overdue remediation — the *state of control*, not a task list. Lead with the rating distribution and the trend.
6. **Follow up until validated.** Track each action plan to its due date; on completion, **re-test the remediated control** with fresh evidence before closing — a management "done" is a claim, not a close. Report overdue and past-due-with-elevated-risk items to the committee.
7. **State the flip conditions** — the 1-2 facts that would change the rating (a compensating control surfaced in review, a population wider than sampled, an accepted-risk decision by an appropriate authority that changes the residual exposure).

## Worked example

> User: "Three-way match was overridden on 3 of 25 sampled payments with no secondary approval. Write it up."

- **Finding (5 C's):**
  - **Criteria** — the P2P policy requires a valid three-way match or a documented secondary approval before payment.
  - **Condition** — 3 of 25 sampled payments (12%) were released on a manual match-override with **no** secondary approval; extrapolated, ~X of the annual override population.
  - **Cause** — the AP system permits an override without enforcing the secondary-approval workflow (design gap), and AP staff were not trained on the exception path (operating gap).
  - **Consequence** — unauthorized/duplicate disbursement risk; $Y of payments bypassed the key preventive control this period.
  - **Corrective action** — (management) enforce the secondary-approval workflow on override in the system; remediate the training gap.
- **Rating:** a **key preventive control** bypassed, systemic (design-level), material dollar exposure → **High** (high impact × moderate-high likelihood). If a detective month-end review reliably catches these (a compensating control), it may drop to **Medium** — state that as the flip condition.
- **Management action plan:** owner = AP Controller; action = system config + training; due = next quarter-end.
- **Committee summary:** 1 High (P2P override) in this engagement; trend and remediation status noted.
- **Follow-up:** re-test the override population *after* the config change closes — not on the "done" email.

## Guardrails

- **No criterion → not a finding.** Call it an observation or a suggestion; don't inflate.
- **All 5 C's, especially Cause (root, not symptom) and Consequence (the quantified risk)** — these carry the rating and the fix.
- **Rate residual risk consistently** on impact × likelihood so issues roll up to a meaningful committee picture; factor compensating controls but don't let them silently erase a design gap.
- **Management owns the action plan; IA facilitates and challenges it** — IA authoring the remediation forfeits the independence to validate it.
- **Closed means re-tested** with fresh evidence — a management "done" is a claim, not a close.
- **Report the state of control, not the volume of activity** — the committee wants residual risk and remediation status, not an audit tally.
- Volatile claims (rating-scale definitions tied to a policy, regulatory criteria) carry a **retrieval date** and are re-verified before the report is finalized. See [`../../knowledge/internal-audit-patterns-2026.md`](../../knowledge/internal-audit-patterns-2026.md).
