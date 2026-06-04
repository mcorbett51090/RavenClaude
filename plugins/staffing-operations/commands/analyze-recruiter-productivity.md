---
description: "Analyze recruiter or desk productivity without blaming the under-fed — normalize for reqs-per-recruiter and order quality, separate speed from conversion, and check the unblock-vs-hire lever before any headcount or PIP recommendation."
argument-hint: "[the concern, e.g. 'leadership wants to PIP the bottom-3 recruiters by placements']"
---

# Analyze recruiter productivity

You are running `/staffing-operations:analyze-recruiter-productivity` for `$ARGUMENTS`. Do it the way the `recruiting-funnel-strategist` does — an under-fed recruiter on aged, uncompetitive orders is a supply problem in a performance costume (§3 #4).

## Steps
1. **Check feeding first** — reqs-per-recruiter and order quality per desk. Re-rank normalized for supply ([`../skills/recruiter-capacity-model/SKILL.md`](../skills/recruiter-capacity-model/SKILL.md)).
2. **Normalize for order difficulty** — credentialing-heavy or rural/hard-to-fill desks carry less; don't compare raw.
3. **Separate speed from conversion** — submittal-to-interview and offer-acceptance; a quality problem ≠ an activity problem.
4. **Check the unblock-vs-hire lever** — AI/automation can return up to ~17 hrs/recruiter/week (Bullhorn GRID 2026, `[ESTIMATE]`); the fix may be unblocking, not hiring.
5. **Only after 1–4**, if fed comparably with comparable mix and the funnel ratios are genuinely below peers, frame it as an execution conversation — leading with the specific stage that's off.

Traverse the **recruiter-underperformance tree** in [`../knowledge/staffing-decision-trees.md`](../knowledge/staffing-decision-trees.md).

## Output
A re-ranking that flags **under-fed vs. under-performing**, with the normalized denominator shown. Use [`../templates/recruiting-funnel-analysis.md`](../templates/recruiting-funnel-analysis.md) for the desk-level funnel.

## Guardrails
- Revenue-per-recruiter without a reqs-per-recruiter denominator is a vanity metric — never rank on it raw.
- No PIP recommendation before the feeding and difficulty checks are done.
- No recruiter PII in the deliverable — use desk/role identifiers (§3 #10).
