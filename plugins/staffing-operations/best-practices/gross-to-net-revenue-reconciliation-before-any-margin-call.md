# Reconcile Gross to Net Revenue Before Making a Margin Call

**Status:** Primary diagnostic
**Domain:** Staffing operations — Financial analytics
**Applies to:** `staffing-operations`

---

## Why this exists

Staffing firms commonly report "gross revenue" that includes passthrough items — housing stipends, per-diem allowances, travel reimbursements, compliance fees — that flow through the P&L but generate no spread. When gross revenue is used as the denominator in margin calculations without removing these passthroughs, the reported margin is structurally understated and the absolute spread is understated. A firm with $50M in gross revenue may have $12M in passthroughs, making the relevant revenue base for margin analysis $38M, not $50M. Two firms with the same spread-per-placement can show very different margin percentages if their passthrough ratios differ. Making a pricing recommendation, a competitive margin comparison, or a recruiter productivity calculation on unreconciled gross revenue produces the wrong diagnosis.

## How to apply

**The gross-to-net reconciliation:**

```
Gross Billed Revenue (all invoiced to clients)
  − Housing/travel stipends (IRS nontaxable; passed through to worker)
  − Per-diem / M&IE reimbursements (IRS nontaxable; passed through)
  − Direct travel reimbursements (pass-through; not a margin line)
  − Compliance / credentialing fees (if charged and fully offset)
  − Client-deducted VMS/MSP fees (if shown gross on invoice)
= Net Service Revenue (the spread-generating base)

Net Service Revenue
  − Direct worker cost (base pay + OT + burden stack)
= Gross Profit (spread)

Gross Profit ÷ Net Service Revenue = Gross Margin %
```

**Passthrough ratio check (run before any margin comparison):**

| Line | Amount ($) | % of Gross Revenue |
|---|---|---|
| Gross Billed Revenue | | 100% |
| Total passthroughs | | [X%] — flag if >20% |
| Net Service Revenue | | [100−X]% |
| Gross Profit (spread) | | [Y% of NSR] |

If passthroughs exceed 20% of gross revenue, the margin calculation on gross revenue is materially misleading. Restate before comparing to benchmarks or competitors.

**Cross-firm comparison discipline:**

When comparing margin to industry benchmarks or competitor estimates:
1. Confirm whether the benchmark is gross-revenue-based or net-service-revenue-based. SIA and most public-company filings use "revenue" that may or may not strip passthroughs — check the footnotes. Mark `[unverified — verify against source methodology]` if unsure.
2. Restate both firms' margins to the same basis before comparing.
3. State the restated basis explicitly in the deliverable: "GP margin on net service revenue, passthroughs excluded."

**Do:**
- Always define the revenue base in the margin metric: "Gross margin of 22% on net service revenue (passthroughs excluded)" — not just "22% margin."
- Pull the passthrough line items from payroll/billing reports, not from a summary P&L that may already net them — verify the netting treatment.
- Recalculate recruiter productivity (revenue per recruiter) on net service revenue, not gross, to avoid inflating per-recruiter metrics with non-spread activity.

**Don't:**
- Compare a travel-segment margin (high passthrough ratio) to a per-diem or direct-hire margin on a gross-revenue basis — the passthrough structures are different and the comparison is meaningless.
- Accept a client or internal report's stated "margin" without asking: "margin on gross revenue or net service revenue, and are stipends stripped?"
- Use gross revenue as the productivity denominator when measuring recruiter or desk performance — a recruiter doing exclusively travel-nurse placements with high housing stipends will appear more productive than a per-diem recruiter on a gross-revenue basis, even if spread-per-placement is identical.

## Edge cases / when the rule does NOT apply

- **Direct-hire and permanent placement fees:** there are typically no passthroughs; gross revenue and net service revenue are the same. The rule still applies in principle — confirm there are no reimbursement components in the fee structure before skipping the reconciliation.
- **Light industrial / general staffing with no stipends:** passthrough ratio is near zero; gross-to-net reconciliation adds no material adjustment. Still define the revenue basis in margin reporting for consistency.

## See also

- [`../agents/staffing-operations-analyst.md`](../agents/staffing-operations-analyst.md) — runs the reconciliation as part of margin diagnostics
- [`../agents/healthcare-staffing-specialist.md`](../agents/healthcare-staffing-specialist.md) — owns the passthrough mechanics for travel and per-diem placements
- [`./decompose-margin-before-calling-it-pricing.md`](./decompose-margin-before-calling-it-pricing.md) — the next-step rule after identifying a margin problem
- [`./burden-stack-decomposition-is-the-first-step-in-margin-analysis.md`](./burden-stack-decomposition-is-the-first-step-in-margin-analysis.md) — companion rule on the cost side

## Provenance

Codifies a standard practice in staffing-firm financial analysis: the distinction between gross billed revenue and net service revenue (also called "net revenue" or "service revenue" in staffing CFO parlance). The passthrough treatment is particularly material in travel healthcare, where housing and per-diem stipends can represent 15–30% of the gross bill rate. Grounded in the team's §3 #3 ("margin is bill-rate minus pay-rate minus burden — name all three") and the knowledge bank's spread-mechanics documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
