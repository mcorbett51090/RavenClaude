# Fabric workspace & capacity plan — <ORG / PROJECT>

> Owned by `fabric-architect` (+ `fabric-admin` for capacity/cost). Fill the blanks; delete guidance italics.

## 1. Domains (data-mesh grouping)
| Domain | Business owner | Workspaces | Delegated tenant settings |
|---|---|---|---|
| <e.g. Finance> | <name> | <list> | <which, if any> |

## 2. Workspaces (per medallion layer / function)
| Workspace | Purpose (bronze/silver/gold/serve/admin) | Domain | Capacity | Region |
|---|---|---|---|---|
| | | | | |

*One layer per workspace where governance earns it; gold-serving separate from raw ingest.*

## 3. Capacity
| Capacity | SKU | Workloads on it | Isolation rationale | Reservation posture |
|---|---|---|---|---|
| | F<n> | | <why isolated from X> | <PAYG / 1-yr reserved> |

- **Sizing method:** <POC on trial/PAYG SKU → Capacity Metrics app → extrapolate>
- **Isolation:** <which noisy workloads are separated so they can't throttle interactive BI>
- **Region / residency:** <region per capacity; Multi-Geo? data-residency constraints>

## 4. Movement posture
| Source | Into | Method (shortcut/mirror/auto-mirror/copy-job/pipeline/eventstream) | Why |
|---|---|---|---|
| | | | |

## 5. Open questions / decisions
- <decision needed + owner>
