# Rate Strategy — Brief

> Output of `revenue-manager` / the `revenue-management-and-rate-strategy` skill. A rate strategy with no
> demand forecast, no net-ADR channel view, or no RevPAR/GOPPAR target is not ready to ship.

## 1. KPI baseline

| KPI | Current | Target | Notes |
|---|---|---|---|
| RevPAR (north-star) | | | RevPAR = ADR × Occupancy |
| ADR | | | |
| Occupancy | | | |
| GOPPAR (profit check) | | | read RevPAR against this |

## 2. Demand forecast (the spine)

- **By-date forecast drivers:** <seasonality / day-of-week / events / pickup pace>
- **Current pickup vs. forecast:** <ahead / on / soft, by date>
- **Forecast method owner:** <framed here; statistical method routed to `applied-statistics`>

## 3. Rate ladder

| Date / demand tier | BAR / rate | Fences (LOS / advance-purchase) | Discount-or-hold rule |
|---|---|---|---|
| Peak | | | hold rate |
| Shoulder | | | |
| Soft | | | discount only if RevPAR rises after give-back AND profitable on GOPPAR |

## 4. Channel mix (net ADR)

| Channel | Gross rate | Commission / cost | **Net ADR** | Share now → target |
|---|---|---|---|---|
| Direct | | | | |
| OTA (Booking/Expedia) | | ~15-25% `[verify]` | | |
| GDS / other | | | | |

_Compare on net ADR. Shift to direct where it nets more — without stranding demand the OTAs uniquely reach._

## 5. Overbooking / yield call

- **Date(s):** <high-demand dates considered>
- **Forecasted no-show / cancel rate:** <%>
- **Overbook to:** <rooms over capacity> — **yield upside:** <$>
- **Walk-cost + walk-protocol:** <routed to `hotel-operations-lead`; must exist before overbooking>
- **Limit:** <beyond which broken-guarantee risk isn't worth it>

## 6. Handoffs

| What | Routed to |
|---|---|
| The walk-protocol + labor schedule the forecast drives | `hotel-operations-lead` |
| The statistical forecast method (seasonality, intervals) | `applied-statistics` |
| The RevPAR / KPI dashboard pipeline | `data-platform` |
| The F&B / banquet revenue | `restaurant-operations` |

---

```
Status: ...
Files changed: ...
KPI impact: ...
Guest impact: ...
Handoff to neighbours: ...
Open questions: ...
Grounding checks performed: ...
```
