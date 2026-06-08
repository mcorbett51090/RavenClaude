---
description: "Produce a DAP/SOAP/BIRP behavioral-health progress-note (or treatment-plan) template with a medical-necessity thread — structure only, PHI placeholdered, never clinical content."
argument-hint: "[note format preference (DAP/SOAP/BIRP) + service type + any audit/denial concern]"
---

You are running `/behavioral-health-practice:draft-progress-note-template`. Use `clinical-documentation-specialist` + the `clinical-documentation` skill.

## Steps
1. Confirm the format (DAP / SOAP / BIRP) or recommend one for the service type — structure only.
2. Build the template with placeholdered fields (`[Client]`, `[Dx]`, `[DOB]`); the clinician authors the clinical content.
3. Thread medical necessity through it: diagnosis → functional impairment → intervention delivered → client response → plan — so the note structurally supports the claim.
4. Add a short standards note (contemporaneous, behavioral, factual; the note is a legal record).
5. If an ROI/records-request angle is in scope, add the consent-before-disclosure gate and the 42 CFR Part 2 specific-consent check for SUD content.
6. Keep real PHI out entirely; route any clinical-content question to a licensed clinician. Align the note's necessity with the claim via billing-and-authorization-lead.
7. Emit the template + the Structured Output block (with `Not clinical advice:` and `PHI posture:` lines).
