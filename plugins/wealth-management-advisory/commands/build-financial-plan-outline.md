---
description: "Build a CFP-process-aligned financial plan outline for an advisor's client profile: goals discovery, current situation, prioritized planning issues by life stage, recommendations with rationale stubs, and action items. Produces advisor-prep work; not personalized client advice."
argument-hint: "[client profile, e.g. '52-year-old physician couple, $2.8M investable, retiring at 60, two college-bound kids, large traditional IRA']"
---

You are running `/wealth-management-advisory:build-financial-plan-outline`. Use the
`financial-planning-specialist` discipline and the `financial-planning-process` skill.

## Steps

1. From the client profile provided, identify: life stage (accumulation / pre-retirement / 
   retirement / legacy), key asset/liability picture, income sources, insurance and estate status.
2. Run the **goals-discovery framework** from `skills/financial-planning-process/SKILL.md`
   (Step 2) — identify the primary financial-independence target, retirement date, income
   replacement goal, major upcoming expenditures, legacy intent.
3. Map the client's situation against the **planning-issues-by-life-stage table** (Step 3) —
   identify the top 3–5 planning issues most relevant to this profile.
4. For each planning issue, draft a **recommendation stub**: the issue, the current situation,
   the preliminary recommendation direction, and a rationale placeholder.
5. Produce a **prioritized action-item list** (owner: advisor vs. client vs. CPA vs. attorney;
   urgency: urgent / high-value / ongoing).
6. Fill in the structure of
   [`templates/financial-plan-outline.md`](../templates/financial-plan-outline.md) with the
   above content.
7. Flag any product recommendations for `advisory-compliance-advisor` Reg BI clearance before
   the plan is presented. Add the "advisor should review before presenting to client" note.
8. Emit the Structured Output block with the plan outline and handoff recommendations.
