---
name: denial-prevention-and-appeals
description: "Prevent PT/rehab claim denials at the front end (eligibility, authorization, units, modifiers, documentation) and triage the ones that slip through to their root cause, then write a documentation-grounded appeal — confirming each payor's edits before billing."
---

# Denial Prevention & Appeals

A denial is the expensive recovery of a front-end miss. Prevent first; appeal with evidence.

## Front-end prevention (before the claim leaves)

1. **Eligibility + benefits** verified — active coverage, therapy benefit, visit cap.
2. **Authorization** in hand if required, with enough visits.
3. **Units** correct under the 8-minute rule (see [`../therapy-billing-and-units/SKILL.md`](../therapy-billing-and-units/SKILL.md)).
4. **Modifiers** correct (GP/KX/59) and supported by documentation.
5. **Documentation** establishes medical necessity and skilled care (see [`../defensible-documentation/SKILL.md`](../defensible-documentation/SKILL.md)).

## Denial triage (root cause → fix)

| Denial signal | Likely root cause | Fix |
|---|---|---|
| Units / frequency | 8-minute-rule variant, cap exceeded | Recount; check payor variant + auth |
| Modifier / NCCI edit | Missing/wrong GP/KX/59 | Match modifier to discipline/threshold/distinct service |
| Medical necessity | Boilerplate / no skilled justification | Documentation, not appeal language, is the fix |
| Eligibility / auth | Front-end miss | Verify before re-submission |

## The appeal

Lead with the **documentation that already exists** — the note is the evidence. Cite the specific clinical reasoning, the POC goal, and (if threshold) the KX attestation basis. A late or boilerplate appeal loses.

## Verify-at-use

- **Each payor's denial reason codes, edits, and appeal windows differ and change** — confirm against the payor's current policy before re-billing or appealing. `[verify-at-use]`.

Traverse the denial-triage tree in [`../../knowledge/pt-clinic-decision-trees.md`](../../knowledge/pt-clinic-decision-trees.md); template at [`../../templates/denial-appeal-letter.md`](../../templates/denial-appeal-letter.md).
