---
description: "Plan a marketing campaign end-to-end — apply the campaign taxonomy, fill the campaign brief, set UTM parameters, create the MAP and CRM campaign records, enter the campaign in the cost ledger, and complete the launch checklist."
argument-hint: "[context, e.g. 'ABM webinar for enterprise Salesforce admins, Q3 2026, $15K budget, target 50 MQLs, HubSpot + Salesforce, 3 follow-up nurture emails']"
---

You are running `/marketing-operations-demand-gen:plan-campaign`. Use the
`demand-gen-strategist` and `marketing-automation-engineer` disciplines and the
`campaign-operations` skill.

## Steps

1. Apply the campaign taxonomy to produce the canonical campaign name:
   `[Year]-[Quarter]-[Segment]-[Motion]-[Name]`. Confirm the name will be used consistently
   in the MAP, CRM, cost ledger, and UTM parameters.

2. Fill `templates/campaign-brief.md` with the campaign objectives, ICP target segment, channel
   mix, budget, pipeline contribution target, success metrics, and key dates.

3. Generate the UTM parameter set for all campaign assets using `templates/utm-taxonomy.md`.
   Validate that all required parameters are present (source, medium, campaign in kebab-case).
   Produce a URL-builder example for the campaign landing page and any email CTAs.

4. Specify the MAP campaign/program setup:
   - Campaign type, success criteria, member status progression.
   - Entry criteria (who enters the program).
   - Suppression logic (current customers, active opportunities if applicable, unsubscribes,
     competitor domains).
   - Consent / opt-in verification note for any email components.

5. Specify the CRM campaign record setup (Salesforce or HubSpot):
   - Campaign name (matching taxonomy), type, start/end dates, budget.
   - Campaign Influence settings and attribution model to apply.

6. Produce the cost ledger entry for this campaign (canonical name, channel, budget,
   vendor/publisher, GL code placeholder).

7. Output the completed campaign brief, UTM set, MAP/CRM setup spec, cost ledger entry, and
   the launch checklist from `skills/campaign-operations/SKILL.md` with all items pre-filled
   for this campaign. Emit the Structured Output block with handoffs (attribution-analyst to
   confirm UTM coverage, marketing-ops-lead to confirm suppression and MQL routing).
