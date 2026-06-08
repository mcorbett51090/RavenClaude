---
description: "Design or audit a rent collection and delinquency management process: collection cycle, late-fee enforcement, delinquency action ladder (days 1–45+), payment arrangement criteria, and legal notice coordination. Outputs the action ladder and economic occupancy impact analysis."
argument-hint: "[context, e.g. '80-unit portfolio, $1,600 avg rent, current delinquency 6%, AppFolio, Texas']"
---

You are running `/property-management-residential:plan-rent-collection`. Use the
`pm-ops-lead` and `leasing-strategist` disciplines and the `rent-collection-and-delinquency` skill.

## Steps

1. **Establish the collection cycle** — due date, grace period, late fee amount (confirm it is
   within jurisdiction statutory limits if the jurisdiction is known), auto-charge vs. manual
   invoicing in the PM software.

2. **Build the delinquency action ladder** — day-by-day contacts, notices, and escalations from
   day 1 through 45+. Use the ladder in `skills/rent-collection-and-delinquency/SKILL.md` as the
   baseline; adapt timing to jurisdiction's statutory notice requirements if known. Flag: **always
   verify current state law notice requirements before issuing legal notices.**

3. **Define payment arrangement criteria** — eligibility (prior late history, balance cap, plan
   specificity), required documentation (written agreement, schedule, default consequence). State
   the consistent-application rule explicitly.

4. **Calculate the economic occupancy impact** — use `scripts/pm_calc.py`:
   - `delinquency_rate()` — current delinquency as % of gross potential rent
   - `economic_occupancy()` — physical occupancy adjusted for vacancy loss, concessions, bad debt
   Show the owner/manager what each delinquent unit costs in annualized rent loss.

5. **Identify PM software configuration** — what needs to be configured in AppFolio / Buildium /
   Yardi Breeze to automate steps 1–2: late fee rules, notice templates, delinquency report
   schedule, payment portal activation.

6. **Flag legal-notice seam** — note that statutory pay-or-quit notice requirements vary by
   state/city (form, delivery method, cure period). Recommend `pm-compliance-advisor` review and
   landlord-tenant counsel for any jurisdiction-specific notice before filing.

7. **Emit the Structured Output Protocol block** with `handoff_recommendation` to `pm-ops-lead`
   (NOI and economic occupancy reporting) and `pm-compliance-advisor` (notice compliance review).
