# Embedded & IoT Engineering Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/embedded_iot_calc.py`](../scripts/embedded_iot_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. The power budget is the spec (§3 #1)

```
avg_current_mA = active_mA * active_fraction + sleep_mA * sleep_fraction
battery_life_h = battery_mAh / avg_current_mA           # derate for self-discharge/EOL
```

The sleep floor and wake frequency usually dominate — a chatty radio or a missed sleep state can swamp everything else. Build this first and let it constrain the part choices.

## 2. Deadlines are met on worst case (§3 #2)

```
schedulable = (sum of WCET/period over critical tasks) within the scheduling bound
deadline_met = (response_time_worst_case <= deadline)
```

Average-case timing tells you nothing about whether a deadline holds under the worst-case arrival pattern.

## 3. Memory is budgeted like money (§3 #3)

```
flash_used = image_size;            flash_headroom = (flash_avail - flash_used)/flash_avail
ram_used   = static + worst_stack + worst_heap
```

No headroom is over-budget — stack peaks and OTA dual-bank both need margin (§3 #5).

## 4. Connectivity is a per-unit cost too (§3 #6)

```
bom_unit       = sum(component_cost at volume_tier)
sell_price      = bom_unit / (1 - target_margin)
```

The radio module and its certification are part of the BOM; the protocol choice is a cost as well as a power/range trade.
