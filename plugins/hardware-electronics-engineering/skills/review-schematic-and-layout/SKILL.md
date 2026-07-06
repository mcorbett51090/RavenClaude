---
name: review-schematic-and-layout
description: "Review a schematic and PCB layout before fab: correctness (ERC/DRC, footprints/pinouts/polarity, power), integrity (decoupling at the pin, grounding/return paths, stack-up, controlled impedance), and DFM/DFA/DFT against the target fab's rules — returning a prioritized findings list with fixes. Reach for this before sending to fab, or on an inherited design. Driven by pcb-design-engineer."
---

# Skill: Review Schematic & Layout

Most first-spin failures are caught by a disciplined pre-fab review. This skill runs
that review and returns a prioritized fix list. Driven by `pcb-design-engineer`.

## Step 1 — Correctness (first-spin killers)

- **ERC/DRC clean** — no unconnected/short nets, rule violations resolved.
- **Footprints / pinouts / polarity** — verified against the actual datasheet (pin 1,
  package, land pattern). This is the #1 most expensive first-spin killer.
- **Power** — every rail present, correct voltage, protection/sequencing per the power
  tree; no rail miswired.

## Step 2 — Integrity

- **Decoupling at the pin** — bypass caps close to power pins with a short return path,
  not scattered "near enough".
- **Grounding & return paths** — continuous reference plane under fast signals; no
  plane split under a fast net; a deliberate ground strategy.
- **Stack-up** — deliberate for the signal speeds and density; impedance control where
  needed (USB, RF, high-speed) with the fab's impedance profile.
- **Controlled impedance / length/skew** — applied where the interface requires it.

## Step 3 — DFM / DFA / DFT

- **DFM** — trace/space, drill, annular ring, soldermask, copper-to-edge within the
  **target fab's** current rule deck, with margin (not at the bleeding edge).
- **DFA** — courtyards, orientation consistency, thermal reliefs, fiducials,
  panelization for the assembler.
- **DFT** — test points on key rails/nets and debug/programming access.

## Step 4 — Prioritize the findings

1. **Blockers** — will not work or won't build: wrong footprint/polarity, miswired
   power, DRC/ERC violations, DFM rule breaks.
2. **Integrity risks** — decoupling/grounding/impedance/return-path issues that cause
   intermittent faults or EMC failures.
3. **Hardening** — DFA/DFT improvements, margin, second-source footprints.

## Step 5 — Output

A prioritized findings list: **each issue + the fix + why it matters + which first-spin
killer or integrity/DFM rule it maps to.** For bring-up after fab, sequence power rails
first and diagnose faults (short / wrong value / footprint / sequencing) incrementally.
Escalate any part-sourcing or architecture conflict to `hardware-systems-architect`.
