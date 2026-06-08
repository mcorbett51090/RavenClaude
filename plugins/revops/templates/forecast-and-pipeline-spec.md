# Forecast & Pipeline — Spec

> Output of `pipeline-and-forecast-analyst` / the `forecast-methodology` skill. A forecast with no named method,
> stages with no exit criteria, coverage from a folk 3x, or no deal inspection is not ready to ship.

## 1. Deal inspection (before any aggregate)

| Flag | Count | $ amount | Action |
|---|---|---|---|
| Past close date | | | |
| Aged / stuck in stage | | | |
| No recent activity | | | |
| Amount doesn't reconcile | | | |

**Raw pipeline:** <$> → **Inspected (cleaned) pipeline:** <$>

## 2. Forecast methodology

- **Method chosen:** <weighted-by-stage / commit-category / AI-regression>
- **Why this method for this data:** <rationale>
- **Known bias:** <e.g. weighted over-counts early stage>
- **Weighted forecast:** <$>  |  **Commit forecast:** <$>  |  **Gap + why:** <...>
- **Call/roll-up cadence:** <...>

## 3. Stage exit criteria + historical probability

| Stage | Objective exit criterion (buyer action) | Historical stage→close % |
|---|---|---|
| | | |

_Use your own historical conversion, not the CRM defaults._

## 4. Coverage (derived, not a folk 3x)

- **Gap to target:** <$>
- **Stage-weighted win-rate (this segment):** <%>
- **Required coverage = gap ÷ win-rate:** <x>
- **Actual coverage on inspected pipeline:** <x>  →  **Gap:** <...>

## 5. Win-rate & sales velocity

- **Win-rate** (won ÷ won+lost), by segment/source: <...>
- **Sales velocity** = (open opps × win-rate × ACV) ÷ cycle length: <...>
- **Lever a proposed change moves:** <opps / win-rate / ACV / cycle>

## 6. Back-test

| Quarter | Forecast | Actual | Error | Bias direction |
|---|---|---|---|---|
| | | | | |

## 7. Build handoff

| What | Routed to |
|---|---|
| The warehouse revenue mart | `data-platform` |
| The forecast dashboard | `tableau` |
| "Is this win-rate difference significant" | `applied-statistics` |
| Funnel/stage definition fixes | `revops-architect` |

---

```
Status: ...
Files changed: ...
Revenue impact: ...
Definition integrity: ...
Handoff to system teams: ...
Open questions: ...
Grounding checks performed: ...
```
