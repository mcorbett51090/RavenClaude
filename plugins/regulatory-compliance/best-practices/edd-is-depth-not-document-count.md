# EDD adds verification depth, senior approval, and a recorded rationale — not just more documents

**Status:** Absolute rule
**Domain:** AML / KYC — enhanced due diligence
**Applies to:** `regulatory-compliance`

---

## Why this exists

The most common EDD failure is treating "enhanced" as "more documents". A file gets a thicker folder — extra passport copies, more utility bills — but none of the three things that actually make due diligence *enhanced*: independent verification (a source other than the customer's own attestation), senior-management approval to proceed, and a written rationale that records *why* the firm is comfortable taking the relationship on despite the elevated risk. Without those, the firm has done standard CDD twice, not EDD once. An examiner reads the file looking for the approval and the rationale; a stack of customer-supplied documents is not a substitute for either.

## How to apply

When a file is rated high or an EDD trigger fires, the EDD package must add all three:

```
1. Independent verification   source of wealth / source of funds corroborated by a source OTHER than
                              the customer (registry, audited accounts, reputable third-party data)
2. Senior-management approval named approver, date, and the decision to onboard/retain on record
3. Rationale-to-proceed       written: why the residual risk is acceptable given the controls applied
4. Enhanced ongoing monitoring shorter refresh cadence + tighter transaction-monitoring thresholds
```

**Do:**
- Name the senior approver and capture the approval in writing before the relationship goes live.
- Corroborate source of wealth/funds independently on every higher-risk file.
- Record the rationale-to-proceed in the customer's own words-of-decision — the *why now, why acceptable*.

**Don't:**
- Equate "we collected more documents" with EDD — count the three enhancements, not the page count.
- Let the relationship manager who owns the revenue be the sole approver — escalate to independent senior management.
- Treat a PEP as automatic decline — PEP means enhanced controls + senior approval + ongoing monitoring, not "no".

## Edge cases / when the rule does NOT apply

- **PEP that is also low on every other axis** — still EDD: PEP status forces the senior-approval + ongoing-monitoring elements even where source-of-funds risk is modest.
- **Existing customer crossing into a higher-risk product** — EDD applies at the trigger event, not only at onboarding; reflect the new product risk in the CRR and re-run.
- **Legal-opinion gate** — whether a specific relationship is permissible as a matter of law routes to counsel; the EDD documentation continues regardless.

## See also

- [`./aml-risk-rate-before-you-choose-cdd-depth.md`](./aml-risk-rate-before-you-choose-cdd-depth.md) — how the tier that triggers EDD is set.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: CDD vs EDD vs SDD by customer risk`.
- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — "EDD doesn't just add documents — it adds independent verification, senior-management approval, and a *recorded* rationale".

## Provenance

Codifies the `aml-kyc-analyst` opinion "EDD is a depth" and the anti-pattern "EDD applied as 'more documents' without independent verification or senior approval" ([`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)), and the §8 `kyc-edd-review` skill (SoW vs SoF, EDD triggers, sign-off chain) in [`../CLAUDE.md`](../CLAUDE.md).

---

_Last reviewed: 2026-05-30 by `claude`_
