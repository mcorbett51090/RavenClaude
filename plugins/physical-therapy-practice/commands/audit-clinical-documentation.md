---
description: "Audit PT clinical documentation for defensibility — check each note for skilled service, medical necessity, progress, and the timed-minute basis, review the plan of care, and prioritize the highest-risk gaps."
---

# /audit-clinical-documentation

Spawn `clinical-documentation-and-compliance-specialist` to assess documentation defensibility and
audit readiness.

## What it does

1. Checks notes against the four elements: skilled service, medical necessity, progress toward measurable goals, timed-minute basis.
2. Reviews the plan of care: goals, frequency/duration justification, certification/recert timing.
3. Verifies the unit basis via [`../scripts/pt_calc.py`](../scripts/pt_calc.py) (8-minute rule).
4. Prioritizes the highest-risk gaps (units without minutes, necessity not established, lapsed certs).

## Usage

```
/audit-clinical-documentation
```

Then paste a sample note and plan of care (de-identified). The agent applies
[`pt-documentation-and-compliance`](../skills/pt-documentation-and-compliance/SKILL.md) and the
[`plan-of-care-template`](../templates/plan-of-care-template.md).

> Decision-support only — verify specifics against current CMS/payer policy and a certified
> coder/compliance professional. Use **de-identified** records.
