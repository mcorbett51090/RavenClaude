# Proration & Plan-Change Test Matrix — <product>

> The money-path spec. Every mid-cycle change gets a row with the **expected** charge/credit, then a fixture/replay test that proves it. A proration bug is a revenue bug — this matrix is BLOCKING before go-live. Rules set by [`billing-systems-architect`](../agents/billing-systems-architect.md); implemented + tested by [`billing-implementation-engineer`](../agents/billing-implementation-engineer.md).

## Policy (fill in first)

- **Upgrade timing:** immediate | next cycle
- **Upgrade charge:** prorated invoice now | added to next invoice
- **Downgrade timing:** immediate | end of cycle
- **Downgrade credit:** proration credit | no credit (use through period end)
- **Seat add/remove:** prorated | next cycle
- **Trial-to-paid:** charge at trial end | immediate on conversion
- **Refund policy:** none | prorated | full within N days
- **Annual proration:** <how mid-term changes prorate on annual terms>

## Test matrix

| # | Scenario | Starting state | Change | Timing in cycle | Expected charge/credit | Expected entitlement | Test |
|---|---|---|---|---|---|---|---|
| 1 | Upgrade tier | Basic monthly | → Pro | Day 10 of 30 | Prorated Pro−Basic for 20 days now | Pro immediately | ☐ |
| 2 | Downgrade tier | Pro monthly | → Basic | Day 10 of 30 | Credit / no charge (use Pro to period end) | Basic at next cycle | ☐ |
| 3 | Add seats | 5 seats | → 8 seats | Day 15 of 30 | Prorated 3 seats × 15 days | 8 seats immediately | ☐ |
| 4 | Remove seats | 8 seats | → 5 seats | Day 15 of 30 | Credit per policy | 5 seats at next cycle | ☐ |
| 5 | Monthly → annual | Monthly | → Annual | Day 10 of 30 | Annual now, credit unused month | Same tier, annual term | ☐ |
| 6 | Trial → paid | Trialing | Convert | Trial end | First full charge | Paid entitlement | ☐ |
| 7 | Trial cancel | Trialing | Cancel | During trial | No charge | Downgraded/none | ☐ |
| 8 | Refund | Paid Pro | Refund | Day 5 of 30 | Per refund policy | Per policy | ☐ |
| 9 | Currency/coupon interaction | Discounted plan | Upgrade | Mid-cycle | Proration respects coupon rules | Upgraded | ☐ |
| 10 | Dunning downgrade | Past due | Grace expires | — | No new charge | Downgraded/suspended | ☐ |

## Delivery-robustness rows (idempotency)

| # | Scenario | Expected |
|---|---|---|
| D1 | Same webhook delivered twice | Second delivery is a no-op (no double charge/provision) |
| D2 | `updated` arrives before `created` | State reflects latest object version; stale event ignored |
| D3 | Provider call retried after timeout (same idempotency key) | Exactly one subscription/charge created |
| D4 | Reconciliation after a dropped webhook | Local state reconverges to provider; drift → 0 |

## Sign-off

- [ ] All policy rows have expected values agreed with the architect
- [ ] Every row has a passing fixture/replay test
- [ ] Delivery-robustness rows D1–D4 pass
