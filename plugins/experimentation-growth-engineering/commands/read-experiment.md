---
description: "Certify an experiment's trustworthiness (SRM, exposure, no-peeking, guardrails) and route the significance verdict to applied-statistics."
argument-hint: "[experiment + data]"
---

You are running `/experimentation-growth-engineering:read-experiment`. Use `experimentation-architect` + the `ab-test-plumbing` skill.

## Steps
1. Traverse the trust tree: SRM, exposure validity, pre-registration/no-peeking, guardrails.
2. If plumbing is broken, STOP — the result is invalid.
3. If trustworthy, package clean data and route the significance verdict to applied-statistics; the ship decision to product-management.
4. Emit (from `templates/experiment-readout.md`) + Structured Output block.
