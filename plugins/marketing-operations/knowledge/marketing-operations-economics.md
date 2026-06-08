# Marketing Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/marketingops_calc.py`](../scripts/marketingops_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. The funnel back-solves required volume (§3 #1)

```
required_leads = target_wins / (r_lead_mql * r_mql_sql * r_sql_opp * r_opp_win)
leaking_stage  = stage with the lowest conversion (or longest dwell)
```

If you need 50 wins and the product of stage rates is 0.5%, you need ~10,000 leads — but if one stage leaks, fixing that stage is cheaper than 10,000 more leads (§3 #1).

## 2. Spend is gated on unit economics, not lead count (§3 #3)

```
CAC          = fully_loaded_acquisition_cost / customers_acquired
LTV_CAC      = ltv / CAC
payback_mo   = CAC / monthly_gross_margin_per_customer
```

A channel producing cheap leads that never convert has a low cost-per-lead and a terrible CAC — the lead count flatters it while the economics condemn it (§3 #3 #4).

## 3. Channel ROI depends on the attribution model (§3 #2)

```
channel_roi = (pipeline_or_revenue_contribution - cost) / cost   # under a NAMED model
```

First-touch credits the channel that opened the relationship; last-touch credits the closer; multi-touch splits across the path. The same campaign can look like a winner or a loser depending only on the model — so state it (§3 #2).

## 4. Channels saturate — read marginal ROI (§3 #5)

```
marginal_roi = d(contribution) / d(spend)   # the next dollar, not the average
```

Average ROI stays high long after the marginal dollar has gone negative; budget decisions follow the marginal curve, and scaling past the efficient frontier quietly destroys blended CAC (§3 #5).
