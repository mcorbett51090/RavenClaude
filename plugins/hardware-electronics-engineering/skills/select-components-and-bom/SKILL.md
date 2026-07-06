---
name: select-components-and-bom
description: "Select the MCU/SoC and key components and build a supply-aware BOM: match parts to requirements, read datasheet parameters at the operating point (worst-case + margin), and weigh availability / second-source / lifecycle / cost at the target volume. Reach for this after the architecture is scoped, before schematic capture. Driven by hardware-systems-architect."
---

# Skill: Select Components & Build the BOM

A part is only as good as it is obtainable at the operating point. This skill selects
parts and builds a BOM that survives supply reality. Driven by
`hardware-systems-architect`.

## Step 1 — Match parts to requirements

For the MCU/SoC: peripherals, compute, memory, power modes, package, and **ecosystem**
(toolchain, libraries, community — hand firmware fit to `embedded-iot-engineering`).
For each key component, start from what the requirement demands, not from a familiar part.

## Step 2 — Read the datasheet at the operating point

A parameter is valid only at its stated voltage / temperature / load. Design to
**worst-case across the operating range with margin**, not to the headline "typical @
25°C". Note the conditions you're relying on.

## Step 3 — Score supply, not just spec

For every key part, check and record:

| Criterion | Why it's a selection criterion |
|---|---|
| **Availability / stock** | An unobtainable perfect part is a failed design. |
| **Lifecycle (active / NRND / EOL)** | An NRND/EOL part is a redesign scheduled for later. |
| **Second source** | A sole-sourced key part is a single point of failure. |
| **Lead time** | Long lead times gate your whole schedule. |
| **Cost at target volume** | Price at the real volume, not at qty 1. |

A part that fails supply is escalated back into the architecture, not forced through.

## Step 4 — Cost the BOM at volume

Roll up the BOM cost at the target production volume (not prototype qty). Flag the
cost drivers and any single part dominating the BOM.

## Step 5 — Output

A supply-aware BOM: **each key part with its operating-point-valid spec + availability /
second-source / lifecycle / lead-time / volume-cost**, the risk parts flagged, and the
datasheet conditions relied on. Datasheet/availability facts are dated + `[verify-at-use]`
(see [`../../knowledge/eda-fab-and-compliance-2026.md`](../../knowledge/eda-fab-and-compliance-2026.md)).
Feeds schematic capture by `pcb-design-engineer`.
