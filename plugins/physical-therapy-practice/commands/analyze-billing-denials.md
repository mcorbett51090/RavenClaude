---
description: "Analyze and prevent PT billing denials — cluster denials by reason code to their origin, verify timed units against the 8-minute rule, and fix each cause at the point it originates."
---

# /analyze-billing-denials

Spawn `billing-and-reimbursement-analyst` (with the documentation specialist for documentation-origin
denials) to analyze denials and build prevention.

## What it does

1. Clusters denials by reason code (medical necessity, units/8-minute-rule, authorization, modifier, coding).
2. Traces each cluster to its origin (documentation, point-of-care minutes, front desk, threshold tracking).
3. Verifies timed units via [`../scripts/pt_calc.py`](../scripts/pt_calc.py) `eight_minute_rule_units`.
4. Returns the prevention fix at the source for each cluster.

## Usage

```
/analyze-billing-denials
```

Then share your denial reason-code distribution and a sample denied claim (de-identified). The agent
applies [`pt-billing-units-and-denials`](../skills/pt-billing-units-and-denials/SKILL.md) and the
[`denial-prevention-checklist`](../templates/denial-prevention-checklist.md).

> Decision-support only — verify coding/payer specifics against current CMS/payer policy and a
> certified coder. Use **de-identified** records.
