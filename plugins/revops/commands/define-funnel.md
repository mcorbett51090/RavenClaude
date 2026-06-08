---
description: "Define the B2B lead-to-cash funnel + bowtie as one accountable revenue engine: one definition per stage, the RevOps data model, and the marketing↔sales↔CS SLAs."
argument-hint: "[current funnel + teams + CRM/warehouse stack + where definitions disagree]"
---

You are running `/revops:define-funnel`. Use `revops-architect` + the `funnel-and-revops-data-model` skill.

## Steps
1. Surface where marketing, sales, and CS define the funnel differently — if any stage has two definitions, that's the root problem; name it before anything else.
2. Define the lead-to-cash funnel + the bowtie (acquisition + retention/expansion as one motion), with one objective definition per stage (MQL/SQL/SAL/opportunity/closed-won/renewal).
3. Specify the funnel metric glossary (conversion, velocity, coverage) and the single instrumentation point per stage.
4. Draw the CRM-neutral RevOps data model (accounts/contacts/leads/opps/activities + system of record per object) and the marketing↔sales↔CS handoff SLAs.
5. Route the builds: platform → salesforce, warehouse mart → data-platform, dashboard → tableau, post-sale health → customer-success-analytics.
6. Emit the funnel-and-data-model brief + the Structured Output block (with `Revenue impact:` and `Handoff to system teams:`).
