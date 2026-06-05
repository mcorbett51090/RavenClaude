# Lease Expiration Schedule Is a Hold-Period Risk Map

**Status:** Absolute rule
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

A lease-expiration schedule is not just a property management calendar. In the context of an acquisition or asset plan, it is the primary hold-period risk instrument. A property where 40% of the GLA expires in year 3 of a 5-year hold has a fundamentally different risk profile than one with staggered expirations — but the two look identical on a going-in cap-rate basis. Failing to model the lease-expiration curve against the hold period means the IC memo is missing its most important downside scenario.

## How to apply

Every underwriting and asset plan must include a lease-expiration rollover schedule mapped to the projected hold:

```
Lease Rollover Schedule — [Property Name]
────────────────────────────────────────────
Hold period: Year 1 through Year [X] (projected exit: [date])

Year | Tenant | Suite | SF / GLA% | Lease expires | Option? | NER ($/sf) | Risk tier
─────|────────|-------|-----------|---------------|---------|------------|──────────
  1  |        |       |     %     |               | Y/N/[mo]|            | Low/Med/High
  2  |        |       |           |               |         |            |
 ...

Rollover exposure summary:
  Year 1–2 rollover (% of GLA):  ___  (low risk if ≤ 15%)
  Year 3–4 rollover (% of GLA):  ___  (manageable if market is strong)
  Year 5+ rollover (% of GLA):   ___  (after projected exit — exit price risk)

Key lease events in hold period:
  - [Tenant] option decision:  [date] — if exercised, NER at $___; if not, re-leasing risk
  - [Tenant] kick-out clause:  [date/condition]
  - Credit watch tenants:      [list]

Exit timing note:  If [X]% of GLA expires in [exit year ± 1], exit cap rate is impacted by re-leasing risk.
```

**Do:**
- Build the rollover schedule at acquisition underwriting, not post-close — the concentration risk is a pricing input, not just an asset-management note.
- Stress the scenario where the largest lease(s) do not renew; model the re-leasing cost (TI + LC + free rent) and the impact on exit-year NOI and cap rate.
- Flag any expiration where the tenant has a below-market lease (versus current market NER) — those tenants have economic incentive not to renew.

**Don't:**
- Report only the weighted-average remaining lease term (WALT) without the expiration schedule — WALT hides concentration; the schedule reveals it.
- Treat a lease option as equivalent to a lease term; options are the tenant's right, not the owner's certainty.
- Assume rent on rollover equals in-place rent — model re-leasing at current market NER, not at the expiring rate.

## Edge cases / when the rule does NOT apply

NNN single-tenant properties where the sole lease extends beyond the hold period have no rollover risk within the hold; the schedule still exists but the risk section notes "no expiration within projected hold."

## See also

- [`../agents/acquisitions-underwriter.md`](../agents/acquisitions-underwriter.md) — uses the rollover schedule to stress the hold-period NOI and exit cap rate.
- [`./net-effective-rent-is-the-real-number-not-face-rent.md`](./net-effective-rent-is-the-real-number-not-face-rent.md) — the companion rule on using NER rather than face rent in rollover scenarios.

## Provenance

Codifies a standard CRE underwriting discipline; rollover concentration is a primary hold-period risk category in institutional acquisition underwriting practice [unverified — training knowledge]. Consistent with CBRE/JLL/Cushman data conventions for lease-expiration disclosure in IC memos.

---

_Last reviewed: 2026-06-05 by `claude`_
