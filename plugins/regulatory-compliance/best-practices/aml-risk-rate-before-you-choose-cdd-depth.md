# Risk-rate the customer before you choose CDD depth — SDD, CDD, or EDD

**Status:** Absolute rule
**Domain:** AML / KYC — customer due diligence
**Applies to:** `regulatory-compliance`

---

## Why this exists

Due diligence depth is an **output of a risk rating**, not a starting assumption. The failure mode is choosing the depth first — "this is a corporate, run the full EDD pack" or "low-touch onboarding, light KYC" — and back-filling a rating to match. That inverts the logic regulators expect: a risk-based program rates the customer (product risk, geographic risk, delivery-channel risk, customer-type risk) on a reproducible model, and the rating *determines* whether simplified (SDD), standard (CDD), or enhanced (EDD) due diligence applies. A rating computed but not recorded, or recorded inconsistently, is the same defect as no rating — the examiner cannot reproduce the decision, so the decision did not happen.

## How to apply

Run the customer-risk-rating (CRR) model first; let the tier select the depth:

```
Inputs (weighted):  customer type · product/service risk · geographic risk · delivery channel
Output:             risk tier  ->  due-diligence depth
  Low (and a permitted SDD category) -> SDD  : reduced verification, documented basis for the reduction
  Standard                            -> CDD  : identity, beneficial ownership, source of funds, expected activity
  High (or EDD trigger present)       -> EDD  : independent verification + senior-management approval + recorded
                                                rationale-to-proceed + shorter refresh cadence
```

EDD triggers that force the high tier regardless of the base score: PEP, high-risk jurisdiction `[verify-at-build — FATF lists change]`, complex/opaque ownership, large unexplained cash, correspondent/nested relationships.

**Do:**
- Record the rating: inputs, weights, output tier, date — reproducible if re-run.
- Treat EDD as a *depth*, not a *document count*: independent verification + senior approval + a written rationale-to-proceed.
- Tie refresh cadence to the tier (higher risk refreshes more often), on a calendar, not "at next adverse event".

**Don't:**
- Pick the depth, then rationalize the rating to fit.
- Apply SDD without a documented basis that the customer sits in a permitted simplified category for that regime `[verify-at-build]`.
- Verify source of funds on a higher-risk file by the customer's own statement alone — corroborate independently.

## Edge cases / when the rule does NOT apply

- **SDD is not "no DD"** — it is reduced, and only where the regime permits it; the reduction itself needs a recorded basis.
- **A single EDD trigger overrides a low base score** — PEP status alone forces enhanced controls + senior approval even if every other input is low.
- **Legal-conclusion questions** ("is this structure lawful") route to counsel — the `Legal-advice gate:` flips. The rating and DD documentation continue.

## See also

- [`./edd-is-depth-not-document-count.md`](./edd-is-depth-not-document-count.md) — what "enhanced" actually adds.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: CDD vs EDD vs SDD by customer risk`.
- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — owns CRR models; "risk rating is a model, not a vibe".

## Provenance

Codifies the `aml-kyc-analyst` opinions "CDD is a posture, EDD is a depth" and "risk rating is a model, not a vibe" ([`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)) and house opinion #13 (risk quantified where possible) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
