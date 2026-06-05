# Lab shopping is a licensing and audit risk — document testing history per batch

**Status:** Absolute rule
**Domain:** Cannabis operations / quality / compliance
**Applies to:** `cannabis-operations`

---

## Why this exists

Lab shopping — submitting a failed sample to a second accredited laboratory in hopes of a passing result — is prohibited in every mature cannabis regulatory framework, and regulators track it through the track-and-trace system by requiring failed test results to be logged before a re-test can be authorized. An operator whose batch records show a failed test with no corresponding retesting approval, or a passed test at a second lab with no documented first-lab failure, has created a compliance event that can result in license suspension or revocation. Separately, a cost model that excludes failed-test batches from production economics systematically understates the true cost of goods.

## How to apply

Maintain a test-history log as part of every batch cost record:

```
Test history — Batch ID: ____ — Strain: ____ — Harvest date: ____

Test 1
  Lab name:                ____  [licensed + accredited in state: Y/N]
  Sample ID:               ____
  Date submitted:          ____
  Date result received:    ____
  Result:                  Pass / Fail
  Failure reason (if fail):____
  State re-test approval:  ____  [required before re-submission]

Test 2 (only if re-test approved)
  Lab name:                ____
  Sample ID:               ____
  Date submitted:          ____
  Date result received:    ____
  Result:                  Pass / Fail
  Disposition if fail:     Remediate / Destroy / Convert (state-specific)
```

Log all test results — including failures — in the state track-and-trace system at the time of receipt, before any disposition decision.

**Do:**
- Verify the testing laboratory is currently licensed and accredited in the applicable state before submitting a sample — accreditation lapses.
- Log failed results immediately; the regulatory window for logging is typically narrow (24-72 hours depending on state).
- Include test-fail cost and re-test cost in the batch cost record — they are real production costs, not accounting noise.

**Don't:**
- Submit a second sample without first receiving a state-authorized re-test approval — the order matters for compliance.
- Remediate a failed batch (re-extraction, blending) without confirming the state permits that disposition for the specific failure type; pesticide failures typically require destruction, not remediation.
- Exclude failed-test batches from the production yield and cost analysis — a 5% fail rate understated in the model produces a COGS that overstates profitability.

## Edge cases / when the rule does NOT apply

- States with a provisional/conditional re-test protocol (some states allow a second sample from the same harvest lot without a formal re-test authorization) — apply the state-specific rule, but still log both results.
- Potency-only re-tests (not safety) may have different procedural rules in some states; verify.

## See also

- [`../agents/seed-to-sale-compliance-specialist.md`](../agents/seed-to-sale-compliance-specialist.md) — owns the track-and-trace logging for test results.
- [`../agents/cannabis-finance-analyst.md`](../agents/cannabis-finance-analyst.md) — incorporates test-fail rates into the production cost model.
- [`./testing-and-remediation-are-a-yield-and-cost-reality.md`](./testing-and-remediation-are-a-yield-and-cost-reality.md) — the house opinion this rule operationalizes.

## Provenance

Derived from state cannabis laboratory testing regulations, track-and-trace testing logging requirements, and compliance enforcement patterns. `[unverified — training knowledge]` — cite the applicable state's testing regulations and verify accreditation requirements before advising a client.

---

_Last reviewed: 2026-06-05 by `claude`_
