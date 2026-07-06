---
name: scope-a-hardware-design
description: "Turn a product idea into a hardware architecture: decide module/dev-board vs custom PCB (via the decision tree), name requirements before parts, sketch the power tree, the interface plan, and an EMC/pre-compliance posture — against a cost/power/size/volume/schedule budget. Reach for this at the START of any board project. Driven by hardware-systems-architect."
---

# Skill: Scope a Hardware Design

Build-vs-buy is the highest-leverage hardware decision. This skill produces the
architecture before any schematic. Driven by `hardware-systems-architect`.

## Step 1 — Name the requirements before any part

Function, compute/peripherals, power envelope & battery, size/enclosure, operating
environment (temp/humidity/vibration), interfaces/connectivity, volume, schedule, and
certification needs. The MCU and parts are conclusions of these — not the starting point.

## Step 2 — Decide module vs custom PCB

Traverse [`../../knowledge/module-vs-custom-pcb-decision-tree.md`](../../knowledge/module-vs-custom-pcb-decision-tree.md):
volume × cost × size × certification × time-to-market. Special-case **wireless** — a
pre-certified radio module reuses its FCC/CE approval; a discrete radio means your own
intentional-radiator certification. State the crossover conditions.

## Step 3 — Sketch the power tree

Rails and their loads; LDO vs switching regulator per rail (noise vs efficiency vs
size); a power budget; sequencing and protection; battery/thermal. Power decided here
is cheap; power found at bring-up is expensive.

## Step 4 — Interface & connectivity plan

Digital buses (I2C/SPI/UART/USB), analog front-end needs, and wireless (module vs
discrete, with the certification caveat). Name connectors and protection.

## Step 5 — EMC / pre-compliance posture

Identify the likely regulatory regime (FCC/CE, etc. — dated, `[verify-at-use]`) and the
design-for-EMC choices to bank now (grounding, filtering, clock management, shielding).
Note that certification is a **test-lab verdict**, not something asserted here.

## Step 6 — Output

An architecture brief: **build-vs-buy verdict + requirements + MCU/component direction +
power tree + interface plan + pre-compliance posture + the flip conditions.** Hand
component detail to [`select-components-and-bom`](../select-components-and-bom/SKILL.md),
then schematic + layout to `pcb-design-engineer`.
