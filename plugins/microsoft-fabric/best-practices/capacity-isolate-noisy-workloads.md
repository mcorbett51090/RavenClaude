# Isolate noisy workloads; use surge protection — one capacity for everything starves the interactive users

**Status:** Pattern — workload isolation plus surge protection is the strong default for any capacity mixing BI with background jobs; "one capacity for everything" is the documented anti-pattern (house opinion #5).

**Domain:** Capacity / FinOps / throttling

**Applies to:** `microsoft-fabric`

---

## Why this exists

Throttling is **per-capacity**: one overloaded capacity is throttled while others run normally. So when interactive BI (user-facing reports) shares a capacity with heavy background jobs (Spark, pipelines, AI, refreshes), a surge of background work can push the capacity into **background rejection** and **interactive delay/rejection** — and your executives' dashboards stall because a data-prep job ran long. Two levers fix this: **isolation** (put noisy workloads on a different capacity than interactive BI) and **surge protection** (let the capacity reject *new background* operations before it enters deep throttling, protecting interactive users). Critically, surge protection is **not a substitute for sizing or isolation** — to *fully* protect a critical solution, it must live on its own correctly-sized capacity.

## How to apply

Separate the noisy from the interactive, then tune surge protection on the shared capacity.

```text
Interactive BI (exec dashboards)  → its own capacity (or Mission Critical workspace tag).
Data prep / pipelines / AI jobs   → a separate capacity, OR surge-protected on the shared one.
```

- **Capacity-level surge protection:** set a **background-operations rejection threshold** (capacity starts rejecting *new* background ops when the smoothed 24-h background % hits it) and a **recovery threshold** (rejection stops when it drops below). Tune both from the Capacity Metrics app **Background rejection** / **Interactive rejection** / **Utilization** charts — e.g. if interactive rejection spikes when background hits 75%, set rejection between 60–75% and recovery between 40–60%.
- **Workspace-level surge protection:** cap a workspace's max CU spend (% over a rolling 24h); tag the executive-reporting workspace **Mission Critical** to exempt it; **Block** a runaway workspace.
- **Know the gotcha:** many "interactive-looking" ops (SQL queries, some UI actions) are billed as **background** and *will* be rejected when surge protection is active. Surge protection rejects in-flight reruns — it's a blunt instrument, hence "isolate critical workloads" remains the real protection.

**Do:**
- Put interactive BI on a capacity (or Mission-Critical workspace) separate from heavy background jobs.
- Enable surge protection where they must share; tune thresholds from the metrics charts, not by guess.
- Use capacity reservations + isolation together: dedicated capacity for the critical, shared+protected for the rest.

**Don't:**
- Run everything on one capacity and treat surge protection as the whole answer — it rejects background jobs (with broad impact) and doesn't guarantee interactive ops aren't delayed.
- Forget that SQL/UI ops can count as background and get rejected under surge protection.

## Edge cases / when the rule does NOT apply

- **Small, single-purpose capacity** with no interactive/background contention doesn't need isolation — there's nothing to isolate from.
- **Capacity overage (preview)** can absorb *rare* spikes without scaling — but it prevents throttling, doesn't add performance, and can admit large new jobs; set surge protection to 100% to stop new background jobs while overage is on.
- **OneLake activities** are unaffected by capacity-level surge protection — don't expect it to throttle storage I/O.

## See also

- [`capacity-size-to-average-not-peak.md`](./capacity-size-to-average-not-peak.md) — sizing is the prerequisite; surge protection doesn't replace it
- [`../knowledge/capacity-finops-and-throttling.md`](../knowledge/capacity-finops-and-throttling.md) — bursting/smoothing/throttling + isolation in the FinOps playbook
- [`../knowledge/fabric-decision-trees.md`](../knowledge/fabric-decision-trees.md) — the capacity-throttled response decision tree
- [`../agents/fabric-admin.md`](../agents/fabric-admin.md)

## Provenance

Codifies house opinion #5 from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Surge protection](https://learn.microsoft.com/fabric/enterprise/surge-protection) (rejection/recovery thresholds; threshold-tuning examples; Mission Critical / Blocked workspace states; "many interactive operations like SQL query are also considered background and might be rejected"; "critical workloads still require dedicated capacity"), [Evaluate and optimize capacity](https://learn.microsoft.com/fabric/enterprise/optimize-capacity) (optimize/scale-up/scale-out; surge protection is not a substitute for sizing), and [Capacity overage (preview)](https://learn.microsoft.com/fabric/enterprise/capacity-overage-overview) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
