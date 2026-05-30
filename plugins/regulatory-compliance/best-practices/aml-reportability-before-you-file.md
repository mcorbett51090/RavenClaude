# Decide reportability before you draft — suspicion-based, threshold-based, or no report

**Status:** Primary diagnostic
**Domain:** AML / KYC — reporting obligations
**Applies to:** `regulatory-compliance`

---

## Why this exists

"Reportable" is not one thing. A suspicion-based report (SAR/STR) and a threshold-based report (e.g. a currency/cash-transaction report over a set amount) are different obligations with different triggers, different forms, and different consequences for getting it wrong. The failure modes are symmetric: filing a SAR for a transaction that is merely *large* (a threshold report's job) while missing the actual suspicion, or treating a clear suspicion as "just a big transaction, no narrative needed". Deciding the *category* first — before drafting anything — stops the analyst from reaching for the wrong instrument. Both categories also require the firm to document a *no-report* decision when the threshold isn't met, so the reasoning survives an exam.

## How to apply

Classify the obligation before drafting:

```
Is there articulable SUSPICION (typology you can name)?        -> SAR/STR (suspicion-based)
   ...AND it also crosses a reporting threshold?               -> SAR/STR AND threshold report (both)
Crosses a value/cash THRESHOLD but no suspicion?               -> threshold report only  [verify-at-build: amount]
Neither?                                                       -> no report; DOCUMENT the no-file rationale
```

Thresholds and the exact report families are **jurisdiction-specific** — confirm the regime's current amounts and forms before relying on a number `[verify-at-build]`.

**Do:**
- Name the category first; then pick the form and draft.
- File *both* when a transaction is both suspicious and over a threshold — they are not mutually exclusive.
- Record the no-report decision and its basis when nothing fires.

**Don't:**
- Substitute a SAR for a threshold report (or vice versa) — they answer different obligations.
- Treat "large" as "suspicious" by default — size is one indicator, not a typology.
- Let a continuing pattern go without a continuing-activity report once a SAR has been filed.

## Edge cases / when the rule does NOT apply

- **Structuring to avoid a threshold** is itself suspicious — sub-threshold activity designed to dodge a report flips you into the suspicion-based branch.
- **Jurisdiction sets the menu** — the available report types and thresholds differ by regime; route Bermuda specifics to `bermuda-insurance-specialist` (POCA / AMLR) and US specifics to the BSA family `[verify-at-build]`.
- **Legal-opinion gate** — whether a disclosure obligation is legally triggered in an edge case routes to counsel; the operational reportability triage continues.

## See also

- [`./aml-sar-narrative-answers-why.md`](./aml-sar-narrative-answers-why.md) — drafting the narrative once the SAR branch is chosen.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: Is this reportable — SAR, threshold report, or none`.
- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — SAR/STR drafting and transaction-monitoring disposition.

## Provenance

Codifies the `aml-kyc-analyst` surface area (SAR/STR drafting, threshold/recordkeeping obligations) and anti-pattern "SAR continuing-activity reports never filed for a known continuing pattern" ([`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)), plus house opinion #6 (default to written — including no-file decisions) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
