# Fabric capacity & cost review — <CAPACITY / DATE>

> Owned by `fabric-admin`. See `knowledge/capacity-finops-and-throttling.md`.

## Current state
- **SKU:** F<n> (<CUs> CUs) · **Reservation:** <PAYG / 1-yr reserved>
- **Workspaces on this capacity:** <list>
- **Observed utilization (Capacity Metrics app):** peak <%>, sustained <%>, throttling events <count>

## Findings
| Symptom | Root cause (smoothing/bursting/throttling lens) | Severity |
|---|---|---|
| <slow interactive queries> | | |
| <throttling> | | |
| <runaway background job> | | |

## Recommendations
- [ ] **Rightsize:** <up / down / hold> to F<n> — rationale: <average + headroom>
- [ ] **Isolate:** move <noisy workload> to its own capacity (throttling is per-capacity)
- [ ] **Reserve:** <commit 1-yr / stay PAYG> — based on <steady vs spiky>
- [ ] **Per-experience optimization:** <stop idle Spark sessions; NEE on; pre-aggregate; query folding; right-size executors>
- [ ] **Surge protection / capacity limits:** <cap background consumption so interactive BI isn't starved>

## Projected impact
- **Cost change:** <$ / mo>; **performance change:** <expected>
