# Subrogation Recovery Is a Claims Unit Revenue Line

**Status:** Pattern
**Domain:** P&C insurance — claims operations
**Applies to:** `insurance-pc`

---

## Why this exists

Subrogation — the carrier's right to pursue a third party for losses it paid on behalf of the insured — is a direct offset to the incurred loss ratio, but it is systematically under-managed in many claims operations. When subrogation is treated as a back-office afterthought rather than a front-line claims workflow step, recovery opportunities expire (statutes of limitations are hard deadlines), evidence is lost, and the net loss ratio is worse than the inherent risk profile requires. On a $100M loss portfolio, a 2-point improvement in net subrogation recovery rate is $2M in recovered losses — worth treating as a managed revenue line, not a collection hope.

## How to apply

**Subrogation identification — at first notice of loss:**

```
Every claim intake must answer:
[ ] Is there a potentially negligent third party? (auto: at-fault driver; property: contractor,
    product manufacturer, adjacent property owner; GL: contractual indemnitor)
[ ] Is there a contractual indemnification agreement in the insured's contracts?
[ ] Is the statute of limitations > 12 months from loss date? (if < 12 months, flag for
    immediate referral)
[ ] Is evidence preservation needed? (photos, physical evidence, EUO)
```

**Triage thresholds — route to dedicated subrogation unit vs. adjuster-managed:**

| Loss Amount | Liability Clarity | Recommended Handling |
|---|---|---|
| > $25k | Clear or probable | Refer to subrogation specialist immediately |
| > $25k | Disputed / unclear | Refer and flag — investigate liability concurrently with claim |
| $5k–$25k | Clear | Adjuster-managed with subrogation unit oversight |
| < $5k | Any | Adjuster discretion; automated demand letter programs appropriate |

**Key performance metrics for the subrogation unit:**

| Metric | Target | How Measured |
|---|---|---|
| Subrogation identification rate | ≥ 80% of eligible losses identified at FNOL | Claims system flag rate |
| Recovery rate ($ recovered / $ identified) | ≥ 35% [unverified — training knowledge; varies by line] | Ceded recovery / identified pipeline |
| Average cycle time (identification to collection) | [Benchmark by line — auto faster than property] | Claims system date fields |
| Statute of limitations violations | 0 — hard stop | Claims audit |

**Do:**
- Train front-line adjusters to identify subrogation potential at FNOL — recovery that isn't identified can't be pursued.
- Set a calendar reminder for statute of limitations on every open subrogation file; treat an SOL miss as a claims quality defect.
- Report subrogation recovery as a separate line in the monthly loss report — net loss ratio (after recovery) vs. gross loss ratio (before) should both appear.

**Don't:**
- Defer subrogation referral until the claim closes — time kills recovery options (evidence, witness memory, SOL).
- Treat small-dollar claims as too small to recover — an automated demand program can run $1k–$5k recoveries at near-zero marginal cost.
- Report only gross paid losses in the combined ratio without showing the subrogation recovery offset — it understates claims unit performance.

## Edge cases / when the rule does NOT apply

Workers' compensation subrogation operates under different state statutes (many require the insured to be made whole first before the carrier recovers) and is typically handled by a specialized WC recovery unit, not the P&C claims unit. Apply the identification discipline but route to the appropriate specialist for WC recovery.

## See also
- [`../agents/claims-specialist.md`](../agents/claims-specialist.md) — owns claims operations metrics including subrogation recovery rate.
- [`../agents/actuarial-pricing-analyst.md`](../agents/actuarial-pricing-analyst.md) — includes net subrogation recovery in loss ratio decomposition.

## Provenance

Codifies standard P&C claims operations practice; recovery rate benchmarks are [unverified — training knowledge] and vary by line, liability jurisdiction, and claims volume mix.

---

_Last reviewed: 2026-06-05 by `claude`_
