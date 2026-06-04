---
name: ab-test-plumbing
description: "Build trustworthy A/B-test plumbing: deterministic sticky assignment, exposure logging (who actually saw the variant), Sample-Ratio-Mismatch checks before reading results, pre-registered metric/MDE/duration, and guardrail metrics — leaving significance to applied-statistics."
---

# A/B Test Plumbing

## Plumbing before result
- **Deterministic, sticky** assignment (hash-based per unit).
- Log **exposure** (who SAW the variant), not just assignment.
- **SRM check**: observed split != intended -> assignment is broken -> result invalid (no matter how significant).

## Pre-register (with applied-statistics)
Primary metric, **MDE**, duration, guardrails — set before start. No peeking-to-stop, no HARKing.

## Guardrails
A winning primary metric that tanks latency/errors/revenue is not a win.

## Hand off
Deliver clean exposure + metric data; **significance is applied-statistics'**.
