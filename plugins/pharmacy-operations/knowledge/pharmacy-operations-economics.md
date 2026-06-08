# Pharmacy Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/pharmacy_operations_calc.py`](../scripts/pharmacy_operations_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Throughput and verification safety are both the job (§3 #1 #5)

```
tech_hours       = daily_scripts / scripts_per_tech_hour
pharmacist_hours = daily_scripts / verifications_per_pharmacist_hour
```

Staff to fill volume PLUS clinical-service time. Verification capacity is a hard constraint: a plan that pushes volume past what the pharmacist can safely verify is a patient-safety and liability failure, not an efficiency win — the verification/DUR judgment itself is always the pharmacist's.

## 2. The real margin is net of DIR (§3 #3)

```
real_margin = reimbursement - acquisition_cost - dir_fee     # per script
```

The sticker reimbursement overstates margin because DIR/clawback fees hit retroactively. A script that looks profitable at fill can go negative after DIR; read the real margin and flag the negative-margin classes.

## 3. Days-on-hand is cash and stockout risk (§3 #2 #6)

```
days_on_hand = inventory_value / daily_cogs
```

Every dollar of inventory is cash off the floor plus shrink/expiry risk; too little is a stockout and a lost script. Specialty, 340B, and refrigerated drugs carry distinct handling and reimbursement — a blanket DOH target across the book mis-manages all three.

## 4. Adherence is outcomes and revenue (§3 #4)

```
pdc = days_covered / days_in_measurement_period
```

PDC drives both clinical outcomes and the plan star ratings/value-based reimbursement tied to them. An adherence gap is a quality problem and a revenue problem at once; the highest-leverage focus is patients near a band threshold.
