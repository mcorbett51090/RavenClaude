# Manufacturing Operations

The **manufacturing-operations** plugin — the discrete/process manufacturing operations craft: the **plan / make / control** loop on the factory floor that turns demand into a buildable plan, runs the line at the throughput it can sustain, and holds quality in statistical control — distinct from re-engineering the process, running the inferential statistics, sourcing the parts, or moving the finished goods.

## Agents

- **`production-planner`** — The plan: MRP/MPS, demand-vs-capacity planning, S&OP reconciliation, BOM management, lot sizing, and finite (constraint-respecting) scheduling. Plans to the bottleneck and material availability, not to infinite capacity.
- **`shop-floor-and-oee-analyst`** — The running line: OEE (availability × performance × quality) with defined denominators, throughput, takt vs cycle time, Theory-of-Constraints bottleneck analysis, and MES/shop-floor downtime data. Fixes the constraint, not a non-bottleneck.
- **`quality-and-capa-lead`** — Quality under control: SPC (special vs common cause), nonconformance (NCR) → containment → CAPA, inspection plans, FMEA, supplier quality, and control plans. Prevention over detection over scrap.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install manufacturing-operations@ravenclaude
```

## Seams

- **Redesigning the process (kaizen, DMAIC, value-stream map, SMED changeover reduction)** → `process-improvement`; this team runs the line as-is and finds the bottleneck, they re-engineer it.
- **The inferential statistics (Gage R&R / measurement-system analysis, the capability-study math, hypothesis tests, DOE)** → `applied-statistics`; we apply SPC and read Cpk, they own the rigor.
- **Sourcing the parts (supplier selection, the contract)** → `procurement-sourcing`; we set the incoming-quality and on-time bar, they source to it.
- **Moving the finished goods (distribution, route, fleet)** → `fleet-logistics`; we build them, they move them.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `process-improvement`, `applied-statistics`, `procurement-sourcing`, and `fleet-logistics`.
