# Stages are exit criteria, not vibes

**Status:** Absolute rule
**Domain:** Pipeline management
**Applies to:** `revenue-operations`

---

## Why this exists

A pipeline stage is a claim about a deal's position in the buying process. When that claim is based
on a rep's feeling rather than a verifiable condition, the pipeline is fiction — and any forecast
built on it is fiction compounded. "Rep thinks it's ready to move" is not a stage criterion; it is a
description of the rep's emotional state, which is uncorrelated with the buyer's actual position.

The problem compounds: reps who define stages by intuition will disagree with each other; managers
cannot inspect a deal against an undefined standard; the stage-probability defaults are wrong for
every rep; and the weighted or category forecast built on the stages is unreliable. The CRM becomes
a trophy cabinet for deals the rep feels good about, not an operational system of record.

## How to apply

For every pipeline stage, write down:

1. The **binary, objective conditions** that must be true for a deal to be in that stage.
2. **Where each condition is verifiable in the CRM** (a field, an attached document, a contact
   role, a date field).
3. **Who can verify it** — it cannot require asking the rep to summarize their feeling.

**Do:**

- Write exit criteria as checkboxes: "Champion identified (Contact Role = Champion in CRM)",
  "Technical win documented (Opportunity note with date)", "Close date within 90 days."
- Validate exit criteria against the CRM: if the condition cannot be confirmed from CRM data,
  it is not a CRM-enforceable exit criterion.
- Use validation rules to enforce stage-exit criteria mechanically — do not rely on training alone.
- Calibrate stage probabilities from historical win-rate data by stage, not from estimates.

**Don't:**

- Write exit criteria that include rep judgment ("rep confident", "deal feels warm", "rep believes
  budget is approved").
- Accept "Proposal Sent" as an exit criterion without a corresponding logged activity in the CRM
  confirming delivery.
- Use a stage model designed by someone who has never spoken to the sales team about what actually
  happens at each stage.

## Edge cases / when the rule does NOT apply

In a very early-stage, seed-funded company with fewer than three AEs and no meaningful historical
data, a lightweight stage model with fewer stages and acknowledged subjective criteria may be
appropriate as a starting point — but it must be labeled as temporary and reviewed at the first
opportunity with real close data. Even a subjective criterion must be written down; "I'll know it
when I see it" is not a criterion.

## See also

- [`./one-definition-of-pipeline.md`](./one-definition-of-pipeline.md)
- [`./a-forecast-is-a-commitment-not-a-hope.md`](./a-forecast-is-a-commitment-not-a-hope.md)
- [`../skills/pipeline-hygiene-and-stage-definitions/SKILL.md`](../skills/pipeline-hygiene-and-stage-definitions/SKILL.md)
- [`../templates/stage-definition-doc.md`](../templates/stage-definition-doc.md)

## Provenance

Codifies the SRM (Sales Review Meeting) discipline and the MEDDIC/MEDDPICC qualification
methodology community consensus that objective exit criteria are the foundation of a trustworthy
pipeline and a reliable forecast. Consistent with Salesforce's own published pipeline-management
best practices.

---

_Last reviewed: 2026-06-08 by `claude`._
