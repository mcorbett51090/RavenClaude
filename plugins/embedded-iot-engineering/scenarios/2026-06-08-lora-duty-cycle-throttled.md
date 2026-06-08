---
scenario_id: 2026-06-08-lora-duty-cycle-throttled
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: lorawan
product_version: "unknown"
scope: likely-general
tags: [lora, lorawan, radio, duty-cycle, airtime, telemetry]
confidence: high
reviewed: false
---

## Problem

An agricultural soil-moisture fleet on LoRaWAN (EU868) was specced to report every sensor reading — temperature, moisture, battery, and a few diagnostics — once a minute. In the lab over a short link it worked. In the field, devices fell silent for long stretches, the gateway saw a fraction of the expected uplinks, and the team blamed range and antenna placement. Swapping antennas and adding gateways barely helped.

## Constraints context

- EU868 imposes a sub-band duty-cycle limit (commonly 1% on the default channels) — a hard regulatory cap on on-air time, not a tuning knob.
- The chosen spreading factor for the range needed was high (SF11/SF12), so each ~40-byte uplink had a long on-air time — well over a second.
- Once-a-minute reporting at that airtime blew straight through the 1% budget; the LoRaWAN stack was silently enforcing the duty cycle by deferring transmissions, which looked exactly like "dropped packets" from the gateway side.

## Attempts

- Tried: more gateways and better antennas. This was a range fix for a problem that wasn't range — the uplinks that did arrive were clean; the missing ones had never been allowed to transmit.
- Tried: dropping to a lower spreading factor to cut airtime. Helped a little but sacrificed the range the deployment actually needed, and still didn't fit a 60-second cadence within 1%.
- Tried: computing the on-air time per uplink against the duty-cycle budget first (the `airtime` estimate), then redesigning the payload + cadence to fit — pack the readings into a compact binary payload, batch several readings into one larger uplink, and stretch the cadence to every 15-20 minutes (plus an event-driven uplink on a threshold crossing). With airtime per message and messages per hour now inside the 1% headroom, the deferrals stopped. This was the fix.

## Resolution

Once the payload was compact and the cadence sat inside the duty-cycle budget with margin, the LoRaWAN stack stopped deferring transmissions and the gateway saw the expected uplinks. Reported coverage "improved" dramatically — but the real change was that the devices were now legally allowed to transmit when they tried. The team added an airtime-vs-duty-cycle check to every LoRaWAN spec before picking a reporting cadence.

## Lesson

On a duty-cycle-limited radio, the regulatory on-air budget — not range — often sets your real reporting cadence. Compute airtime per message (it grows fast with spreading factor) against the sub-band duty-cycle cap before promising a cadence; silent stack-enforced deferral looks identical to dropped packets. Pick the radio and the payload by the budget: pack the payload, batch readings, stretch the cadence, and reserve event-driven uplinks for what actually matters. Use the `airtime` subcommand of `scripts/embedded_calc.py` for the on-air-time + duty-cycle-headroom estimate.
