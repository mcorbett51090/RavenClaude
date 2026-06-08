# Automotive Dealership Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/automotive_dealership_calc.py`](../scripts/automotive_dealership_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Absorption is the survival metric (§3 #5)

```
absorption = fixed_ops_gross / total_fixed_overhead
```

At/above 100% the store covers its overhead from service + parts before selling a single car, and variable ops becomes pure upside. Below 100%, the showroom must carry the gap — structural fragility (§3 #1).

## 2. Days-supply and floorplan are carrying-cost cash (§3 #2)

```
days_supply       = units_in_stock / daily_sales_rate
monthly_floorplan = units_in_stock * per_unit_daily_carry * 30
```

Every aging unit burns floorplan interest, holdback, and depreciation daily; price-to-turn aged units rather than hold for a gross that erodes faster than it accrues.

## 3. Total gross is front plus back (§3 #3)

```
total_gross      = (front_gross_per_unit + fi_back_per_unit) * units
total_gross_unit = total_gross / units
fi_pvr           = fi_back_per_unit
```

A thin front with a strong, compliant back can beat a fat front with no back; manage the combined number, not the front alone.

## 4. The funnel converts at each step (§3 #6)

```
sold = ups * writeup_rate * close_rate
```

A volume shortfall is usually a conversion problem at a specific step (lead handling, desking, or close), not a traffic problem — diagnose the step before buying leads.
