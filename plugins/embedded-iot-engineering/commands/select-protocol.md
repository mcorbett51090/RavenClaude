---
description: "Select the radio on the power/range/bandwidth/cost trade — don't default to Wi-Fi. Reach for this on a connectivity question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Select connectivity protocol

You are running `/embedded-iot-engineering:select-protocol` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. State the need — Required data rate, range, topology, and the energy budget the app allows (§3 #6).
2. Map to the regime — BLE / LoRa / Wi-Fi / cellular against that need — long-range-low-rate ≠ local-high-rate (§3 #6).
3. Cost the airtime + BOM — TX airtime energy into the power budget; module/cert cost via `embedded_iot_calc.py bom-cost` (§3 #6).
4. Confirm on real RF — Range/throughput claims carry a datasheet date and a real-environment caveat (§3 #7 #8).

## Output
A protocol selection on the power/range/bandwidth/cost trade with the airtime-energy and BOM implication. Traverse Tree 3 in the decision-trees file. See [`../skills/select-protocol/SKILL.md`](../skills/select-protocol/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No device/telemetry PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
