# Accounts Receivable Over 90 Days Is Unrecoverable Revenue

**Status:** Primary diagnostic
**Domain:** Revenue cycle / A/R management
**Applies to:** `dental-practice`

---

## Why this exists

Dental practice A/R aged beyond 90 days has dramatically lower recovery probability than current A/R. After 90 days, patient balances are often past the point where a standard statement cycle will collect them; insurance claim timely-filing windows have usually closed; and the cost of pursuing the balance via collections erodes the net recovery. A practice with a large over-90-day bucket is carrying phantom revenue — it appears on the books but will not cash. Worse, a growing over-90 bucket is almost always an upstream billing process problem (claims not filed, patient balances not billed, payment plans not followed up) that compounds monthly.

## How to apply

Segment the A/R report by aging bucket and payer type monthly. Act on the over-90 bucket immediately.

```
A/R aging diagnostic:
Healthy A/R profile (as % of total A/R):
  0–30 days:   ≥50% [unverified — training knowledge]
  31–60 days:  ≤25%
  61–90 days:  ≤15%
  >90 days:    ≤10% — if above this, the over-90 bucket requires immediate triage

Over-90 triage steps:
1. Segment by payer: insurance vs. patient balance
   - Insurance >90 days: check claim status; refile or appeal if not paid/denied
   - Patient balance >90 days: confirm statements were sent; flag for collections conversation

2. Timely-filing audit: 
   - Identify claims where the insurance timely-filing window has closed → write-off vs. appeal
   - Document the write-off decision and root cause to prevent recurrence

3. Collections decision criteria:
   - Balance > $200 + no payment in 90 days + patient not responding → refer to collections
   - Balance < $200 → internal write-off may be more cost-effective than collections referral
   - VIP or high-value patient → escalate to office manager before collections referral

4. Root cause fix (upstream):
   - Claims not filed → fix claims submission workflow or staffing
   - Patient statements not sent → fix billing cycle
   - Payment plans not followed up → implement auto-follow-up process
```

**Do:**
- Run the aging report segmented by insurance and patient balance — the two require different actions and have different recovery trajectories.
- Act on over-90 insurance claims within 5 business days of identifying them — every week of delay reduces recovery probability.
- Measure the over-90 bucket as a % of total A/R monthly; track the trend, not just the snapshot.

**Don't:**
- Use total A/R balance as the headline metric — it masks the age structure. A practice with $150k A/R that is 60% over-90 is in worse shape than one with $200k that is 5% over-90.
- Write off over-90 balances without documenting the root cause and fixing the upstream process.
- Conflate timely-filing-closed insurance balances with collectable insurance A/R — they must be separated before computing real A/R.

## Edge cases / when the rule does NOT apply

Practices offering formal in-house payment plans (e.g., 12-month 0% interest) will carry legitimate patient A/R beyond 90 days that is on-track. These must be tagged and excluded from the problem A/R bucket — but track them separately to ensure plan compliance.

## See also

- [`../agents/dental-rcm-specialist.md`](../agents/dental-rcm-specialist.md) — owns A/R management, collections ratio, and claims workflow.
- [`./collections-not-production-pay-the-bills.md`](./collections-not-production-pay-the-bills.md) — over-90 A/R is the most direct path from high production to low collections.

## Provenance

Standard dental RCM and practice finance management; grounded in ADA and MGMA dental practice benchmarks; A/R aging thresholds reflect standard dental billing operations guidance.

---

_Last reviewed: 2026-06-05 by `claude`_
