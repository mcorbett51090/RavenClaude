---
description: "Threat-model a feature or system with STRIDE: DFD + trust boundaries, STRIDE per element, ranked threats, and a mitigation or routed acceptance for each."
argument-hint: "[feature/architecture + its data]"
---

You are running `/security-engineering:threat-model`. Use `threat-modeler` + the `threat-modeling-stride` skill.

## Steps
1. Draw the DFD and mark trust boundaries.
2. Walk STRIDE per element/flow.
3. Rank threats by likelihood×impact; cluster where sensitive data flows (loop data-governance-privacy).
4. Map each to mitigate/transfer/accept; route acceptances to security-reviewer.
5. Emit the threat model (from `templates/threat-model.md`) + Structured Output block.
