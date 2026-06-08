---
description: "Structure a CAPA from a nonconformance: containment, root-cause analysis, corrective + preventive action, effectiveness check, and the control-plan/FMEA update."
argument-hint: "[the defect/NCR + where/when found + affected product + any SPC/inspection data]"
---

You are running `/manufacturing-operations:run-capa`. Use `quality-and-capa-lead` + the `capa-and-spc` skill.

## Steps
1. Capture the nonconformance precisely (what, where, when, how much, affected product) and the immediate containment that stops the bleeding.
2. If SPC data exists, call special vs common cause first — limits from the process, not the spec; don't tamper with common-cause noise.
3. Run root-cause analysis (5-Whys / fishbone / is–is-not) to the actual cause, not the symptom.
4. Separate the corrective action (fix this batch) from the preventive action (remove the cause); define the effectiveness check.
5. Update the control plan / FMEA so the cause is prevented or detected at the source (prevention > detection > scrap).
6. Route the deep work: Gage R&R / capability-study math → applied-statistics; design-the-cause-out → process-improvement; supplier sourcing → procurement-sourcing. For regulated/safety-critical product, draft only and escalate closure to the accountable human.
7. Emit the CAPA report + the Structured Output block (with `Constraint respected:` and `Handoff to method teams:`).
