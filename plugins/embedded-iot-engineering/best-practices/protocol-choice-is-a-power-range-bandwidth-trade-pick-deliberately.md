# Protocol choice is a power/range/bandwidth trade — pick deliberately.

**Status:** Pattern. **Constitution:** §3 #6, §4.

## Use when
Any embedded & iot engineering deliverable where this question is in play — read, applied, and cited whole.

## The rule
BLE, LoRa(WAN), Wi-Fi, and cellular trade power, range, bandwidth, topology, and cost against each other; match the protocol to the data rate, range, and energy budget the application actually needs (low-rate long-range telemetry ≠ high-rate local streaming), don't default to Wi-Fi.

## Why it matters
This is house opinion §3 #6, distilled into a citable rule. Practitioners act on these deliverables, so a framing error here is not academic — it sends real operating decisions the wrong way. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Make every number in the deliverable carry a definition, a window, and a baseline (§3 #1).
- Cite a source + date for any external benchmark, or mark it `[unverified — training knowledge]` (§3 #8).
- When this rule and another both apply, route to [`embedded-systems-lead`](../agents/embedded-systems-lead.md) to sequence them — overlapping signals usually mean two drivers at once.
- Keep device/telemetry PII out of the deliverable; route professional/legal determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected metric movement.

## The anti-pattern this prevents
The §4 failure mode: acting as if "protocol choice is a power/range/bandwidth trade — pick deliberately." weren't true — the most common way an analysis quietly misleads the practitioner who acts on it. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #6 — the house opinion this rule encodes.
- [`../knowledge/embedded-iot-engineering-decision-trees.md`](../knowledge/embedded-iot-engineering-decision-trees.md) — the decision trees that route to it.
