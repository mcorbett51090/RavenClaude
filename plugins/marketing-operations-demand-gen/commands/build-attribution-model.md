---
description: "Select and implement a multi-touch attribution model — traverse the attribution-model selection tree, define marketing-sourced vs marketing-influenced pipeline, specify the CRM campaign influence configuration, and produce a channel ROI report template with named model and documented limitations."
argument-hint: "[context, e.g. 'B2B SaaS, 90-day average sales cycle, Salesforce CRM, HubSpot MAP, $500K annual marketing spend, 3 main channels: paid search, LinkedIn, events']"
---

You are running `/marketing-operations-demand-gen:build-attribution-model`. Use the
`attribution-analyst` discipline and the `attribution-modeling` skill.

## Steps

1. Traverse the Attribution-model selection decision tree in
   `knowledge/marketing-ops-decision-trees.md` top-to-bottom using the context provided.
   Name the model you recommend and the leaf you land on.

2. Define marketing-sourced (MS) and marketing-influenced (MI) using the standard definitions.
   Document the lookback window and the qualifying touch types. Confirm these align with the
   lifecycle model (use the `lead-scoring-and-lifecycle` skill for the stage definitions if
   needed).

3. Specify the UTM taxonomy required to support the attribution model. Reference
   `templates/utm-taxonomy.md` for the governance structure. Flag any gaps in current UTM
   coverage that would impair attribution quality.

4. Produce the CRM campaign influence configuration specification:
   - Salesforce: Campaign Influence model settings, Primary Campaign Source setup, custom
     influence model if needed.
   - HubSpot: Revenue Attribution settings and deal association rules.
   - OR: recommended third-party attribution tool (Dreamdata, HockeyStack) with integration
     seams, if the CRM-native option is insufficient for the sales cycle complexity.

5. Build the channel ROI report template with: channel, spend, MQLs attributed, SQLs attributed,
   pipeline attributed, CAC, pipeline-to-spend ratio — and the attribution model named in every
   table header. Include a "Model caveats" section.

6. Document the quarterly model maintenance protocol (model review, UTM coverage audit,
   MS/MI definition drift check).

7. Emit the Structured Output block with model limitations stated, handoffs
   (marketing-ops-lead for lifecycle alignment, marketing-automation-engineer for MAP UTM
   instrumentation, data-platform for the BI layer).
