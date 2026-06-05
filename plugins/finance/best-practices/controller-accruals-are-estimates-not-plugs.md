# Accruals Are Estimates, Not Plugs

**Status:** Absolute rule
**Domain:** Close / accrual accounting
**Applies to:** `finance`

---

## Why this exists

An accrual is an estimate of an obligation or revenue-earning event that has occurred but not yet been invoiced or paid. A plug is a number chosen to make a line item hit a target — a budget number, a prior-period balance, or an analyst's expectation. The two look identical in the journal entry, but they are epistemically opposite: an accrual is supported by a calculation or a business event; a plug is chosen to produce a desired outcome. Plugs create real accounting risk — they can inflate income or understate liabilities — and auditors are trained to find them by looking for round numbers, recurring exact-prior-period amounts, and accruals that consistently reverse to zero without matching invoices.

## How to apply

Every accrual entry must be supported by a documented calculation before the journal entry is posted.

```
Accrual Documentation — Required Fields
────────────────────────────────────────────────
Accrual name / account:   <e.g., Accrued bonus — Q4 2025>
Period:                   <Month / quarter being accrued>
Calculation basis:        <e.g., "Estimated annual bonus pool × Q4 pro-rata weight (25%)
                           per the 2025 bonus plan approved by the Compensation Committee
                           on 2025-03-15">
Supporting data:          <Source: HR system headcount report, dated 2025-12-28;
                           bonus-pool estimate per CFO guidance memo, 2025-11-30>
Amount:                   $XXX,XXX
Prior-period comparable:  $XXX,XXX  (explain material difference if any)
Reversal entry:           Yes / No — if yes, date of automatic reversal
Preparer:                 <Name>  Date: <YYYY-MM-DD>
Reviewer:                 <Name>  Date: <YYYY-MM-DD>
```

**Do:**
- Support every recurring accrual with the same documentation structure each period — the prior-period comparative is a built-in reasonableness check.
- If an accrual amount changes materially from the prior period, document the cause in the memo field, not just the new number.
- Post the reversing entry at the same time as the accrual, with a future date — don't rely on a manual reversal reminder.
- For provisions under ASC 450 (contingent liabilities), document the probability tier (probable / reasonably possible / remote) and cite the assessment.

**Don't:**
- Post a round-number accrual without a calculation that arrives at that round number.
- Adjust an accrual to hit a budget or prior-period balance without a business reason.
- Leave the accrual at the same amount for more than two consecutive periods without re-validating the calculation basis.
- Rely on the CFO's verbal guidance as the sole documentation — a memo or email is the minimum written record.

## Edge cases / when the rule does NOT apply

- **ASC 450 contingency where a range estimate is the best achievable precision** — document the range and the basis for the point chosen (typically the minimum of the range or the most likely outcome); the requirement for documentation is not waived, only the precision changes.
- **Accruals below the materiality threshold** where the calculation effort would exceed the risk — still document the threshold and a brief basis note; the formal calculation template is not required below the threshold.

## See also

- [`../agents/controller.md`](../agents/controller.md) — owns the accrual close process and the journal-entry memo requirement.
- [`./controller-every-journal-entry-carries-a-memo-and-reviewer.md`](./controller-every-journal-entry-carries-a-memo-and-reviewer.md) — the upstream rule; the accrual documentation described here is the memo that JE rule requires.

## Provenance

Codifies the controller's accrual discipline from the finance plugin's knowledge file `knowledge/accrual-and-cutoff-discipline.md` and house opinion #6 (audit trail in every workpaper). The ASC 450 probability taxonomy and the round-number plug detection framing reflect standard public-accounting audit-planning practice.

---

_Last reviewed: 2026-06-05 by `claude`_
