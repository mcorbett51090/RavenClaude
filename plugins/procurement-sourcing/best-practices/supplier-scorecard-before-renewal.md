# Run a Supplier Scorecard Before Every Renewal

**Status:** Absolute rule
**Domain:** Supplier management / contract renewal
**Applies to:** `procurement-sourcing`

---

## Why this exists

Renewing a supplier contract without a scorecard means renewing on the basis of inertia. The incumbent retains the business not because they have earned it but because switching is inconvenient. A scorecard-before-renewal discipline does two things: it gives procurement the data to negotiate from a position of knowledge ("your on-time delivery was 87% against a 95% SLA — what's your plan?") and it surfaces whether the incumbent is still the right supplier for the category at its current Kraljic position. A supplier that was once strategic may now be leverage — and should be tested against the market.

## How to apply

Issue and score the supplier scorecard at least 90 days before the renewal decision date — early enough to act on the findings.

```
Supplier Scorecard — Minimum Fields (quarterly or at renewal)
──────────────────────────────────────────────────────────────
PERFORMANCE METRICS (weight as appropriate to category)
Metric                  | SLA / Target    | Actual  | Score (1–4)
Quality / defect rate   | < X%            | Y%      |
On-time delivery        | ≥ X%            | Y%      |
Invoice accuracy        | ≥ X%            | Y%      |
Issue resolution time   | ≤ X days        | Y days  |
Responsiveness          | <qualitative>   |         |

FINANCIAL HEALTH (at renewal)
  Current credit-rating indicator or Dun & Bradstreet score
  Any known financial distress signals (media, industry)

INNOVATION / VALUE-ADD
  New capabilities or cost-reduction ideas proposed in period: Yes / No

OVERALL SCORE   [Weighted average]
RENEWAL DECISION
  Score ≥ 3.5 → Renew; negotiate improvements on weak metrics
  Score 2.5–3.4 → Conditional renewal; improvement plan required with milestones
  Score < 2.5 → Market-test; do not renew without competitive alternative

STAKEHOLDER SIGN-OFF   [Business owner + Procurement Lead + date]
```

**Do:**
- Distribute the scorecard to the business stakeholders who work with the supplier day-to-day — procurement's view of supplier performance is incomplete without it.
- Share the scorecard with the supplier before the renewal discussion; surprises in the meeting produce defensiveness, not problem-solving.
- For strategic suppliers, use a more detailed joint-business-review format, not just the scorecard.

**Don't:**
- Run the scorecard as a formality if you have already decided to renew — the discipline only works if the findings can change the outcome.
- Tie 100% of the score to price — price is one input; a supplier who delivers below SLA at a low price is not a good supplier.
- Skip the financial-health check on large, single-source suppliers; a supplier failure during a critical production period is a supply-continuity crisis.

## Edge cases / when the rule does NOT apply

- **Short-term or transactional contracts** (one-time purchase, project-based) — no renewal cycle; apply the scorecard concept at project close as a supplier-qualification record for future use.
- **Government-mandated or sole-source suppliers** where switching is not legally possible — the scorecard still informs the performance-improvement dialogue, even if it cannot drive a competitive event.

## See also

- [`../agents/supplier-risk-specialist.md`](../agents/supplier-risk-specialist.md) — owns supplier financial and operational risk assessment used in the scorecard.
- [`./supplier-risk-is-a-portfolio-not-a-checkbox.md`](./supplier-risk-is-a-portfolio-not-a-checkbox.md) — the scorecard is the per-supplier view; the portfolio rule is the aggregate view across the supply base.

## Provenance

Codifies the supplier-risk-specialist and category-strategist joint discipline from the procurement-sourcing plugin's CLAUDE.md §3 #4 ("supplier risk is a portfolio, not a checkbox") and §3 #3 (realized savings vs. negotiated). The scorecard structure and renewal decision tiers reflect standard SRM (Supplier Relationship Management) practice.

---

_Last reviewed: 2026-06-05 by `claude`_
