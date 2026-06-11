---
name: referral-management-and-new-patient-conversion
description: "Grow and protect the referral pipeline and convert referrals to evaluations — track referral-source volume and trend, spot sources going cold, fix the referral→scheduled→arrived→evaluated funnel with speed-to-contact, and plan direct-access growth within scope."
---

# Referral Management & New-Patient Conversion

**Purpose:** keep the front of the pipeline full and flowing — manage referral sources like a sales
pipeline, and convert the referrals you get into evaluated patients.

---

## Steps

### 1. Track referral sources like a pipeline

For each referral source (physician, group, self-referral channel), track volume and trend. A single
high-volume source quietly going cold can outweigh any marketing — so a declining source is an alert,
not a footnote. Use [`../../scripts/pt_calc.py`](../../scripts/pt_calc.py) for source share and trend.

### 2. Measure referral → evaluation conversion

```
referral → scheduled → arrived → evaluated → plan-of-care started
```

Each arrow is a conversion. `referral_conversion_rate` localizes the leak. Referrals that never become
evaluations are lost revenue and a frustrated referral source.

### 3. Fix the leak with speed-to-contact and access

| Leak | Fix |
|---|---|
| referral → scheduled | speed-to-contact (call within hours, not days), easy scheduling |
| scheduled → arrived | reminders, benefit/cost clarity up front, directions |
| arrived → evaluated | front-desk readiness, verification done before arrival |

Speed-to-contact is the highest-leverage lever: conversion drops sharply with each day of delay.

### 4. Close the loop with referral sources

Send outcome/status updates back to referring physicians. A source that sees good outcomes and clear
communication refers more; the loop is the relationship.

### 5. Plan direct-access growth within scope

Where state practice acts and payer rules allow patient self-referral, design the acquisition channel
and access experience — and flag the scope/visit-limit caveats for verification.

---

## Output

A referral-source analysis, a conversion-funnel fix, and a referral relationship plan. Use the
[`referral-source-scorecard`](../../templates/referral-source-scorecard.md) template; deepen with the
[`referral-and-revenue-cycle-reference`](../../knowledge/referral-and-revenue-cycle-reference.md).
