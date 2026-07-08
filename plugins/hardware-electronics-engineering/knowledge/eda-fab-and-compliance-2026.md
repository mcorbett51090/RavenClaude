# EDA, fab, assembly & compliance — dated 2026 map

> **Retrieval date: 2026-07-06.** Component specs/availability, fab & assembly DFM
> rules, EDA-tool capabilities, and regulatory thresholds are **volatile and
> vendor/jurisdiction-specific**. Treat every part number, DFM rule, and regulatory
> threshold here as `[verify-at-use]` — read the actual datasheet at the operating
> point and the target fab's current rule deck before committing. The **durable**
> content is the design method (power/decoupling/grounding/DFM discipline) and the
> compliance *mindset*; the specific numbers and rules are the perishable part.

## EDA tooling (durable roles; features dated)

| Tool class | Examples | Notes |
|---|---|---|
| **Open / free** | KiCad | Capable, free, strong community; the default for many products and all hobby/low-budget work. |
| **Professional** | Altium, and other commercial suites | Advanced high-speed/SI tooling, library/PLM integration; licensing cost. |
| **Web / integrated-fab** | Vendor-integrated design+fab flows | Fast prototyping; watch lock-in and export portability. |

Tool choice rarely gates a design; the **method** does. Keep outputs (schematic,
Gerbers, BOM, netlist) portable.

## Fab & assembly / DFM (durable discipline; exact rules dated)

Every fab publishes a **capability/DFM rule deck** — trace/space, minimum drill,
annular ring, soldermask sliver, copper-to-edge, controlled-impedance options. These
are `[verify-at-use]` per fab and per process class. Durable rules:

- **Design to the target fab's actual rules**, with margin — not to the absolute
  bleeding edge of what's possible (yield + cost suffer at the edge).
- **Stack-up is a deliberate choice.** Layer count and dielectric set impedance
  control and return paths. Ask the fab for their standard stack-ups and impedance
  calculators.
- **Design for assembly (DFA):** courtyards, component orientation/consistency,
  thermal reliefs, fiducials, panelization — an assembler's constraints, not just the
  fab's.
- **Design for test (DFT):** test points on key rails/nets and programming/debug
  access, planned before layout is locked.

## Power & integrity (durable rules)

- **Decoupling at the pin.** Bypass caps close to each power pin with a short return
  path; this is placement, not an afterthought.
- **Regulator choice per rail:** **LDO** for low-noise, low-drop, low-current rails;
  **switching** for efficiency at higher current — at the cost of noise/EMC and layout
  care. Budget power and thermals; plan sequencing and protection.
- **Return paths are real nets.** Keep a continuous reference plane under fast signals;
  a plane split under a fast net is an integrity + emissions problem.
- **Read datasheet parameters at the operating point** — voltage, temperature, load.
  "Typical @ 25°C" is not worst-case at your real conditions; design with margin.

## Compliance / pre-compliance (durable mindset; standards dated)

- **EMC is designed in, not tested in.** Grounding, filtering, clock/edge-rate
  management, and shielding decided at architecture time are cheap; a failed
  radiated-emissions scan after layout is expensive and can't be firmware-patched.
- **Likely regimes** (all `[verify-at-use]`, jurisdiction/product-specific): e.g. FCC
  Part 15 (US), CE/EMC + RED for radios (EU), and safety standards where applicable.
  Identify the applicable set early with a qualified resource.
- **Radio modules reuse certification.** A pre-certified module carries modular
  approval; a discrete radio means your own intentional-radiator certification.
- **Certification is a test-lab verdict.** This team gives pre-compliance *engineering
  judgment* and a design-for-EMC checklist; the pass/fail belongs to an accredited lab.
  Pre-scanning before the formal test de-risks it.

## The recurring first-spin killers (durable, read this)

1. **Wrong footprint / pinout / polarity** — verify pin 1, package, and land pattern
   against the actual datasheet.
2. **Inadequate decoupling / grounding** — the most common source of intermittent,
   hard-to-debug faults.
3. **A part that's unobtainable / NRND / long-lead** — a supply failure, not a design
   one, but just as fatal; second-source key parts.
4. **Power sequencing / thermal** — found expensively at bring-up if not architected.

## Seams

- Firmware / drivers / RTOS / HAL on the MCU → `embedded-iot-engineering`.
- The full robot / actuation / autonomy → `robotics-autonomous-systems-engineering`.
- Mechanical / enclosure / thermal-mechanical → out of scope (flag it).
- Certification pass/fail → an accredited test lab.
