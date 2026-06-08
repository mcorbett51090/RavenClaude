---
description: "Audit the GTM machine: pipeline hygiene, lead routing & scoring SLAs, territory/quota/comp, attribution, and CRM data quality enforced at the point of entry."
argument-hint: "[CRM + routing/scoring rules + quota/comp model + attribution model + known data issues]"
---

You are running `/revops:audit-pipeline-hygiene`. Use `gtm-systems-engineer` + the `pipeline-hygiene-and-routing` skill.

## Steps
1. Audit data quality at the point of entry: required fields per stage, dupes, dead accounts, stuck/aged deals — specify the entry-point enforcement (don't accept a quarterly scrub).
2. Audit lead routing & scoring: is there a defined owner, a speed-to-lead SLA, an accept/reject loop, and a scoring model with a feedback loop validated against conversion?
3. Audit territory & quota: is quota built bottoms-up from capacity and reconciled against the board number, with the gap surfaced? Flag uncovered whitespace / overlapping ownership.
4. Audit comp: name what the plan rewards and what it accidentally rewards (sandbagging, cherry-picking, end-of-quarter dumping).
5. Audit attribution: is one model (usually last-touch) silently driving budget? Name its distortion and recommend triangulation.
6. Route the platform build → salesforce; the warehouse/dashboard → data-platform / tableau; significance → applied-statistics. Emit the audit + the Structured Output block (with `Revenue impact:` and `Handoff to system teams:`).
