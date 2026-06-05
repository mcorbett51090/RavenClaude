# Buy a Fabric capacity reservation for predictable 24x7 workloads — PAYG for bursts

**Status:** Pattern
**Domain:** Fabric FinOps / capacity
**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric capacity has two billing models: Pay-As-You-Go (PAYG, billed per CU-second) and 1-year/3-year reservations (a fixed monthly cost for a committed CU count). PAYG is never the correct choice for a predictable, 24x7 production workload — a constantly-running F64 on PAYG costs roughly twice the reservation price over a year. However, reservations are wrong for burst-only jobs (weekend ETL, quarterly reporting) where the average utilization is far below the committed amount. The decision requires matching the utilization profile (predictable 24x7 vs bursty) to the billing model.

## How to apply

Utilization test:

| Workload profile | Recommended billing | Rationale |
|---|---|---|
| Production BI + always-on pipelines, > 70% CU utilization 24x7 | Reservation (1yr or 3yr) | Lower unit cost, predictable spend |
| Dev/test capacities, < 30% CU utilization on average | PAYG or pause/resume | Paying for idle reserved CUs is more expensive |
| Seasonal batch (quarterly close, annual reporting) | PAYG + scale up temporarily | The burst duration is too short to amortize a reservation |
| Mixed: always-on BI + weekly batch bursts | Reservation for the BI baseline + separate bursty PAYG capacity | Isolate burst to avoid depleting the reserved capacity |

**Do:**
- Calculate the break-even point: `PAYG monthly cost at average utilization > reservation monthly cost` → buy the reservation.
- Use the **Fabric Capacity Metrics app** to measure average and peak CU utilization over 30 days before committing to a reservation size.
- Size the reservation to the **average + smoothing buffer**, not the peak (house opinion #5 in CLAUDE.md).

**Don't:**
- Size a reservation to cover peak load — peak can be handled by Fabric's burst-and-smooth mechanism; sizing for peak wastes reservation spend.
- Buy a reservation on a dev or sandbox capacity — these are typically heavily paused or idle, making PAYG cheaper.
- Forget that reservation covers **purchased CU capacity**, not the overage billed when smoothed CUs exceed the reserved amount; overage is still billed at PAYG rates.

## Edge cases / when the rule does NOT apply

Pilot / proof-of-concept workloads with less than 90 days of data should use PAYG — the utilization profile is unknown and committing to a reservation too early leads to waste if the capacity size turns out to be wrong.

## See also

- [`../agents/fabric-admin.md`](../agents/fabric-admin.md) — owns FinOps and capacity sizing decisions
- [`./capacity-size-to-average-not-peak.md`](./capacity-size-to-average-not-peak.md) — the complementary sizing discipline that feeds this reservation decision

## Provenance

Codifies the Fabric FinOps reservation guidance from CLAUDE.md §8 knowledge bank (`capacity-finops-and-throttling.md`); Microsoft Learn Fabric capacity reservations pricing documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
