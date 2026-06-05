# Detention Cost Is a Billable Asset, Not a Shipper Favor

**Status:** Pattern
**Domain:** Lane economics / carrier-shipper relationship
**Applies to:** `fleet-logistics`

---

## Why this exists

Detention — time a driver and truck wait at a shipper or receiver beyond the free time — is one of the most under-recovered costs in trucking. Industry surveys consistently find that carriers collect on fewer than half of qualifying detention events, and the average detention rate charged is below the actual cost of the idle truck and driver [unverified — training knowledge]. A truck waiting three hours beyond its two-hour free window is a truck that cannot earn revenue. At an average RPTD of $700/day, three hours of detention is $88 in lost earning capacity — plus the driver's waiting time. Accepting detention as a shipper relationship cost trains the shipper to continue the behavior.

## How to apply

Build a detention tracking and billing process:

```
Detention billing checklist (per load):
1. Record arrival time at shipper/receiver (timestamp from ELD or driver app).
2. Record door-open / loading-complete time.
3. Calculate: dwell time − free time (contract or standard 2 hours) = billable detention hours.
4. Apply the contracted or posted detention rate (minimum: $25–$75/hour to cover actual cost [unverified — training knowledge]).
5. Attach the ELD timestamp record to every detention invoice — it is the audit trail.
6. Invoice within 30 days; many shipper contracts have claim windows.

Recovery rate target: ≥ 80% of qualifying events invoiced, ≥ 70% collected.
```

Carrier-level detention analytics:
- Rank shippers/receivers by average dwell time and detention frequency.
- Shippers in the top quartile for dwell are candidates for a rate premium, a revised free-time clause, or a volume reduction.

**Do:**
- Automate detention logging via ELD data — manual logs are disputed; ELD timestamps are not.
- Include detention in the lane P&L: a lane with a low-margin rate but high detention frequency may be net-negative.
- Negotiate the free-time window and detention rate at contract signing, not when a claim arises.

**Don't:**
- Waive detention as a relationship gesture without a reciprocal commitment from the shipper — it signals that the carrier will absorb the cost indefinitely.
- Set detention rates below the true idle cost (driver pay + fixed truck cost per hour) — underpriced detention is not a discount, it's a loss.

## Edge cases / when the rule does NOT apply

Drop-and-hook operations where the carrier leaves the trailer and picks up an empty have no driver dwell — detention is a trailer-pool economics question, not a driver-time question. Dedicated contract carriers with guaranteed loads per day may have dwell built into their day rate; the billing mechanism differs but the cost is still tracked.

## See also

- [`../agents/dispatch-routing-specialist.md`](../agents/dispatch-routing-specialist.md) — owns the shipper ranking and dwell analysis.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the detention recovery rate and lane P&L integration.
- [`./revenue-per-truck-per-day-is-the-utilization-clock.md`](./revenue-per-truck-per-day-is-the-utilization-clock.md) — unrecovered detention is one of the dwell components that suppresses RPTD.

## Provenance

Synthesized from ATA and FMCSA detention research and carrier contracting practice; the under-recovery of detention is a documented industry problem cited in FMCSA detention studies (2014, 2020) and carrier advocacy materials.

---

_Last reviewed: 2026-06-05 by `claude`_
