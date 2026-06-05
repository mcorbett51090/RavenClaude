# Crop Insurance Selection Requires APH Accuracy Before Coverage Selection

**Status:** Absolute rule
**Domain:** Risk management / crop insurance
**Applies to:** `precision-agriculture`

---

## Why this exists

Actual Production History (APH) is the foundation of crop insurance coverage: the guarantee is the APH yield × coverage level × projected price. A grower with inaccurate APH — under-reported yields that suppress the APH average — is buying insurance on a smaller number than their real production history warrants. An APH understate of 10 bu/acre on corn at 85% coverage and $4.50/bu represents $3.83/acre of under-coverage, recurring annually [unverified — ESTIMATE]. The coverage-level decision (75%, 80%, 85% RP) is secondary to making sure the APH itself is accurate. Most APH errors favor the insurance company because growers underreport in good years (less paperwork) and over-report actual losses in bad years.

## How to apply

Build an APH accuracy review before each crop insurance renewal:

```
APH accuracy review checklist (per unit/field, per crop):
  [ ] Pull the APH worksheet from the crop insurance agent (it shows all reported years)
  [ ] Compare each year's reported yield to the actual settled scale tickets or FSA records
  [ ] Flag any year with T-yield substitution (T-yields suppress the average in good regions)
  [ ] Check for yield exclusion eligibility (years with documented catastrophic weather events)
  [ ] Verify that all irrigated acres are correctly assigned to the irrigated practice code
  [ ] Check that spring-planted and fall-planted crops are filed under the correct type

  Yield exclusion test (per year in APH):
    Was this a county-level loss year? (>50% county loss) → apply for yield exclusion
    Excluded year replaced with the APH average → APH increases, coverage increases

  APH correction:
    If reported yields are below scale tickets → request yield correction through the agent
    Statute of limitations: APH corrections are generally available for 2–3 crop years back [unverified]
```

**Do:**
- Request the full APH history from your agent at every renewal — do not rely on the summary; check the underlying years.
- Apply for yield exclusion in every eligible year; it is not automatic and it consistently raises the APH average.
- Match the enterprise unit structure (optional units vs. basic units vs. enterprise units) to the actual risk distribution of the operation; enterprise units often have a lower premium for the coverage level.

**Don't:**
- Choose coverage level before verifying APH accuracy — coverage level on a suppressed APH does not provide the intended protection.
- Accept T-yield substitutions without confirming that the actual year's production was not available; T-yields are typically lower than actual production in high-yielding environments.

## Edge cases / when the rule does NOT apply

Beginning farmers with fewer than 4 years of APH are in a limited APH situation; the options (T-yield substitution, catastrophic coverage, beginning farmer provisions) are different and should be reviewed with the agent. Specialty crops and some vegetable crops have Whole Farm Revenue Protection (WFRP) as the primary product rather than yield-based APH; the rule applies to the revenue-history accuracy instead.

## See also

- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns the insurance coverage economics and APH-to-coverage value model.
- [`../agents/agronomy-engagement-lead.md`](../agents/agronomy-engagement-lead.md) — flags APH accuracy as part of the farm risk management review.
- [`./weather-and-price-are-the-risk-hedge-the-controllable-plan-t.md`](./weather-and-price-are-the-risk-hedge-the-controllable-plan-t.md) — crop insurance is the primary weather risk management tool; APH accuracy is what makes it work.

## Provenance

USDA RMA (Risk Management Agency) publishes APH procedures and yield exclusion provisions; the emphasis on APH accuracy before coverage selection is standard in crop insurance consulting and farm risk management education.

---

_Last reviewed: 2026-06-05 by `claude`_
