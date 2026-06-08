---
description: "Build a risk register, score likelihood x impact, choose a treatment per risk, and drive control selection from risk rather than from a framework checklist."
argument-hint: "[assets/data + known threats + existing controls + risk appetite]"
---

You are running `/cybersecurity-grc:build-risk-register`. Use `grc-architect` / `control-and-evidence-engineer` + the `risk-register-and-assessment` skill.

## Steps
1. Enumerate the assets worth protecting (data, systems, people) and the threats against each.
2. Score each risk with a consistent likelihood × impact scale (inherent risk first).
3. Choose a treatment per risk — mitigate / accept / transfer / avoid — and name the treating control for mitigations; record an owner + review date for every row.
4. Score residual risk after the treating control; flag any top risk with no control (the real exposure) and any control with no risk behind it (cost without benefit).
5. Feed the register into the Statement of Applicability and the control roadmap; hand control implementation + evidence to control-and-evidence-engineer.
6. Emit the scored risk register + the Structured Output block (with `Risk addressed:`, `Control state:`, and `Handoff to technical teams:`; mark recalled methodology specifics `[verify-at-build]`).
