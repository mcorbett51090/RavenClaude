# Workbook Performance Audit — <workbook name>

> Fill-in report for the [`workbook-performance-audit`](../skills/workbook-performance-audit/SKILL.md)
> skill. Evidence-first: the Performance Recorder runs **before** any change. Date: <YYYY-MM-DD> ·
> Auditor: <name> · Target SLA: <e.g. ≤5s load, ≤2s interaction>

## 1. Scope & symptom

| Field | Value |
|---|---|
| Workbook / dashboard | <name + URL> |
| Slow action reproduced | <load / this filter / that parameter> |
| Observed time | <seconds> |
| Connection | <extract (Hyper) / live — freshness reason if live> |
| Data source | <published + certified? embedded?> |

## 2. Performance Recorder evidence (longest events first)

| Dominant event category | Total ms | Notable events |
|---|---|---|
| Executing Query (few / many) | | |
| Computing / Generating | | |
| Rendering (mark count: ___) | | |
| Connecting / Geocoding | | |

**Diagnosis (decision-tree leaf reached):** <e.g. Executing Query — many → query fragmentation>

## 3. Levers applied (one change → re-record)

| # | Change | Rule | Before (ms) | After (ms) |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

## 4. Structural checklist (cheap wins)

- [ ] Extract vs live carries a stated freshness reason
- [ ] Filters pushed to the lowest layer (source / extract / data-source)
- [ ] No high-cardinality "show all values" quick filters → relevant-values / wildcard
- [ ] Mark count bounded (no 100k+ crosstab on a summary dashboard)
- [ ] LOD / table-calc addressing explicit
- [ ] Dashboard sheets share source/grain so query fusion engages

## 5. Result & residue

- **Result:** <new load/interaction time vs SLA>
- **Upstream work (→ data-platform):** <source indexing / warehouse modeling>
- **Security filters (→ ravenclaude-core/security-reviewer):** <any RLS/user-filter touched>
