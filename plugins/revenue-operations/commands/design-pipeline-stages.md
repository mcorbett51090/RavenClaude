---
description: "Design or redesign opportunity pipeline stages with objective exit criteria, empirically calibrated probabilities, and forecast-category mapping — producing a stage-definition document ready for CRM implementation."
argument-hint: "[sales motion and context, e.g. 'enterprise B2B SaaS, 90-day average cycle, 5 AEs, currently using Salesforce with 6 undefined stages']"
---

You are running `/revenue-operations:design-pipeline-stages`. Use the `pipeline-forecast-engineer`
discipline and the `pipeline-hygiene-and-stage-definitions` skill.

## Steps

1. Gather inputs: existing stages (names + descriptions), historical win-rate data by stage if
   available, current CRM (Salesforce / HubSpot / other), average sales-cycle length, deal
   complexity (transactional vs. enterprise), and any known hygiene problems.

2. Traverse the forecast-method decision tree in
   `knowledge/revops-decision-trees.md` — the stage model must feed the forecast methodology the
   business is using or will adopt, so methodology selection comes first.

3. Design the stage model: for each stage, produce name, definition, **objective binary exit
   criteria**, default probability (from historical data if available; flag if using estimates),
   and forecast category (Omitted / Pipeline / Best Case / Commit / Closed).

4. Calibrate probabilities: if historical closed-deal data exists, calculate win-rate by stage
   using `scripts/revops_calc.py` (win-rate mode). If not, use industry benchmarks and flag
   every probability as `[estimate — calibrate from historical data; verify-at-use]`.

5. Run a hygiene audit on the current open pipeline against the new exit criteria: how many
   deals are in a stage they don't actually qualify for? Produce a Red/Yellow/Green breakdown.

6. Fill in `templates/stage-definition-doc.md`.

7. Produce CRM implementation notes: which fields must be required, which validation rules
   enforce exit criteria, and the migration plan for existing open deals.

8. Emit the Structured Output block; hand the CRM implementation to `crm-operations-architect`
   and the forecast-methodology alignment to `pipeline-forecast-engineer`.
