# New Business Loss Ratio Is Not the Same as Renewal Loss Ratio

**Status:** Absolute rule
**Domain:** P&C insurance — underwriting analytics
**Applies to:** `insurance-pc`

---

## Why this exists

New business and renewal business are fundamentally different risk pools, and blending their loss ratios into a single portfolio number conceals the underwriting dynamics of each. New business carries adverse selection risk — the insured's history may be incomplete, and brokers bring new business when their prior carrier priced them out (often a signal, not a gift). Renewal business has been seasoned against the book's pricing and terms. A combined ratio that looks stable while new business is deteriorating and renewals are subsidizing it will eventually gap out when the renewal base ages into the new-business loss profile. Separate reporting is not optional on a growing book.

## How to apply

**Segmentation framework:**

| Segment | Definition | Typical LR differential vs. book |
|---|---|---|
| New business — first policy year | No prior history with this carrier; first year on risk | Often +5 to +15 LR points vs. renewal [unverified — training knowledge] |
| Renewal — 1 to 3 years on risk | Has been through at least one full renewal cycle | Typically matches or beats the book average |
| Renewal — 3+ years on risk | Seasoned account; carrier has full loss history | Often the best performers; watch for underpricing on loyalty |
| Internally rewritten | Policy restructured but same insured | Treat as renewal for loss history; apply new-business pricing discipline to changed coverage |

**How to report separately:**

```
Underwriting result by vintage — example table format:
| Vintage         | Earned Premium | Incurred Loss | Loss Ratio | Change YoY |
| New business    | $[X]           | $[X]          | [X]%       | [+/-X pp]  |
| Renewal 1–3 yr  | $[X]           | $[X]          | [X]%       | [+/-X pp]  |
| Renewal 3+ yr   | $[X]           | $[X]          | [X]%       | [+/-X pp]  |
| Total book      | $[X]           | $[X]          | [X]%       |            |
```

**Red flags to act on:**
- New business LR > Renewal LR by more than 10 points → tighten new business submission criteria.
- New business LR deteriorating while renewal LR holds → adverse selection in submissions or pricing model is lagging on new-business segments.
- Renewal LR rising faster than new business → prior-year underpricing is maturing into losses; re-rate the renewal book.

**Do:**
- Tag every policy with its new-business vs. renewal vintage at inception in the policy admin system.
- Report new vs. renewal loss ratio in every quarterly underwriting review.
- Apply a new-business load to pricing models in lines where the historical NB vs. renewal LR differential is empirically established.

**Don't:**
- Average new and renewal into a single loss ratio for a growing book — it is directionally misleading.
- Assume a clean new business loss ratio in year one means the new accounts are well-underwritten — development lag means year-one NB claims are often incomplete.
- Use broker submission volume as a substitute for underwriting quality metrics on new business.

## Edge cases / when the rule does NOT apply

Personal lines in highly commoditized markets (standard personal auto in competitive states) where policy year 1 vs. renewal distinction is embedded in rate filings may not need separate management reporting — the rate structure already carries the new-business load. Confirm the pricing model embeds the adjustment before omitting the separate reporting.

## See also
- [`../agents/actuarial-pricing-analyst.md`](../agents/actuarial-pricing-analyst.md) — decomposes the combined ratio by line, segment, and vintage.
- [`../agents/pc-underwriter.md`](../agents/pc-underwriter.md) — uses the NB/renewal split to evaluate submission strategy and rate adequacy.

## Provenance

Codifies standard P&C underwriting analytics discipline; LR differential estimates are [unverified — training knowledge] and vary materially by line of business, market cycle, and portfolio composition.

---

_Last reviewed: 2026-06-05 by `claude`_
