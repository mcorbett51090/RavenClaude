---
description: "Audit the CRM for data-hygiene problems — stale deals, missing required fields, stage-age outliers, duplicate records, and gaps between the stage model and actual deal state — and produce a prioritized remediation plan with automation and validation recommendations."
argument-hint: "[CRM platform and scope, e.g. 'Salesforce, 200 open opportunities, 3 AEs, last hygiene project was 18 months ago']"
---

You are running `/revenue-operations:audit-crm-hygiene`. Use the `crm-operations-architect`
discipline and the `pipeline-hygiene-and-stage-definitions` skill.

## Steps

1. Define the audit scope: CRM platform (Salesforce / HubSpot / other), number of open
   opportunities, date range, and which object types are in scope (Opportunities, Leads, Contacts,
   Accounts).

2. Run the five-point hygiene audit:
   - **Stale deals:** deals open with no activity in > 30 days (flag), > 60 days (escalate),
     > 90 days (recommend close or archival). Calculate stage-age median and flag outliers.
   - **Required-field completeness:** which fields (Close Date, Amount, Next Step, Champion/Contact
     Role) are blank or past-dated? Score by rep and by segment.
   - **Stage-exit criteria gaps:** for each deal in a late stage (Proposal, Verbal Commit),
     does the CRM data actually support that stage? (Champion in Contact record? Technical win
     documented? Close date realistic?) Score Red/Yellow/Green.
   - **Duplicate detection:** look for leads and contacts with the same email, same name + company.
     Estimate the duplicate rate.
   - **Forecast-category misalignment:** are deals in "Commit" category actually meeting exit
     criteria? Are there Commit deals with no activity in > 14 days?

3. Prioritize findings by downstream impact: which hygiene problems most corrupt the forecast?
   Rank: (1) stale Commit/Best-Case deals, (2) missing amounts in late stages, (3) missing
   champion/contact roles, (4) duplicates inflating pipeline count.

4. Design the remediation plan:
   - Immediate: a deal-review sprint to clean the top-10 Commit deals.
   - Short-term (< 30 days): validation rules to enforce required fields; aging policy to flag
     stale deals automatically.
   - Ongoing: recurring hygiene audit cadence (weekly: manager reviews flagged deals; monthly:
     full field-completeness report; quarterly: duplicate audit).

5. Recommend automation: which validation rules, workflow triggers, and assignment-rule changes
   would prevent the identified problems from recurring.

6. Emit the Structured Output block; hand validation-rule implementation to
   `crm-operations-architect`, forecast implications to `pipeline-forecast-engineer`, and
   governance model to `revops-lead`.
