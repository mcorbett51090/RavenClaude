# Customer Support & CX Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/supportops_calc.py`](../scripts/supportops_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Deflection is recurring savings vs a recurring hire (§3 #1)

```
cost_avoided   = deflection_rate * volume * cost_per_contact
hire_cost       = fully_loaded_agent_cost   # recurring, added
```

A hire adds recurring cost forever; a deflected contact removes it forever. Model deflection first — the cheapest contact never reaches an agent (§3 #1).

## 2. Staffing is workload and occupancy, not a ratio (§3 #2)

```
workload_hours = contacts * AHT
agents         = workload_hours / (interval_hours * target_occupancy)
```

A fixed 'one agent per N tickets' ratio ignores handle time and occupancy and breaks the moment volume or AHT moves. Staff to the workload at a healthy occupancy band (§3 #2).

## 3. Backlog is a flow — arrivals vs capacity (§3 #5)

```
backlog_change = arrivals - resolution_capacity     # per day
days_to_clear  = current_backlog / max(resolution_capacity - arrivals, 0)
```

If arrivals exceed capacity the backlog grows without bound — no amount of 'work faster' closes it. Close the arrivals-vs-capacity gap (deflect, staff, or tier) (§3 #5).

## 4. FCR is the master metric (§3 #4)

```
repeat_cost   = (1 - FCR) * volume * cost_per_contact
```

A reopen is a second (or third) paid contact and an angrier customer. FCR lowers cost and lifts satisfaction at the same time — optimize it over raw speed-to-first-reply (§3 #4).
