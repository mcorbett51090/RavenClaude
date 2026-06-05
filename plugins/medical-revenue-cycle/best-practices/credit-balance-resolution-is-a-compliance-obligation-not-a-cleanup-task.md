# Credit Balance Resolution Is a Compliance Obligation, Not a Cleanup Task

**Status:** Absolute rule
**Domain:** Medical revenue cycle — compliance, billing operations
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

A credit balance — a negative balance on a patient or payer account, meaning the provider has collected more than it is owed — is not surplus revenue. It is an overpayment that belongs to the payer or patient and must be refunded. For Medicare and Medicaid, unresolved credit balances that represent overpayments are subject to the 60-day repayment rule under the False Claims Act: once a provider has identified or "should have identified" an overpayment, they have 60 days to report and return it or face FCA exposure. [unverified — training knowledge] Credit balance reports are routinely reviewed in payer audits and government program audits; a backlog of unresolved credits signals either weak controls or intentional retention, neither of which is defensible.

## How to apply

**Credit balance categories and their resolution timelines:**

| Credit Type | Cause | Required Action | Resolution Deadline |
|---|---|---|---|
| Medicare / Medicaid overpayment | Duplicate payment, billing error, retroactive rate correction | Report and refund to CMS / state Medicaid | 60 calendar days from identification (FCA deadline) |
| Commercial payer overpayment | Duplicate payment, coordination of benefits error | Refund to payer | Per contract terms; typically 60–90 days |
| Patient overpayment | Estimated co-pay > actual; insurance paid more than expected | Refund to patient (check) or apply to future balance per patient preference | 30–60 days from identification (state law varies) |
| Coordination of benefits (COB) | Primary and secondary both paid in full | Return to lower-priority payer | Per contract; resolve COB first then issue refund |

**Minimum workflow controls:**

```
[ ] Credit balance report runs automatically weekly from the PM/billing system
[ ] All credits > $[threshold — e.g., $25] are assigned to a named reviewer
[ ] Medicare/Medicaid credits are flagged immediately for compliance review
    regardless of dollar amount
[ ] Resolution date is recorded for each credit
[ ] Credits unresolved > 30 days escalate to RCM leadership
[ ] Monthly summary reported to CFO / compliance officer: # open credits,
    $ value, age distribution, % resolved in period
```

**KPIs for credit balance management:**

| Metric | Target | How Measured |
|---|---|---|
| Credit balance aging > 60 days (Medicare / Medicaid) | 0 — hard stop | AR system aging report |
| Credit balance aging > 90 days (all payers) | < 5% of total credit volume | AR aging |
| Average days to resolution | ≤ 30 days | Date opened vs. date resolved |
| Credit balance as % of total A/R | < 1% | Monthly balance report |

**Do:**
- Run a credit balance report on the same cadence as the A/R aging report — they are both cash-control documents.
- Identify the underlying cause of every credit balance above $[threshold], not just resolve it — duplicate payments and COB errors repeat without a root-cause fix.
- Document the resolution (refund date, check number, payer confirmation) in the account notes.

**Don't:**
- Allow Medicare or Medicaid credit balances to age past 60 days without resolution — this is the FCA deadline, not a performance target.
- Apply a Medicare overpayment to a future claim as an offset without following the formal repayment process — this is not a compliant resolution.
- Treat the credit balance report as a low-priority monthly cleanup; it is a real-time compliance control.

## Edge cases / when the rule does NOT apply

Small patient overpayments below a de minimis threshold (e.g., < $5) may be handled per practice policy (waived with patient consent documented) in some states. Confirm state law and practice policy before applying a de minimis threshold; never apply it to payer credits.

## See also
- [`../agents/rcm-analytics-analyst.md`](../agents/rcm-analytics-analyst.md) — tracks credit balance metrics in the RCM scorecard.
- [`../agents/denials-management-specialist.md`](../agents/denials-management-specialist.md) — investigates root causes including duplicate payments that generate credit balances.

## Provenance

Codifies False Claims Act 60-day repayment obligation and standard healthcare RCM compliance practice; legal citations are [unverified — training knowledge] and must be confirmed against current CMS guidance and state Medicaid rules before acting.

---

_Last reviewed: 2026-06-05 by `claude`_
