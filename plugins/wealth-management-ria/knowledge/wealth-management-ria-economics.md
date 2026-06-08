# Wealth Management (RIA Practice) Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/riaops_calc.py`](../scripts/riaops_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. AUM growth decomposes into flows and market (§3 #1 #7)

```
aum_growth      = ending_aum - beginning_aum
market_growth   = aum_growth - net_new_flows
organic_growth  = net_new_flows / beginning_aum
```

A 15% AUM rise in a 15%-up market can be 0% organic — the practice rode the market, it didn't grow. Only the organic rate survives a drawdown (§3 #7).

## 2. Revenue is tiered, and the blended fee follows (§3 #3)

```
revenue     = sum(tier_aum * tier_fee for tier in schedule)
blended_fee = revenue / total_aum
```

Ad-hoc exceptions to the schedule both leak revenue and create disclosure/fairness problems — a consistently applied schedule is a revenue-integrity control (§3 #3).

## 3. Client value is margin, not AUM (§3 #2)

```
client_margin  = client_revenue - cost_to_serve
breakeven_aum  = cost_to_serve / effective_fee
```

A high-AUM, high-touch, discounted client can sit below a smaller efficient one. Rank by margin and act on the sub-breakeven tail (§3 #2).

## 4. Capacity is a leading retention indicator (§3 #4 #5)

```
households_per_advisor = households / advisors
```

Past a defensible band, service quality and review cadence slip, and the cost shows up later as attrition — and retention compounds on the base, so a lost household is lost forever (§3 #4 #5).
