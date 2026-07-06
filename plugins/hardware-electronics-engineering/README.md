# hardware-electronics-engineering plugin

> **The board** for the RavenClaude marketplace: the electronics hardware that
> embedded firmware runs on. It answers **"what is this board, from what parts,
> powered how, laid out how — and is it manufacturable and pre-compliant?"** — the
> hardware layer that `embedded-iot-engineering` (firmware/HAL/RTOS) and
> `robotics-autonomous-systems-engineering` (the robot) don't own. Engineering
> decision-support, **not** a certification or safety-sign-off authority.

**Designed for:** a hardware/electrical engineer (or a founder taking a product from
idea to board) who needs the build-vs-buy call right, a supply-aware BOM, a sound power
architecture, a clean schematic + PCB layout, and an EMC/pre-compliance mindset before
the first fab run.

## What this plugin gives you

- **The build-vs-buy call, decided on volume** — module/dev-board vs custom PCB against
  volume × cost × size × certification × time-to-market (with the wireless special case:
  reuse a pre-certified radio module's approval instead of your own).
- **A supply-aware BOM** — parts matched to requirements, datasheet parameters read at
  the operating point (worst-case + margin), and availability / second-source /
  lifecycle / cost scored as first-class selection criteria.
- **Sound power & integrity** — an explicit power tree (LDO vs switcher per rail),
  decoupling at the pin, deliberate grounding and return paths, and a stack-up chosen
  for the signal speeds.
- **Manufacturable, pre-compliant boards** — schematic + layout reviewed against the
  first-spin killers and the target fab's DFM rules, with EMC designed in (not tested
  in) and certification correctly scoped as a test-lab verdict.

## The two agents

| Agent | Owns |
|---|---|
| `hardware-systems-architect` | The shape: build-vs-buy, MCU/component selection + supply-aware BOM, power architecture, interfaces, and the EMC/pre-compliance posture. |
| `pcb-design-engineer` | The build: schematic capture, PCB layout (stack-up, decoupling, grounding, controlled impedance), signal/power integrity, DFM/DFA/DFT, and board bring-up. |

## The three skills

| Skill | What's inside |
|---|---|
| `scope-a-hardware-design` | Turn a product idea into an architecture: build-vs-buy, requirements-first, power tree, interfaces, pre-compliance posture. |
| `select-components-and-bom` | Select the MCU/components and build a supply-aware BOM, reading datasheets at the operating point. |
| `review-schematic-and-layout` | Pre-fab review: correctness (ERC/DRC, footprints, power), integrity (decoupling/grounding/impedance), and DFM/DFA/DFT. |

## When to use it

- You're taking a product from idea to board and need the build-vs-buy call and the
  architecture before you design anything.
- You need an MCU/parts selection and a BOM that won't die on availability or lifecycle.
- You have a schematic/layout and want it reviewed against the first-spin killers and
  the fab's DFM rules before you spend money on a fab run.

## When *not* to use it

- You need firmware / drivers / RTOS / the HAL on the MCU — that's
  `embedded-iot-engineering`. This plugin builds the board firmware runs on.
- You're building the full robot (actuation, motion, autonomy) — that's
  `robotics-autonomous-systems-engineering`.
- You need mechanical / enclosure / thermal-mechanical design — out of scope.
- You need a certification pass/fail — that's an accredited **test lab's** verdict; this
  plugin gives pre-compliance engineering judgment.

## Seams to neighbouring plugins

- **`embedded-iot-engineering`** — the firmware/HAL/RTOS on the board (the primary sibling).
- **`robotics-autonomous-systems-engineering`** — the full robot a board might sit in.
- **`performance-engineering`** — system-level constraints where they apply.
- **`ravenclaude-core`** — the domain-neutral constitution + protocols.
- **An accredited test lab** — the EMC/safety certification verdict (not this plugin).

## Requires

- `ravenclaude-core@>=0.7.0`.

See [`CLAUDE.md`](CLAUDE.md) for the team constitution and house opinions.
