# embedded-iot-engineering

A **Embedded & IoT Engineering specialist team** for an embedded engineer, firmware lead, or hardware founder accountable for a fielded device that must meet a power, timing, and memory budget. It treats the power budget as the spec, holds real-time deadlines as hard constraints, budgets flash/RAM like money, favors determinism over throughput in control loops, and requires OTA + rollback before a device is fielded.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). MCU-explicit, application-flexible (bare-metal | RTOS | Linux-class edge; battery | mains | energy-harvesting).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `embedded-systems-lead`, `firmware-rtos-specialist`, `power-budget-analyst`, `connectivity-protocol-specialist` |
| **5 skills / commands** | `build-power-budget` · `verify-real-time` · `budget-memory` · `select-protocol` · `plan-ota` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · power-budget.md · memory-budget.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, device/telemetry PII) in generated deliverables |
| **`scripts/embedded_iot_calc.py`** | stdlib calculator — `power-budget` · `memory-budget` · `bom-cost` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install embedded-iot-engineering@ravenclaude
```

## Quickstart

> "Our device won't hit its battery-life target — where's the power going?"

The `embedded-systems-lead` scopes the problem, routes to `firmware-rtos-specialist` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a certification lab, an RF/EMC compliance authority, or a substitute for measuring on the real hardware. It does not issue FCC/CE/UL certifications, sign off on safety-critical compliance, or replace bench measurement. Certification and safety determinations route to the qualified lab/authority.
