---
name: select-protocol
description: "Select the radio on the power/range/bandwidth/cost trade — don't default to Wi-Fi. Reach for this on a connectivity question."
---

# Skill: Select connectivity protocol

Defaulting to Wi-Fi for low-rate long-range telemetry blows the power budget (§3 #6).

## Step 1 — State the need
Required data rate, range, topology, and the energy budget the app allows (§3 #6).

## Step 2 — Map to the regime
BLE / LoRa / Wi-Fi / cellular against that need — long-range-low-rate ≠ local-high-rate (§3 #6).

## Step 3 — Cost the airtime + BOM
TX airtime energy into the power budget; module/cert cost via `embedded_iot_calc.py bom-cost` (§3 #6).

## Step 4 — Confirm on real RF
Range/throughput claims carry a datasheet date and a real-environment caveat (§3 #7 #8).

## Output
A protocol selection on the power/range/bandwidth/cost trade with the airtime-energy and BOM implication. Traverse Tree 3 in the decision-trees file.
