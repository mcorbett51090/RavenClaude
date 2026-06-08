# Hotel & Hospitality Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/hotel_hospitality_operations_calc.py`](../scripts/hotel_hospitality_operations_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. RevPAR is a product, not a single lever (§3 #1)

```
occupancy = rooms_sold / rooms_available
adr       = room_revenue / rooms_sold
revpar    = room_revenue / rooms_available   # = adr * occupancy
```

Cutting ADR to lift occupancy can raise or lower RevPAR depending on the demand curve; the right trade-off is whichever maximizes the product, not a preference for occupancy or rate.

## 2. Channel mix is net-rate management (§3 #2)

```
net_rate_ota    = gross_rate * (1 - ota_commission_pct)
net_rate_direct = gross_rate - direct_acquisition_cost
```

A booking at the same gross rate is worth more direct than through an OTA paying 15-20% commission [unverified — training knowledge]; manage the mix on net rate, and value direct/loyalty for the margin it keeps.

## 3. Labor flexes to occupancy (§3 #4)

```
labor_hours        = occupied_rooms * target_hours_per_occupied_room
labor_cost_per_occ = labor_cost / occupied_rooms
```

A fixed roster over-spends on low-occupancy nights and under-serves high ones; staffing to the pace forecast is the controllable cost lever.

## 4. GOPPAR beats RevPAR (§3 #5)

```
goppar     = gross_operating_profit / rooms_available
flow_through = delta_gop / delta_revenue
```

RevPAR can rise while GOPPAR falls if revenue was bought with commission or labor cost; the owner is paid out of GOPPAR, so flow-through is the test of a real win.
