# Rate Adequacy Testing Runs on Loss Trend, Not Historical Rate Level

**Status:** Absolute rule
**Domain:** Underwriting / pricing
**Applies to:** `insurance-pc`

---

## Why this exists

Rate adequacy analysis that compares current rate to historical rate (or last year's rate) tells you whether you charged more or less than last year — not whether today's rate covers today's expected loss. Loss cost trends — driven by social inflation in liability lines, medical-cost inflation in workers' comp, and property-replacement-cost escalation — move faster than rate in hard market transitions, meaning a carrier that took 6% rate on top of last year's 6% rate may still be losing ground if loss trend is running at 10%. An adequacy test that does not anchor on the current loss trend is measuring rate change, not rate adequacy.

## How to apply

Build the rate adequacy test off a trended and developed loss ratio, not off nominal premium-to-rate comparisons.

```
Rate Adequacy Test — Required Inputs
──────────────────────────────────────────────────────
1. CURRENT RATE LEVEL
   Most recent filed rate or actuarially calculated rate (not just booked premium)

2. TARGET LOSS RATIO
   Loss ratio needed to hit the combined-ratio target given the expense ratio:
   Target Loss Ratio = 1 – Expense Ratio – Target Profit Load
   e.g., 1.00 – 0.35 – 0.05 = 0.60 (60%)

3. INDICATED LOSS RATIO
   Ultimate loss ratio from the trended, developed loss triangle (not raw paid):
   - Apply loss development factors (LDFs) to get ultimate losses
   - Apply loss trend factors for the trend-from and trend-to periods
   - Divide by earned premium at current rate level

4. RATE ADEQUACY INDICATION
   Indicated Rate Change = (Indicated Loss Ratio / Target Loss Ratio) – 1
   e.g., (0.67 / 0.60) – 1 = +11.7% needed

5. CREDIBILITY CHECK
   Apply credibility weighting to your own data vs. industry data when
   experience is thin (fewer than ~500 earned exposures for a given segment).
```

**Do:**
- State the trend assumption explicitly: source, period, and whether it is all-in or split by frequency and severity.
- Show the calculation on a per-unit-of-exposure basis (e.g., per $1,000 insured value for property) to isolate pure loss cost from exposure changes.
- Run the adequacy test separately by line of business — an aggregate result for a mixed book masks cross-subsidization.

**Don't:**
- Use nominal rate change (this year's rate vs. last year's rate) as a proxy for adequacy; it answers the wrong question.
- Apply an industry loss trend to a book that is materially different from industry (e.g., a preferred-risk segment vs. standard market).
- Present a single-point adequacy indication without a sensitivity range on the trend assumption — trend is the most uncertain input.

## Edge cases / when the rule does NOT apply

- **Manuscript / bespoke commercial lines** where there is no credible loss triangle — the adequacy test relies more heavily on exposure-based pricing (should-cost build-up) than triangle development; document the methodology shift.
- **First-year new programs** with no loss history — use industry data with explicit credibility weighting; the adequacy test still applies but is anchored on external benchmarks.

## See also

- [`../agents/actuarial-pricing-analyst.md`](../agents/actuarial-pricing-analyst.md) — owns loss-triangle development, trend selection, and the actuarial adequacy indication.
- [`./underwrite-to-the-loss-ratio-not-the-competitors-rate.md`](./underwrite-to-the-loss-ratio-not-the-competitors-rate.md) — the companion house opinion that gives the loss-ratio target its primacy.

## Provenance

Codifies the actuarial-pricing-analyst's rate adequacy methodology from the insurance-pc plugin's CLAUDE.md §3 #2 (underwrite to the loss ratio, not the competitor's rate) and §3 #3 (separate frequency from severity). The indicated-rate-change formula and trended/developed loss ratio approach are standard casualty actuarial practice (CAS study materials, PCAS).

---

_Last reviewed: 2026-06-05 by `claude`_
