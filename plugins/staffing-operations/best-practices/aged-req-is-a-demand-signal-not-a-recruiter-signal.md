# Aged Requisitions Are a Demand Signal, Not a Recruiter Signal

**Status:** Primary diagnostic
**Domain:** Staffing operations — Funnel diagnostics
**Applies to:** `staffing-operations`

---

## Why this exists

When a requisition sits unfilled for an extended period, the instinctive diagnosis is recruiter performance. In practice, req aging is more reliably a signal about the demand side of the order: bill rate below market, eligibility criteria that eliminate the available supply pool, a facility relationship problem, or a req that was never genuinely workable in the first place. Attributing aged reqs to recruiter underperformance without checking order quality first leads to performance management that does not fix the fill problem and demoralizes recruiters who were given unworkable orders. The house opinion §3 #4 ("diagnose the funnel before blaming the recruiter") and the order-quality-index rule are the upstream principles; this rule operationalizes them specifically for req aging.

## How to apply

**Req aging threshold definitions (calibrate to your segment):**

| Age Band | Classification | First diagnostic step |
|---|---|---|
| 0–14 days | Active | Normal monitoring |
| 15–30 days | Watch | Check submittal count and reason-for-no-hire |
| 31–60 days | Aged | Run the order-quality index before any recruiter action |
| 61–90 days | Stale | Escalate to client services — likely a demand problem |
| 90+ days | Zombie | Review for removal or reclassification; rarely fillable at terms offered |

**The aging diagnostic before any recruiter action:**

```
For each aged req (≥31 days unfilled):
1. Bill rate check — is the bill rate at or above current market for that specialty/geography?
   (Source: internal recent placements + market intel — cite source + date)
2. Submit-to-offer ratio on this req — has it received submittals? Were they rejected?
   - If no submittals: supply problem or unattractive terms
   - If submittals but rejections: client-side problem (standards, responsiveness) or poor fit
3. Similar req comparison — are comparable reqs at the same bill rate filling elsewhere?
   - Fills on similar: this req may have client-relationship or facility-specific issue
   - No fills on similar: market supply problem; bill rate intervention needed
4. Req workability screen — minimum years experience, specialty restrictions,
   geography constraints — does the eligible candidate population actually exist
   at this bill rate in this market?
```

**Do:**
- Report aged-req counts and their distribution (age band breakdown) as a demand-health metric, separate from recruiter productivity metrics.
- When presenting an aged-req list to a client, lead with the order-quality analysis — show the data that distinguishes supply-constrained reqs from client-caused reqs.
- Set a formal "zombie req" review cadence (e.g., monthly) to close or reclassify orders that have aged past 90 days with no submittals at terms — keeping them open inflates the denominator in fill rate and distorts all funnel metrics.
- Track the split: what % of aged reqs are attributable to below-market bill rates vs. supply scarcity vs. client responsiveness vs. recruiter latency.

**Don't:**
- Use aged-req count as a recruiter KPI without the order-quality index denominator — it conflates demand failure with recruiter performance.
- Close a req as "filled" to remove it from aging metrics when it was actually withdrawn or cancelled — reclassify it correctly so the demand-side signal is preserved.
- Allow zombie reqs to accumulate without review — they inflate open-order counts, make fill rate look artificially low, and make req-per-recruiter ratios meaningless.

## Edge cases / when the rule does NOT apply

- **High-velocity, low-credential roles** (general labor, clerical): aging thresholds should be much tighter (5–10 days to watch, 15–20 days to stale) because the supply pool is large and aging reflects execution lag, not market constraints.
- **Rare-specialty healthcare reqs** (pediatric sub-specialty, certain allied roles in rural markets): a 30-day aging is not a signal of a problem — it is the expected time-to-fill for genuinely supply-constrained roles. Calibrate the threshold to the specialty's baseline TTF.

## See also

- [`../agents/recruiting-funnel-strategist.md`](../agents/recruiting-funnel-strategist.md) — owns the funnel-level aging analysis
- [`../agents/staffing-operations-analyst.md`](../agents/staffing-operations-analyst.md) — builds the scorecard that surfaces aging by age band and segment
- [`./order-quality-index-before-recruiter-performance-review.md`](./order-quality-index-before-recruiter-performance-review.md) — the companion rule: always run the OQI before attributing low performance to the recruiter

## Provenance

Codifies the field practice of experienced staffing operations analysts: the first question on an aged req is "is this req fillable at these terms?" not "why hasn't the recruiter filled it?" Grounded in the team's §3 #4 ("diagnose the funnel before blaming the recruiter") and the order-quality-index rule.

---

_Last reviewed: 2026-06-05 by `claude`_
