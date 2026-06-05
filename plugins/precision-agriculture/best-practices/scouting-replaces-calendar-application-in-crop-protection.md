# Scouting Replaces Calendar Application in Crop Protection

**Status:** Absolute rule
**Domain:** Crop protection / IPM
**Applies to:** `precision-agriculture`

---

## Why this exists

Calendar-based crop protection (spray every 14 days, apply at tassel regardless of pressure) is the most expensive and least effective application strategy available. It ignores actual pest and disease pressure, builds resistance through unnecessary applications, and applies chemistry when the economic threshold has not been reached — spending $18–$35/acre [unverified — training knowledge] on an application that returns nothing. Scouting-based applications triggered by economic thresholds (ETs) have decades of university research behind them as the economically and agronomically superior approach. The rule is not optional in a margin-conscious operation.

## How to apply

Build a field-specific scouting and threshold protocol:

```
Scouting protocol (per field, per growth stage):
  Scouting frequency:
    Pre-tassel corn:       every 5–7 days for rootworm, aphids, gray leaf spot
    Soybean V6–R3:         every 5–7 days for bean leaf beetle, aphid, white mold risk
    Wheat anthesis:        daily during heading for scab risk + weather model

  Economic threshold examples [unverified — training knowledge]:
    Corn aphid:            250+ per plant, building population, no natural enemy activity
    Soybean aphid:         250+ per plant, R1–R5 growth stage, population building
    Soybean bean leaf beetle: 30% defoliation pre-bloom; 20% defoliation post-bloom

  Application trigger document:
    Field ID: ______   Date: ______   Scout: ______
    Pest / disease observed: ______   Count / severity: ______
    ET reached? (yes/no): ______
    Recommended action: ______   Product: ______   Rate: ______
    Expected return (yield protection × price − application cost): $______/acre
```

**Do:**
- Require a written scouting record with ET assessment before authorizing any fungicide, insecticide, or herbicide application outside of pre-plant treatments.
- Use university-published ETs for the region and crop — they are peer-reviewed, not product-company estimates.
- Track application history and resistance flags by field and mode of action; calendar applications drive resistance faster than threshold-based ones.

**Don't:**
- Apply a fungicide or insecticide "just in case" without a scouting record showing ET has been reached or that environmental conditions make ET imminent.
- Confuse a prophylactic herbicide at planting (pre-emergent — addressed to a different risk) with in-season threshold-based applications; the prophylactic logic is different.

## Edge cases / when the rule does NOT apply

High-value specialty crops (wine grapes, seed production, organic certified) may have lower economic thresholds or zero-tolerance disease/pest standards that justify prophylactic applications — the threshold logic still applies but the ET is lower. Fields with confirmed heavy insect or disease pressure from adjacent fields in a known epidemic year may justify pre-ET applications as a risk management decision, documented explicitly.

## See also

- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — owns the scouting protocol and ET application decision.
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — models the expected return on the protection application.
- [`./crop-protection-is-threshold-and-resistance-management-not-c.md`](./crop-protection-is-threshold-and-resistance-management-not-c.md) — the parent rule; scouting is the operational execution of that discipline.

## Provenance

Economic threshold-based crop protection is the foundation of Integrated Pest Management (IPM); ETs are published by the Cooperative Extension system (Purdue, Iowa State, University of Illinois, etc.) and are the operative standard in agronomic consulting.

---

_Last reviewed: 2026-06-05 by `claude`_
