# New Client Acquisition Cost Must Be Tracked Against Lifetime Value

**Status:** Pattern
**Domain:** Veterinary practice / growth management
**Applies to:** `veterinary-practice`

---

## Why this exists

Most veterinary practices spend marketing dollars without knowing what they cost per new client acquired, and without knowing what a new client is worth over a lifetime of care. Without both numbers, marketing spend decisions are blind: a $2,000/month Google Ads budget that brings in 20 new clients at $100 each looks expensive until the analysis shows that those clients have a 5-year expected revenue of $1,200–$2,400 each. Conversely, a "free" word-of-mouth strategy looks costless until the practice owner prices in the time spent on community events. The acquisition-cost-to-lifetime-value (CAC:LTV) ratio is the financial discipline that separates practices spending marketing dollars that compound from those spending money that doesn't return.

## How to apply

Calculate CAC and LTV quarterly and use the ratio to allocate the marketing budget:

```
Client Acquisition Cost (CAC) Calculation — [Practice] [Quarter]
─────────────────────────────────────────────────────────────────
Total marketing spend (quarter):          $___
  Paid digital (Google/Meta):             $___
  Print / direct mail:                    $___
  Community events / sponsorships:        $___
  Referral program:                       $___
  Practice owner / staff time (est.):     $___  (hrs × loaded hourly rate)

New clients acquired (quarter, from PIMS): ___
  New clients from digital:               ___
  New clients from referral:              ___
  New clients from walk-in / unknown:     ___

CAC (total):          $___/new client = total spend ÷ new clients
CAC by channel:
  Digital:            $___  (digital spend ÷ digital-attributed new clients)
  Referral program:   $___  (referral incentive cost ÷ referred new clients)
```

```
Client Lifetime Value (LTV) Calculation — [Practice]
──────────────────────────────────────────────────────
Data source: PIMS cohort analysis — clients acquired [year] through [year]

Average annual revenue per active client:  $___  (from PIMS: total revenue ÷ active clients)
Average client retention rate (annual):    ___%  (active clients this year ÷ prior year)
Average client lifespan (years):           ___ = 1 ÷ (1 − retention rate)

LTV (simple):          $___  = annual revenue × avg lifespan
LTV (discounted at ___% discount rate): $___

CAC:LTV ratio:  ___  (target: ≥ 1:3 — $1 of CAC generates $3+ of LTV)
Payback period: ___ months = CAC ÷ (annual revenue per client ÷ 12)
```

**Do:**
- Pull new-client count from the PIMS by acquisition source (use client intake form or referral source field) — without source attribution, CAC cannot be calculated by channel.
- Review CAC:LTV ratio quarterly, not annually — a deteriorating ratio in Q2 (high ad spend, lower new-client volume in a slow season) can be corrected before year-end.
- Include practice owner and staff time in the marketing cost; "free" community marketing has a time cost that is real and should be valued.
- Use the LTV calculation to justify retention investments — a wellness plan program that costs $5,000/year to administer but improves the retention rate from 55% to 65% is worth approximately $[calculate from LTV formula] in additional LTV per new client acquired.

**Don't:**
- Treat new-client count as the sole marketing metric without pairing it with acquisition cost — adding clients at a CAC:LTV ratio below 1:1 is growth that destroys value.
- Use first-year revenue as a proxy for LTV — a new client's first-year spend is typically below average (new-client wellness exam, not yet established for ongoing care); use the 3–5 year average revenue cohort from PIMS.
- Compare CAC across practices without adjusting for market size and competition — a rural practice with few competitors has naturally low CAC; a suburban practice competing with corporate chains has structurally higher CAC and needs a corresponding LTV to justify the spend.

## Edge cases / when the rule does NOT apply

Emergency and specialty referral practices do not acquire clients through traditional marketing — their "clients" are referral DVMs, not pet owners, and the relationship economics are entirely different. For those practices, the equivalent metric is referral-DVM retention rate and referral revenue per referring practice, not individual client LTV.

## See also
- [`../agents/vet-practice-lead.md`](../agents/vet-practice-lead.md) — owns the growth strategy and marketing budget allocation.
- [`../agents/vet-finance-analyst.md`](../agents/vet-finance-analyst.md) — builds the LTV model and tracks CAC by channel.
- [`../knowledge/vet-practice-economics.md`](../knowledge/vet-practice-economics.md) — covers client retention economics and the LTV framework.

## Provenance

Codifies the CAC:LTV discipline from veterinary practice management consulting; the ≥1:3 ratio target is consistent with general SaaS and service business benchmarking applied to veterinary contexts [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
