# Size capacity to smoothed average, not peak — let the 24-hour smoothing window do its job

**Status:** Pattern — sizing to average-plus-smoothing is the strong default; sizing for peak is the documented over-provisioning anti-pattern (house opinion #5).

**Domain:** Capacity / FinOps

**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric **smooths** consumed CUs over future time: interactive ops over 5–64 minutes, **background ops over 24 hours**. So a background job that momentarily consumes 6× the next-10-minute budget *does not throttle* — its cost spreads across 2,880 30-second timepoints. People who don't internalize smoothing make one of two mistakes: they **over-provision** (buy F128 for a workload an F64 handles once smoothing is accounted for), or they **load-test wrong** (run a 5-minute burst, see a spike, and panic-scale — when smoothing would have absorbed it over 24h). The right mental model: size for the **smoothed average**, validate over a **long** window, and use bursting (not a bigger SKU) for the short spikes.

## How to apply

Measure with the Capacity Metrics app over a long window, size to the smoothed average, and leave headroom for scale-down.

```text
1. Run a scoped POC on a trial / pay-as-you-go F SKU.
2. Measure CU in the Fabric Capacity Metrics app over DAYS, not minutes (smoothing hides short tests).
3. Size to the SMOOTHED 24-hour background % + interactive headroom — not the instantaneous peak.
4. Schedule heavy background jobs to RIDE the 24-h smoothing window (off-peak, spread out).
5. Reserve (1-year) when load is steady; pay-as-you-go / autoscale for spiky load.
```

- **Scale-down math:** to safely drop F128→F64, the smoothed usage on F128 should sit **<40%** (so it lands ~80% at F64). Use the metrics, not a guess.
- **Bursting handles spikes** — a small SKU temporarily uses more compute to finish a big job fast (warehouse burst 1×–32× on small SKUs, 1×–12× on F64+). Don't buy a bigger SKU to cover a burst smoothing already absorbs.
- **Buffer for peak:** when setting Azure quotas, allow a **25–50%** buffer for peak/throttling headroom.

**Do:**
- Validate sizing over days with the Capacity Metrics app; size to smoothed average.
- Schedule background jobs to exploit the 24-h smoothing window.
- Reserve for steady load; keep pay-as-you-go/autoscale for spiky load.

**Don't:**
- Size for instantaneous peak — smoothing means you're paying for capacity you don't need.
- Trust a 5-minute load test — short stress tests are exactly what smoothing hides.

## Edge cases / when the rule does NOT apply

- **Interactive-dominated capacity** (BI reports, short ops) smooths over only 5–64 min — less slack than background; size with less optimism.
- **Hard latency SLAs for executives** may justify a dedicated, deliberately over-headroomed capacity — that's isolation (see [`capacity-isolate-noisy-workloads.md`](./capacity-isolate-noisy-workloads.md)), not peak-sizing-by-default.
- **Memory/concurrency limits** are *not* smoothed — a model that doesn't fit the SKU's VertiPaq budget needs a bigger SKU regardless of average CU.

## See also

- [`capacity-isolate-noisy-workloads.md`](./capacity-isolate-noisy-workloads.md) — isolation + surge protection for the cases sizing alone can't solve
- [`directlake-stay-under-guardrails.md`](./directlake-stay-under-guardrails.md) — the memory guardrail that's a SKU decision, not a smoothing one
- [`../knowledge/capacity-finops-and-throttling.md`](../knowledge/capacity-finops-and-throttling.md) — bursting/smoothing/throttling + the FinOps playbook
- [`../agents/fabric-admin.md`](../agents/fabric-admin.md)

## Provenance

Codifies house opinion #5 from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Throttling policy](https://learn.microsoft.com/fabric/enterprise/throttling), [Plan capacity](https://learn.microsoft.com/fabric/enterprise/plan-capacity), [Capacity planning — manage growth & governance](https://learn.microsoft.com/fabric/enterprise/capacity-planning-manage-capacity-growth-governance) (the F128→F64 <40% scale-down math; 25–50% quota buffer) and [Evaluate and optimize capacity](https://learn.microsoft.com/fabric/enterprise/optimize-capacity) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
