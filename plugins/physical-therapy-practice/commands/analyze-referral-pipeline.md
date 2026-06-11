---
description: "Analyze the referral pipeline and new-patient conversion — track referral-source volume/trend, spot sources going cold, measure referral→evaluation conversion, and fix the leak with speed-to-contact and access."
---

# /analyze-referral-pipeline

Spawn `referral-and-patient-access-strategist` to analyze and grow the front of the pipeline.

## What it does

1. Tracks referral-source volume and trend; flags sources going cold.
2. Measures the referral → scheduled → arrived → evaluated funnel via [`../scripts/pt_calc.py`](../scripts/pt_calc.py) `referral_conversion_rate`.
3. Identifies the conversion leak and the fix (speed-to-contact, scheduling friction, benefit clarity).
4. Plans referral-loop closure (outcome updates back to referrers).

## Usage

```
/analyze-referral-pipeline
```

Then share referral counts by source and the referral→evaluation funnel data. The agent applies
[`referral-management-and-new-patient-conversion`](../skills/referral-management-and-new-patient-conversion/SKILL.md)
and the [`referral-source-scorecard`](../templates/referral-source-scorecard.md) template.

## Good inputs

- Referral volume by source over time.
- Referral → evaluation conversion and time-to-first-contact.
