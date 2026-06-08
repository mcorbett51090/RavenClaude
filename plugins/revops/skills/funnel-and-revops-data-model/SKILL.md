---
name: funnel-and-revops-data-model
description: "Define the B2B lead-to-cash funnel and the bowtie as one accountable revenue engine: one definition per stage (MQL/SQL/SAL/opportunity), the funnel metric glossary, the CRM-neutral RevOps data model, and the marketing↔sales↔CS SLAs/handoffs — with one source of truth, not two teams with two definitions."
---

# Funnel & RevOps Data Model

## Start from one definition, not the tooling
Most RevOps disputes are two teams with two definitions of the same stage. Define MQL/SQL/SAL/opportunity-stage **once**, by criteria the *downstream* team accepts, instrument each at exactly one point, and report from one source of truth. Wire an accept/reject feedback loop so the definition stays honest.

## Model the bowtie, not a triangle
B2B revenue compounds after closed-won. Model acquisition (left) and retention/expansion (right) as one connected motion. The right side's health/churn model hands to `customer-success-analytics`, but the funnel definition connects both sides as one engine.

## The funnel metric glossary
Name each metric once: MQL/SAL/SQL, conversion (stage N→N+1 ÷ entering N), sales velocity ((opps × win-rate × ACV) ÷ cycle), pipeline coverage (open ÷ gap — target derived from win-rate). Compute per segment/source, not in aggregate.

## The RevOps data model is CRM-neutral
Accounts/contacts/leads/opportunities/activities, the relationships, and one system of record per object — designed so a CRM migration is a remap, not a redefinition. Hand the platform build (objects/flows/Apex) to `salesforce`; the model is the contract it encodes.

## SLAs make handoffs real
Marketing→sales and sales→CS handoffs have a speed clock, an accept/reject loop, and a named owner — or they're where leads go to die. Document the speed-to-lead SLA, the closed-won→onboarding handoff, and the renewal-pipeline handoff.

## Output
A funnel-and-data-model brief: the lead-to-cash funnel + bowtie, one definition per stage, the metric glossary, the CRM-neutral data model, the marketing↔sales↔CS SLAs, and the build handoff to `salesforce` / `data-platform` / `tableau`.
