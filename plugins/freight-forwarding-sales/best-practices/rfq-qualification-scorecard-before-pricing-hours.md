# RFQ Qualification Scorecard Before Pricing Hours

**Status:** Absolute rule
**Domain:** Freight-forwarding sales
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

Not every RFQ is worth bidding. A large tender from a shipper with a deeply-entrenched incumbent, an unrealistic volume estimate, lanes outside your network, and a procurement team that has set price as the only evaluation criterion will consume 20 hours of pricing work for a 5% win probability. Running a qualification scorecard before committing to the bid takes 15 minutes and either confirms the bid is worth doing or returns the week to winnable business. Chasing every RFQ regardless of fit is the most common time-wasting pattern in freight sales.

## How to apply

Score every RFQ or tender on five dimensions before starting any pricing work:

```
RFQ Qualification Scorecard
─────────────────────────────
RFQ / tender:  ________________
Date received:  ________________
Submission deadline:  ________________

Dimension              | Score 1-5 | Notes
───────────────────────|-----------|──────────────────────────────
Lane/mode fit          |           | Are these lanes in our network? Are we competitive?
Volume reality         |           | Is the stated volume real and material? Prior ship data?
Relationship / contact |           | Do we have a contact at decision level, or are we a cold bid?
Win criteria clarity   |           | Are evaluation criteria stated, or is it a pure price-check?
Incumbent strength     |           | Is there an incumbent? Can we displace them with value?
───────────────────────|-----------|──────────────────────────────
Total score (max 25):  |           |

Decision rule:
  Score ≥ 18: Bid — invest full pricing hours + value narrative
  Score 12–17: Conditional bid — bid only if we can quickly address the low-score dimension
  Score < 12: Decline — polite, relationship-preserving no-bid letter

Recommended action:  [ ] Bid  [ ] Conditional  [ ] Decline
Decision rationale (1–2 sentences):  ________________
```

**Do:**
- Complete the scorecard the same day the RFQ arrives — pre-deadline decisions protect the week.
- Score "volume reality" conservatively; first-time RFQs routinely overstate volume by 30–50%.
- Document the no-bid decision and send a brief, professional declination — it keeps the relationship open for the next round.

**Don't:**
- Skip the scorecard because the shipper is a well-known brand — brand recognition does not predict win probability.
- Bid a conditional RFQ without first addressing the specific low-score dimension (e.g., call to understand evaluation criteria before pricing).
- Let the deadline drive the bid decision — "we might as well try" bids on low-score RFQs waste pricing capacity on un-winnable work.

## Edge cases / when the rule does NOT apply

Existing account renewals or re-bids where the forwarder is the incumbent are a different category — the bid/no-bid decision for an incumbent is almost always "bid," but the strategy is retention-focused rather than new-win-focused. Use the `qbr-account-planning` skill for incumbent re-bid strategy.

## See also

- [`../agents/rfq-tender-strategist.md`](../agents/rfq-tender-strategist.md) — owns the full RFQ qualification and response workflow.
- [`./discount-is-the-last-lever-not-the-first.md`](./discount-is-the-last-lever-not-the-first.md) — the companion rule on rate discipline during the bid response.

## Provenance

Codifies CLAUDE.md §3 #4 (qualify before you quote) with a structured scorecard instrument. The five-dimension qualification framework is consistent with standard B2B sales qualification methodology (MEDDIC, BANT) adapted to the freight-forwarding RFQ context [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
